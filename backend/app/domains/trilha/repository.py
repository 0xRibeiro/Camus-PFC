from fastcrud.exceptions.http_exceptions import NotFoundException
from sqlalchemy import select
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


# Filtra pelo grupo da trilha, seguindo os vínculos dos itens filhos.
def no_escopo(modelo, grupo_id):
    if modelo is Trilha:
        return Trilha.grupo_id == grupo_id

    campo, pai = CAMPOS[modelo]
    return getattr(modelo, campo).in_(select(pai.id).where(no_escopo(pai, grupo_id)))


# retorna uma função que filtra pelo grupo da trilha, seguindo os vínculos dos itens filhos.
def filtro_escopo(coluna):
    def aplicar(escopo):
        return no_escopo(coluna.class_, None if escopo == "global" else escopo)

    return aplicar


# verifica se o item da trilha existe e pertence ao grupo.
async def exigir_item_no_escopo(db: AsyncSession, modelo, item_id: int, grupo_id: int | None, apenas_quiz: bool = False) -> None:
    consulta = select(modelo.id).where(modelo.id == item_id, no_escopo(modelo, grupo_id))
    if apenas_quiz:
        consulta = consulta.where(Conteudo.tipo == ConteudoTipo.quiz)
    if await db.scalar(consulta) is None:
        raise NotFoundException("Item da trilha não encontrado")
