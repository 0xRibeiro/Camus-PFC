from enum import StrEnum

from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Especie(StrEnum):
    DOURADO = "Peixe Dourado"
    BETTA = "Peixe Betta"
    PALHACO = "Peixe Palhaço"
    ANJO = "Peixe Anjo"
    NEON = "Peixe Neon"

    # cadastros antigos, depois insiro eles dnv
    CHROMIS = "Donzela chromis verde"
    BANGGAI = "Cardinal banggai"
    ANTHIAS = "Anthias cauda de lira"
    BODIAO = "Bodião limpador"


class Peixe(Base):
    __tablename__ = "peixes"

    id: Mapped[int] = mapped_column(primary_key=True)

    nome: Mapped[str] = mapped_column(String(50))

    aquario_id: Mapped[int] = mapped_column(ForeignKey("aquarios.id", ondelete="CASCADE"), index=True)
    
    especie: Mapped[Especie] = mapped_column(SQLEnum(Especie, native_enum=False, create_constraint=True, name="especie_peixe"))