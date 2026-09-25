import enum
from datetime import datetime

from sqlalchemy import ForeignKey, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class AcaoAuditoria(enum.Enum):
    create = "create"
    update = "update"
    delete = "delete"


class LogAuditoria(Base):
    __tablename__ = "logs_auditoria"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    usuario_id: Mapped[int | None] = mapped_column(
        ForeignKey("usuarios.id", ondelete="SET NULL")
    )  # quem fez

    acao: Mapped[AcaoAuditoria] = mapped_column() # oque fez

    entidade: Mapped[str] = mapped_column(String(50)) # onde fez

    entidade_id: Mapped[int] = mapped_column() # qual id

    alteracoes: Mapped[dict] = mapped_column(JSONB) # diff

    criado_em: Mapped[datetime] = mapped_column(server_default=func.now()) # qunado fez
