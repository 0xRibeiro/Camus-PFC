import random

from app.domains.dispositivo.model import Dispositivo, EstadoDispositivo
from scripts.seed.config import AGORA, INICIO, PREFIXO_MAC, QTD_DISPOSITIVOS
from scripts.seed.util import inserir, momento_entre


# so pra dashboard
async def criar_dispositivos(db) -> int:
    dispositivos = []
    for _ in range(QTD_DISPOSITIVOS):
        criado_em = momento_entre(INICIO, AGORA, curva=0.8)
        dispositivos.append(
            {
                "mac": f"{PREFIXO_MAC}{random.getrandbits(32):08X}",
                "estado": EstadoDispositivo.offline,
                "criado_em": criado_em,
                "ultimo_contato": criado_em,
            }
        )
    await inserir(db, Dispositivo, dispositivos)
    return len(dispositivos)
