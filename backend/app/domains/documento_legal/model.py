import enum
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class TipoDocumentoLegal(enum.Enum):
    termos_de_uso = "termos_de_uso"
    politica_de_privacidade = "politica_de_privacidade"


# cada linha e uma versao, publicada n muda
class DocumentoLegal(Base):
    __tablename__ = "documentos_legais"
    __table_args__ = (UniqueConstraint("tipo", "versao"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    tipo: Mapped[TipoDocumentoLegal] = mapped_column(index=True)

    # conta por tipo
    versao: Mapped[int] = mapped_column(Integer)

    # json do tiptap
    conteudo: Mapped[dict] = mapped_column(JSONB)

    # null e rascunho
    publicado_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # usuario so leva soft delete
    criado_por: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id", ondelete="RESTRICT"), nullable=False
    )

    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class AceiteDocumentoLegal(Base):
    __tablename__ = "aceites_documentos_legais"
    __table_args__ = (UniqueConstraint("usuario_id", "documento_id"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    usuario_id: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id", ondelete="CASCADE"), index=True
    )

    # versao aceita n pode sumir
    documento_id: Mapped[int] = mapped_column(
        ForeignKey("documentos_legais.id", ondelete="RESTRICT")
    )

    aceito_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
