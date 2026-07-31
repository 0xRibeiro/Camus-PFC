from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Aquario(Base):
    __tablename__ = "aquarios"

    id: Mapped[int] = mapped_column(
        primary_key=True)

    nome: Mapped[str] = mapped_column(
        String(50))
    
    litros: Mapped[int | None] = mapped_column(nullable=True)

    

