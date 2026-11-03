from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.core.database import Base


class ConclusaoConteudo(Base):
    __tablename__ = "conclusoes_conteudos"
    __table_args__ = (UniqueConstraint("usuario_id", "conteudo_id"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    usuario_id: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id", ondelete="CASCADE"), index=True
    )

    conteudo_id: Mapped[int] = mapped_column()

    versao_conteudo: Mapped[int] = mapped_column()

    concluido_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class TentativaQuiz(Base):
    __tablename__ = "tentativas_quiz"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    usuario_id: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id", ondelete="CASCADE"), index=True
    )

    conteudo_id: Mapped[int] = mapped_column()

    versao_conteudo: Mapped[int] = mapped_column()

    respostas: Mapped[dict] = mapped_column(JSONB)

    acertos: Mapped[int] = mapped_column()

    total: Mapped[int] = mapped_column()

    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
