import enum

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.domains.usuario.avatares import AVATAR_PADRAO, COR_FUNDO_PADRAO
from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.sql import func

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

    # soft delete: fica null enquanto a conta ta normal. quando o usuario
    # pede a exclusao, marcamos a data aqui em vez de dar DELETE na linha.
    # o registro continua no banco (o trigger de auditoria pega como UPDATE)
    # mas os dados pessoais sao anonimizados pelo service
    deletado_em: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )


    avatar: Mapped[str] = mapped_column(
        String(50), nullable=False, default=AVATAR_PADRAO, server_default=AVATAR_PADRAO
    )
    cor_fundo: Mapped[str] = mapped_column(
        String(7), nullable=False, default=COR_FUNDO_PADRAO, server_default=COR_FUNDO_PADRAO
    )

    minhas_conquistas = relationship(
        "Conquista",
        secondary="associacao_conquista_usuario"
    )


    aceites_termos: Mapped[list["AceiteTermos"]] = relationship(
    "AceiteTermos",
    back_populates="usuario",
    cascade="all, delete-orphan"
    )


class AceiteTermos(Base):
    __tablename__ = "aceites_termos"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    usuario_id: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id", ondelete="CASCADE"),
        nullable=False
    )

    termos_versao: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    privacidade_versao: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    aceito_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    usuario: Mapped["Usuario"] = relationship(
        "Usuario",
        back_populates="aceites_termos"
    )