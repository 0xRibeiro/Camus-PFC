from typing import Any

from fastcrud import FastCRUD
from fastcrud.exceptions.http_exceptions import BadRequestException, NotFoundException
from pydantic import BaseModel
from sqlalchemy import Row, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.trilha.model import (
    Alternativa,
    Conteudo,
    ConteudoTipo,
    Modulo,
    Questao,
    Trilha,
)

CAMPOS = {
    Modulo: ("trilha_id", Trilha),
    Conteudo: ("modulo_id", Modulo),
    Questao: ("conteudo_id", Conteudo),
    Alternativa: ("questao_id", Questao),
}

#  esse aqui é responsavel por filtrar o escopo pra cada grupo.
def no_escopo(modelo, grupo_id):
    if modelo is Trilha:
        return Trilha.grupo_id == grupo_id

    campo, trilhas = CAMPOS[modelo]
    return getattr(modelo, campo).in_(select(trilhas.id).where(no_escopo(trilhas, grupo_id)))


# precisamos fazer toda essa crud nova da trilha para os donos de grupos terem acesso as operações
# de modificar as trilhas.
class TrilhaCRUD(FastCRUD):
    def __init__(self, modelo, privado=False):
        super().__init__(modelo, custom_filters={"escopo": lambda _: lambda grupo_id: no_escopo(modelo, grupo_id)})
        self.privado = privado

    def grupo_id(self, db):
        return db.info["grupo_id"] if self.privado else None

    async def get(self, db, **kwargs):
        return await super().get(db, id__escopo=self.grupo_id(db), **kwargs)

    async def get_multi(self, db, **kwargs):
        return await super().get_multi(db, id__escopo=self.grupo_id(db), **kwargs)

    async def create(self, db, object, **kwargs):
        if self.model in CAMPOS:
            campo, trilhas = CAMPOS[self.model]
            grupo_id = self.grupo_id(db)
            query = select(trilhas.id).where(
                trilhas.id == getattr(object, campo),
                no_escopo(trilhas, grupo_id),
            )
            if self.privado and trilhas is Conteudo:
                query = query.where(Conteudo.tipo == ConteudoTipo.quiz)
            if await db.scalar(query) is None:
                raise NotFoundException("Item trilhas não encontrado")

        if self.privado and self.model is Conteudo:
            if object.tipo == ConteudoTipo.video or object.video_url is not None:
                raise BadRequestException("Trilhas de grupo aceitam artigos e quizzes.")

        return await super().create(db, object, **kwargs)

    async def update(self, db, object, **kwargs):
        if self.privado and self.model is Conteudo and object.video_url is not None:
            raise BadRequestException("Trilhas de grupo não aceitam vídeos.")

        return await super().update(db, object, id__escopo=self.grupo_id(db), **kwargs)

    async def delete(self, db: AsyncSession, db_row: Row | None = None, allow_multiple: bool = False, commit: bool = True, filters: BaseModel | None = None, **kwargs: Any,) -> None:
        # O FastCRUD ignora os filtros quando recebe db_row. Usa o ID para manter o escopo.
        if db_row is not None:
            filters = None
            kwargs = {"id": db_row.id}

        await super().delete(db, allow_multiple=allow_multiple, commit=commit, filters=filters, id__escopo=self.grupo_id(db), **kwargs)