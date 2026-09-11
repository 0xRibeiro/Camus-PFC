from sqlalchemy import Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.domains.usuario import usuario


# inicialmente pensei nesses atributos para a conquista. a tabela
# intermediária determina qual usuário possui qual conquista.
class Conquista(Base):
	__tablename__ = "conquistas"

	id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

	titulo: Mapped[str] = mapped_column(String(100))

	descricao: Mapped[str | None] = mapped_column(Text)

	# guarda o link da imagem do achievement
	imagem_dir: Mapped[str] = mapped_column(Text)


# Tabela associativa para vincular usuário com conquista.
# feita no ambiente virtual github, conferir se funcionou
# no devenv assim que possivel.
class ConquistaAdquiria(Base):
	__tablename__ = 'conquista_adquirida'
    id = Column(Integer, primary_key=True, index=True)
    conquistaId = Column(Integer, ForeignKey('Item.id'))
    usuarioId = Column(Integer, ForeignKey('Usuario.id'))
	desbloqueada = Column(Boolean)


class ItemDetail(Base):
    __tablename__ = 'ItemDetail'
    id = Column(Integer, primary_key=True, index=True)
    itemId = Column(Integer, ForeignKey('Item.id'))
    detailId = Column(Integer, ForeignKey('Detail.id'))
    endDate = Column(Date)

class ConquistaAdquirida(Base):
	__tablename__= "conquista_adquirida"

	id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

	id_usuario[int] = mapped_column(fo)