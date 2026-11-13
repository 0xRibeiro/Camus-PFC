from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AvisoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    mensagem: str
    lido: bool
    criado_em: datetime