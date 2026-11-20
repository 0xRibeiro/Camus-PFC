from datetime import UTC, datetime

from influxdb_client import Point
from influxdb_client.client.flux_table import FluxRecord
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.influx import cliente_influx
from app.domains.aquario.model import AquarioMembro, PapelAquario
from app.domains.dispositivo.model import Dispositivo, ModuloIot


# flux aceita o horario direto, desde q seja utc com Z no final
def tempo_flux(tempo: datetime) -> str:
    return tempo.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


class DispositivoRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def buscar(self, id_dispositivo: int) -> Dispositivo | None:
        return await self.db.get(Dispositivo, id_dispositivo)

    async def buscar_por_mac(self, mac: str) -> Dispositivo | None:
        resultado = await self.db.execute(select(Dispositivo).where(Dispositivo.mac == mac))
        return resultado.scalar_one_or_none()

    async def buscar_do_aquario(self, id_aquario: int) -> Dispositivo | None:
        resultado = await self.db.execute(select(Dispositivo).where(Dispositivo.id_aquario == id_aquario))
        return resultado.scalar_one_or_none()

    # serve pra criar e pra atualizar
    async def salvar(self, dispositivo: Dispositivo) -> Dispositivo:
        self.db.add(dispositivo)
        await self.db.commit()
        await self.db.refresh(dispositivo)
        return dispositivo

    # sem commit, vai junto no salvar
    async def remover_operadores(self, id_aquario: int) -> int:
        resultado = await self.db.execute(delete(AquarioMembro).where(AquarioMembro.id_aquario == id_aquario)
        .where(AquarioMembro.papel == PapelAquario.operador).returning(AquarioMembro.id_usuario))
        return len(resultado.all())

    async def contar_operadores(self, id_aquario: int) -> int:
        resultado = await self.db.execute(select(func.count()).select_from(AquarioMembro)
        .where(AquarioMembro.id_aquario == id_aquario).where(AquarioMembro.papel == PapelAquario.operador))
        return resultado.scalar_one()

    async def buscar_modulo(self, serial: str) -> ModuloIot | None:
        resultado = await self.db.execute(select(ModuloIot).where(ModuloIot.serial == serial))
        return resultado.scalar_one_or_none()

    async def listar_modulos(self, id_dispositivo: int) -> list[ModuloIot]:
        resultado = await self.db.execute(select(ModuloIot).where(ModuloIot.id_dispositivo == id_dispositivo)
        .order_by(ModuloIot.tipo))
        return list(resultado.scalars().all())

    async def salvar_modulos(self, modulos: list[ModuloIot]) -> None:
        self.db.add_all(modulos)
        await self.db.commit()


# leituras ficam no influx, n no postgres
class LeituraRepository:
    async def gravar(self, pontos: list[Point]) -> None:
        async with cliente_influx() as cliente:
            await cliente.write_api().write(bucket=settings.influx_bucket, record=pontos)

    async def consultar(self, consulta: str) -> list[FluxRecord]:
        async with cliente_influx() as cliente:
            tabelas = await cliente.query_api().query(consulta)

        registros = []
        for tabela in tabelas:
            for registro in tabela.records:
                registros.append(registro)
        return registros

    # params so existe no influx cloud, mac vem do banco (hex) e a condicao das constantes do service.
    # cada resultado vem com o nome no yield:
    # pontos = media das validas por janela, vazia vira null. horario e o comeco da janela, o dia 14 fica no dia 14
    # erros = janelas q tiveram leitura fora da faixa
    # minimo, media e maximo = das validas no periodo todo
    # deslocamento empurra as janelas pra de 1 dia comecar na meia-noite daqui e n na de utc
    async def listar_do_dispositivo(self, mac: str, inicio: datetime, fim: datetime, janela_segundos: int,
        condicao_valida: str, deslocamento_segundos: int) -> list[FluxRecord]:
        return await self.consultar(f"""
            dados = from(bucket: "{settings.influx_bucket}")
              |> range(start: {tempo_flux(inicio)}, stop: {tempo_flux(fim)})
              |> filter(fn: (r) => r._measurement == "leitura" and r.dispositivo == "{mac}" and r._field == "valor")
              |> map(fn: (r) => ({{r with valido: {condicao_valida}}}))

            validos = dados |> filter(fn: (r) => r.valido, onEmpty: "keep")

            validos
              |> aggregateWindow(every: {janela_segundos}s, offset: {deslocamento_segundos}s, fn: mean, createEmpty: true, timeSrc: "_start")
              |> yield(name: "pontos")

            dados
              |> filter(fn: (r) => not r.valido)
              |> aggregateWindow(every: {janela_segundos}s, offset: {deslocamento_segundos}s, fn: count, createEmpty: false, timeSrc: "_start")
              |> yield(name: "erros")

            validos |> min() |> yield(name: "minimo")
            validos |> mean() |> yield(name: "media")
            validos |> max() |> yield(name: "maximo")
        """)

    # leitura mais recente do periodo sem media, pro valor grande do card
    async def ultimas_do_dispositivo(self, mac: str, inicio: datetime, fim: datetime) -> list[FluxRecord]:
        return await self.consultar(f"""
            from(bucket: "{settings.influx_bucket}")
              |> range(start: {tempo_flux(inicio)}, stop: {tempo_flux(fim)})
              |> filter(fn: (r) => r._measurement == "leitura" and r.dispositivo == "{mac}")
              |> last()
        """)
