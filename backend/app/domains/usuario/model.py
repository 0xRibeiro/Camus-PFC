from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True)

    username: Mapped[str] = mapped_column(
        String(50))
    
    email: Mapped[str | None] = mapped_column(
        String(100), unique=True, nullable=True)
    
    hashed_password: Mapped[str] = mapped_column(
        String(1024), nullable=False)

    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True)

