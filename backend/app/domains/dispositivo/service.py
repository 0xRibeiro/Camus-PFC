import secrets
from datetime import UTC, datetime

from fastcrud.exceptions.http_exceptions import DuplicateValueException, NotFoundException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.redis import redis_client
from app.domains.dispositivo.model import Dispositivo
from app.domains.dispositivo.repository import DispositivoRepository
from app.domains.dispositivo.schema import (
    RespostaDesvinculo,
    RespostaVinculo,
    StatusDispositivo,
    VincularDispositivo,
)
from app.domains.usuario.model import Usuario

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


async def vincular(db: AsyncSession, data: VincularDispositivo, usuario: Usuario) -> Dispositivo:
    chave = f"dispositivo:codigo:{data.codigo}"
    mac = await redis_client.get(chave)

    if mac is None:
        raise NotFoundException("Código inválido ou expirou")

    repo = DispositivoRepository(db)
    dispositivo = await repo.buscar_por_mac(mac)

    if dispositivo is None:
        raise NotFoundException("Dispositivo não encontrado")

    vinculo = await repo.buscar_vinculo(dispositivo.id, usuario.id)

    if vinculo is not None:
        raise DuplicateValueException("Você já está vinculado a esse dispositivo")

    await repo.adicionar_vinculo(dispositivo.id, usuario.id)

    # so apaga depois de vincular, se falhar o codigo continua valendo
    await redis_client.delete(chave)
    return dispositivo


async def desvincular_todos(db: AsyncSession, mac: str) -> RespostaDesvinculo:
    repo = DispositivoRepository(db)
    dispositivo = await repo.buscar_por_mac(mac)

    if dispositivo is None:
        return RespostaDesvinculo(removidos=0)

    removidos = await repo.remover_vinculos(dispositivo.id)
    return RespostaDesvinculo(removidos=removidos)
