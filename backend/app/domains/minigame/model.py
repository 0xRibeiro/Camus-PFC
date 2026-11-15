from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base

# jogo é texto igual o status da denuncia, minigame novo n precisa de migration de enum
JOGO_QUEM_E_ESSE_PEIXE = "quem_e_esse_peixe"


# cada pergunta sorteada é uma rodada, a resposta certa fica so no back
class RodadaMinigame(Base):
    __tablename__ = "rodadas_minigame"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id", ondelete="CASCADE"), index=True)

    jogo: Mapped[str] = mapped_column(String(30))

    resposta_taxon_id: Mapped[int] = mapped_column()

    resposta_nome_cientifico: Mapped[str] = mapped_column(String(200))

    # [{taxon_id, nome}] na msm ordem q o aluno viu
    opcoes: Mapped[list[dict]] = mapped_column(JSONB)

    foto_url: Mapped[str] = mapped_column(String(500))

    # null = ainda n respondeu
    acertou: Mapped[bool | None] = mapped_column(default=None)

    pontos: Mapped[int] = mapped_column(default=0)

    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    respondida_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
