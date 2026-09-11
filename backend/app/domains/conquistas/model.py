from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


# inicialmente pensei nesses atributos para a conquista. Usando a
# apenas a lógica de desbloquada ser true ou false, impede a implementação
# da barra de progresso na conquista. mas podemos incrementar isso depois
class Conquista(Base):
	__tablename__ = "conquistas"

	id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

	titulo: Mapped[str] = mapped_column(String(100))

	descricao: Mapped[str | None] = mapped_column(String(200))

	desbloquada: Mapped[bool] = mapped_column(default=False)
