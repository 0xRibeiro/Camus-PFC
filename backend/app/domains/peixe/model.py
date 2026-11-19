from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


# dados da especie sao copia do iNat no cadastro, assim n depende dele pra mostrar
class Peixe(Base):
    __tablename__ = "peixes"

    id: Mapped[int] = mapped_column(primary_key=True)

    aquario_id: Mapped[int] = mapped_column(ForeignKey("aquarios.id", ondelete="CASCADE"), index=True)

    taxon_id: Mapped[int]
    nome_popular: Mapped[str] = mapped_column(String(150))
    nome_cientifico: Mapped[str] = mapped_column(String(150))
    foto_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    foto_credito: Mapped[str | None] = mapped_column(String(300), nullable=True)

    quantidade: Mapped[int] = mapped_column(default=1)

    # nome do pet, so qnd tem 1
    apelido: Mapped[str | None] = mapped_column(String(50), nullable=True)
