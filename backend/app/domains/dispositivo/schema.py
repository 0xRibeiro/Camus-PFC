from pydantic import BaseModel

from app.domains.dispositivo.model import EstadoDispositivo


# payload do topico camus/dispositivos/<mac>/status
class StatusDispositivo(BaseModel):
    estado: EstadoDispositivo

    # o offline do testamento n manda versao
    firmware: str | None = None
