from app.core.database import async_session_maker
from app.core.mqtt import mqtt
from app.domains.dispositivo.schema import StatusDispositivo
from app.domains.dispositivo.service import registrar_status


# + pega o status de qualquer esp
@mqtt.subscribe("camus/dispositivos/+/status")
async def ao_status(status: StatusDispositivo, topic: str):
    # camus/dispositivos/<mac>/status
    mac = topic.split("/")[2]

    async with async_session_maker() as db:
        await registrar_status(db, mac, status)