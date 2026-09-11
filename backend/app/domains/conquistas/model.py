from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


# inicialmente pensei nesses atributos para a conquista. a tabela
# intermediária determina qual usuário possui qual conquista.
class Conquista(Base):
	__tablename__ = "conquistas"

	id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

	titulo: Mapped[str] = mapped_column(String(100))

	descricao: Mapped[str | None] = mapped_column(Text)

	# guarda o link da imagem do achievement
	imagem_dir: Mapped[str] = mapped_column(Text)