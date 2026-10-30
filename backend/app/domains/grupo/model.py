from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


## Os convites são unicos e terá apenas um dono/admin por grupo, mas um usuário pode
## criar vários grupos.
class Grupo(Base):
    __tablename__ = "grupos"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    nome: Mapped[str] = mapped_column(String(50), nullable=False)

    id_dono: Mapped[int] = mapped_column(ForeignKey("usuarios.id", ondelete="CASCADE"))
    

class Participacao(Base):
    __tablename__ = "participacoes"

    id_grupo: Mapped[int] = mapped_column(ForeignKey("grupos.id", ondelete="CASCADE"), primary_key=True)

    id_usuario: Mapped[int] = mapped_column(ForeignKey("usuarios.id", ondelete="CASCADE"), primary_key=True, index=True)
    