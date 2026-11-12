import enum
from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class EstadoDispositivo(enum.Enum):
    online = "online"
    offline = "offline"


# esp central, criado sozinho qnd chega o 1o status dele no mqtt
class Dispositivo(Base):
    __tablename__ = "dispositivos"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # mac sem ":", igual vem no topico
    mac: Mapped[str] = mapped_column(String(12), unique=True, index=True)

    estado: Mapped[EstadoDispositivo] = mapped_column(default=EstadoDispositivo.offline)

    # ultima versao q chegou, o offline n manda
    firmware: Mapped[str | None] = mapped_column(String(20))

    ultimo_contato: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
