from sqlalchemy import Column, ForeignKey, Integer, String, Table, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.domains.usuario import model


# inicialmente pensei nesses atributos para a conquista. a tabela
# intermediária determina qual usuário possui qual conquista.
class Conquista(Base):
	__tablename__ = "conquistas"

	id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

	titulo: Mapped[str] = mapped_column(String(100))

	descricao: Mapped[str | None] = mapped_column(Text)

	# guarda o link da imagem do achievement
	imagem_dir: Mapped[str] = mapped_column(Text)

	usuarios_que_possuem: Mapped[list["model.Usuario"]] = relationship(
		secondary="associacao_conquista_usuario",
		back_populates="minhas_conquistas"
	)


# Tabela many-to-many bi direcional para vincular usuário com conquista.
# se formos guardar outras informações futuramente, da pra transformer
# em um association object.
associacao_conquista_usuario = Table(
	"associacao_conquista_usuario",
	Base.metadata,
	Column("conquista_id", Integer, ForeignKey("conquistas.id"), primary_key=True),
	Column("usuario_id", Integer, ForeignKey("usuarios.id"), primary_key=True)
)