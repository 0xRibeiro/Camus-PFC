import enum

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ConteudoTipo(enum.Enum):
    video = "video"
    artigo = "artigo"
    quiz = "quiz"


class Trilha(Base):
    __tablename__ = "trilhas"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    titulo: Mapped[str] = mapped_column(String(100))

    descricao: Mapped[str | None] = mapped_column(Text)

    is_active: Mapped[bool] = mapped_column(default=False)


class Modulo(Base):
    __tablename__ = "modulos"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    trilha_id: Mapped[int] = mapped_column(ForeignKey("trilhas.id", ondelete="CASCADE"))

    titulo: Mapped[str] = mapped_column(String(50))

    ordem: Mapped[int] = mapped_column()


class Conteudo(Base):
    __tablename__ = "conteudos"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    modulo_id: Mapped[int] = mapped_column(ForeignKey("modulos.id", ondelete="CASCADE"))

    titulo: Mapped[str] = mapped_column(String(100))

    tipo: Mapped[ConteudoTipo] = mapped_column()

    ordem: Mapped[int] = mapped_column()

    video_url: Mapped[str | None] = mapped_column(String(500))

    artigo_texto: Mapped[str | None] = mapped_column(Text)


class Questao(Base):
    __tablename__ = "questoes"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    conteudo_id: Mapped[int] = mapped_column(
        ForeignKey("conteudos.id", ondelete="CASCADE")
    )

    ordem: Mapped[int] = mapped_column()

    enunciado: Mapped[str] = mapped_column(Text)


class Alternativa(Base):
    __tablename__ = "alternativas"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    questao_id: Mapped[int] = mapped_column(
        ForeignKey("questoes.id", ondelete="CASCADE")
    )

    texto: Mapped[str] = mapped_column(String(200))

    correta: Mapped[bool] = mapped_column(default=False)
