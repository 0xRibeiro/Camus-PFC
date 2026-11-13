import enum

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


# dono n e salvo em aquarios_membros, vem do id_dono
class PapelAquario(enum.Enum):
    dono = "dono"
    operador = "operador"
    leitor = "leitor"


class Aquario(Base):
    __tablename__ = "aquarios"

    id: Mapped[int] = mapped_column(primary_key=True)

    nome: Mapped[str] = mapped_column(String(50))

    litros: Mapped[int | None] = mapped_column(nullable=True)

    # ajustes para cada aquario ter um dono
    id_dono: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id", ondelete="CASCADE"), index=True)


class AquarioMembro(Base):
    __tablename__ = "aquarios_membros"

    id_aquario: Mapped[int] = mapped_column(ForeignKey("aquarios.id", ondelete="CASCADE"), primary_key=True)

    id_usuario: Mapped[int] = mapped_column(ForeignKey("usuarios.id", ondelete="CASCADE"), primary_key=True, index=True)

    papel: Mapped[PapelAquario]