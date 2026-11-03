import enum
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.core.database import Base


# de onde veio o xp, ofensiva minigame etc entram aqui dps
class OrigemLancamento(enum.Enum):
    conteudo = "conteudo"


# extrato do xp, cada ganho vira uma linha
class LancamentoPontos(Base):
    __tablename__ = "lancamentos_pontos"
    # no max 1 pagamento por versao da origem
    __table_args__ = (
        UniqueConstraint("usuario_id", "origem_tipo", "origem_id", "versao"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    usuario_id: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id", ondelete="CASCADE"), index=True
    )

    origem_tipo: Mapped[OrigemLancamento] = mapped_column()

    origem_id: Mapped[int] = mapped_column()  # sem FK pro xp n sumir se apagar a origem

    versao: Mapped[int] = mapped_column(default=1)

    pontos: Mapped[int] = mapped_column()

    # null e xp global, preenchido conta so no grupo
    grupo_id: Mapped[int | None] = mapped_column(
        ForeignKey("grupos.id", ondelete="CASCADE")
    )

    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
