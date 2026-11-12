from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.dispositivo.model import Dispositivo
from app.domains.dispositivo.repository import DispositivoRepository
from app.domains.dispositivo.schema import StatusDispositivo


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
