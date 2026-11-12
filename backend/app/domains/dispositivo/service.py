import secrets
from datetime import UTC, datetime

from fastcrud.exceptions.http_exceptions import NotFoundException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.redis import redis_client
from app.domains.dispositivo.model import Dispositivo
from app.domains.dispositivo.repository import DispositivoRepository
from app.domains.dispositivo.schema import (
    RespostaDesvinculo,
    RespostaVinculo,
    StatusDispositivo,
)

CODIGO_VALIDADE_SEGUNDOS = 300


# mac novo vira dispositivo, mac conhecido so atualiza
async def registrar_status(db: AsyncSession, mac: str, status: StatusDispositivo) -> Dispositivo:
    repo = DispositivoRepository(db)
    dispositivo = await repo.buscar_por_mac(mac)

    if dispositivo is None:
        dispositivo = Dispositivo(mac=mac)

    dispositivo.estado = status.estado
    dispositivo.ultimo_contato = datetime.now(UTC)

    # offline n manda versao, mantem a ultima
    if status.firmware is not None:
        dispositivo.firmware = status.firmware

    return await repo.salvar(dispositivo)


async def gerar_codigo(mac: str) -> RespostaVinculo:
    while True:
        codigo = f"{secrets.randbelow(1_000_000):06d}"

        # nx: so grava se o codigo n estiver em uso
        gravou = await redis_client.set(f"dispositivo:codigo:{codigo}", mac, ex=CODIGO_VALIDADE_SEGUNDOS, nx=True)
        if gravou:
            return RespostaVinculo(codigo=codigo, expira_em=CODIGO_VALIDADE_SEGUNDOS)


# usado pelo aquario pra conectar e pra entrar com codigo
async def buscar_por_codigo(db: AsyncSession, codigo: str) -> Dispositivo:
    mac = await redis_client.get(f"dispositivo:codigo:{codigo}")

    if mac is None:
        raise NotFoundException("Código inválido ou expirou")

    dispositivo = await DispositivoRepository(db).buscar_por_mac(mac)

    if dispositivo is None:
        raise NotFoundException("Dispositivo não encontrado")

    return dispositivo


async def apagar_codigo(codigo: str) -> None:
    await redis_client.delete(f"dispositivo:codigo:{codigo}")


# tira o esp do aquario e os operadores saem junto
async def tirar_do_aquario(db: AsyncSession, dispositivo: Dispositivo) -> int:
    if dispositivo.id_aquario is None:
        return 0

    repo = DispositivoRepository(db)
    removidos = await repo.remover_operadores(dispositivo.id_aquario)
    dispositivo.id_aquario = None
    await repo.salvar(dispositivo)
    return removidos


async def desvincular_todos(db: AsyncSession, mac: str) -> RespostaDesvinculo:
    dispositivo = await DispositivoRepository(db).buscar_por_mac(mac)

    if dispositivo is None:
        return RespostaDesvinculo(removidos=0)

    removidos = await tirar_do_aquario(db, dispositivo)
    return RespostaDesvinculo(removidos=removidos)
