import enum
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.domains.usuario.avatares import AVATAR_PADRAO, COR_FUNDO_PADRAO

# so pro tipo
if TYPE_CHECKING:
    from app.domains.documento_legal.model import AceiteDocumentoLegal


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
        String(9), nullable=False, default=COR_FUNDO_PADRAO, server_default=COR_FUNDO_PADRAO
    )

    minhas_conquistas = relationship(
        "Conquista",
        secondary="associacao_conquista_usuario"
    )


    aceites_documentos: Mapped[list["AceiteDocumentoLegal"]] = relationship(
        "AceiteDocumentoLegal",
        cascade="all, delete-orphan",
    )


# fora da tabela usuarios de proposito: la tem trigger de auditoria e cada login
# viraria um log com o usuario inteiro. aqui atualiza a vontade
class AcessoUsuario(Base):
    __tablename__ = "acessos_usuarios"

    usuario_id: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id", ondelete="CASCADE"), primary_key=True
    )

    ultimo_acesso_em: Mapped[datetime] = mapped_column(DateTime(timezone=True))