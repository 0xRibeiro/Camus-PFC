import enum

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.domains.conquistas import model


class RoleUsuario(enum.Enum):
    aluno = "aluno"
    author = "author"
    admin = "admin"


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    username: Mapped[str] = mapped_column(String(50), unique=True)

    email: Mapped[str] = mapped_column(String(100), unique=True)

    hashed_password: Mapped[str] = mapped_column(String(1024), nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    role: Mapped[RoleUsuario] = mapped_column(default=RoleUsuario.aluno)  # default aluno se n definir

    conquistas_adquiridas: Mapped[list["model.Conquista"]] =relationship(
            secondary="conquista_adquirida",
            back_populates="usuarios_que_possuem",
    )