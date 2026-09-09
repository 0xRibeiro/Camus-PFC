from fastapi_pagination import Page
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NaoEncontradoError
from app.domains.trilha.model import Alternativa, Conteudo, Modulo, Questao, Trilha
from app.domains.trilha.repository import (
    AlternativaRepository,
    ConteudoRepository,
    ModuloRepository,
    QuestaoRepository,
    TrilhaRepository,
)
from app.domains.trilha.schema import (
    AlternativaCreate,
    AlternativaUpdate,
    ConteudoCreate,
    ConteudoUpdate,
    ModuloCreate,
    ModuloUpdate,
    QuestaoCreate,
    QuestaoUpdate,
    TrilhaCreate,
    TrilhaUpdate,
)

# trilhas


async def listar_trilhas(db: AsyncSession) -> Page[Trilha]:
    return await TrilhaRepository(db).listar()


async def criar_trilha(db: AsyncSession, data: TrilhaCreate) -> Trilha:
    return await TrilhaRepository(db).criar(**data.model_dump())


async def buscar_trilha(db: AsyncSession, trilha_id: int) -> Trilha:
    trilha = await TrilhaRepository(db).buscar(trilha_id)
    if trilha is None:
        raise NaoEncontradoError("trilha não encontrada")
    return trilha


async def atualizar_trilha(
    db: AsyncSession, trilha_id: int, data: TrilhaUpdate
) -> Trilha:
    trilha = await buscar_trilha(db, trilha_id)
    return await TrilhaRepository(db).atualizar(
        trilha, data.model_dump(exclude_unset=True)
    )


async def deletar_trilha(db: AsyncSession, trilha_id: int) -> None:
    trilha = await buscar_trilha(db, trilha_id)
    await TrilhaRepository(db).deletar(trilha)


# modulos


async def criar_modulo(db: AsyncSession, trilha_id: int, data: ModuloCreate) -> Modulo:
    await buscar_trilha(db, trilha_id)
    repo = ModuloRepository(db)
    ordem = len(await repo.listar_por_trilha(trilha_id))
    return await repo.criar(trilha_id=trilha_id, ordem=ordem, **data.model_dump())


async def listar_modulos(db: AsyncSession, trilha_id: int) -> list[Modulo]:
    await buscar_trilha(db, trilha_id)
    return await ModuloRepository(db).listar_por_trilha(trilha_id)


async def buscar_modulo(db: AsyncSession, modulo_id: int) -> Modulo:
    modulo = await ModuloRepository(db).buscar(modulo_id)
    if modulo is None:
        raise NaoEncontradoError("modulo não encontrado")
    return modulo


async def atualizar_modulo(
    db: AsyncSession, modulo_id: int, data: ModuloUpdate
) -> Modulo:
    modulo = await buscar_modulo(db, modulo_id)
    return await ModuloRepository(db).atualizar(
        modulo, data.model_dump(exclude_unset=True)
    )


async def deletar_modulo(db: AsyncSession, modulo_id: int) -> None:
    modulo = await buscar_modulo(db, modulo_id)
    await ModuloRepository(db).deletar(modulo)


# conteudos


async def criar_conteudo(
    db: AsyncSession, modulo_id: int, data: ConteudoCreate
) -> Conteudo:
    await buscar_modulo(db, modulo_id)
    repo = ConteudoRepository(db)
    ordem = len(await repo.listar_por_modulo(modulo_id))
    return await repo.criar(modulo_id=modulo_id, ordem=ordem, **data.model_dump())


async def listar_conteudos(db: AsyncSession, modulo_id: int) -> list[Conteudo]:
    await buscar_modulo(db, modulo_id)
    return await ConteudoRepository(db).listar_por_modulo(modulo_id)


async def buscar_conteudo(db: AsyncSession, conteudo_id: int) -> Conteudo:
    conteudo = await ConteudoRepository(db).buscar(conteudo_id)
    if conteudo is None:
        raise NaoEncontradoError("conteudo não encontrado")
    return conteudo


async def atualizar_conteudo(
    db: AsyncSession, conteudo_id: int, data: ConteudoUpdate
) -> Conteudo:
    conteudo = await buscar_conteudo(db, conteudo_id)
    return await ConteudoRepository(db).atualizar(
        conteudo, data.model_dump(exclude_unset=True)
    )


async def deletar_conteudo(db: AsyncSession, conteudo_id: int) -> None:
    conteudo = await buscar_conteudo(db, conteudo_id)
    await ConteudoRepository(db).deletar(conteudo)


# questoes


async def criar_questao(
    db: AsyncSession, conteudo_id: int, data: QuestaoCreate
) -> Questao:
    await buscar_conteudo(db, conteudo_id)
    repo = QuestaoRepository(db)
    ordem = len(await repo.listar_por_conteudo(conteudo_id))
    return await repo.criar(conteudo_id=conteudo_id, ordem=ordem, **data.model_dump())


async def listar_questoes(db: AsyncSession, conteudo_id: int) -> list[Questao]:
    await buscar_conteudo(db, conteudo_id)
    return await QuestaoRepository(db).listar_por_conteudo(conteudo_id)


async def buscar_questao(db: AsyncSession, questao_id: int) -> Questao:
    questao = await QuestaoRepository(db).buscar(questao_id)
    if questao is None:
        raise NaoEncontradoError("questao não encontrada")
    return questao


async def atualizar_questao(
    db: AsyncSession, questao_id: int, data: QuestaoUpdate
) -> Questao:
    questao = await buscar_questao(db, questao_id)
    return await QuestaoRepository(db).atualizar(
        questao, data.model_dump(exclude_unset=True)
    )


async def deletar_questao(db: AsyncSession, questao_id: int) -> None:
    questao = await buscar_questao(db, questao_id)
    await QuestaoRepository(db).deletar(questao)


# alternativas


async def criar_alternativa(
    db: AsyncSession, questao_id: int, data: AlternativaCreate
) -> Alternativa:
    await buscar_questao(db, questao_id)
    return await AlternativaRepository(db).criar(
        questao_id=questao_id, **data.model_dump()
    )


async def listar_alternativas(db: AsyncSession, questao_id: int) -> list[Alternativa]:
    await buscar_questao(db, questao_id)
    return await AlternativaRepository(db).listar_por_questao(questao_id)


async def buscar_alternativa(db: AsyncSession, alternativa_id: int) -> Alternativa:
    alternativa = await AlternativaRepository(db).buscar(alternativa_id)
    if alternativa is None:
        raise NaoEncontradoError("alternativa não encontrada")
    return alternativa


async def atualizar_alternativa(
    db: AsyncSession, alternativa_id: int, data: AlternativaUpdate
) -> Alternativa:
    alternativa = await buscar_alternativa(db, alternativa_id)
    return await AlternativaRepository(db).atualizar(
        alternativa, data.model_dump(exclude_unset=True)
    )


async def deletar_alternativa(db: AsyncSession, alternativa_id: int) -> None:
    alternativa = await buscar_alternativa(db, alternativa_id)
    await AlternativaRepository(db).deletar(alternativa)
