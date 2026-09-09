from fastapi import APIRouter, Depends, status
from fastapi_pagination import Page
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.domains.trilha import service
from app.domains.trilha.model import Alternativa, Conteudo, Modulo, Questao, Trilha
from app.domains.trilha.schema import (
    AlternativaCreate,
    AlternativaRead,
    AlternativaUpdate,
    ConteudoCreate,
    ConteudoRead,
    ConteudoUpdate,
    ModuloCreate,
    ModuloRead,
    ModuloUpdate,
    QuestaoCreate,
    QuestaoRead,
    QuestaoUpdate,
    TrilhaCreate,
    TrilhaRead,
    TrilhaUpdate,
)

router = APIRouter()


### trilhas


@router.post(
    "/trilhas",
    response_model=TrilhaRead,
    status_code=status.HTTP_201_CREATED,
    tags=["trilhas"],
)
async def criar_trilha(
    data: TrilhaCreate, db: AsyncSession = Depends(get_async_session)
) -> Trilha:
    return await service.criar_trilha(db, data)


@router.get("/trilhas", response_model=Page[TrilhaRead], tags=["trilhas"])
async def listar_trilhas(db: AsyncSession = Depends(get_async_session)) -> Page[Trilha]:
    return await service.listar_trilhas(db)


@router.get("/trilhas/{trilha_id}", response_model=TrilhaRead, tags=["trilhas"])
async def obter_trilha(
    trilha_id: int, db: AsyncSession = Depends(get_async_session)
) -> Trilha:
    return await service.buscar_trilha(db, trilha_id)


@router.patch("/trilhas/{trilha_id}", response_model=TrilhaRead, tags=["trilhas"])
async def atualizar_trilha(
    trilha_id: int, data: TrilhaUpdate, db: AsyncSession = Depends(get_async_session)
) -> Trilha:
    return await service.atualizar_trilha(db, trilha_id, data)


@router.delete(
    "/trilhas/{trilha_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["trilhas"]
)
async def deletar_trilha(
    trilha_id: int, db: AsyncSession = Depends(get_async_session)
) -> None:
    await service.deletar_trilha(db, trilha_id)


### modulos


@router.post(
    "/trilhas/{trilha_id}/modulos",
    response_model=ModuloRead,
    status_code=status.HTTP_201_CREATED,
    tags=["modulos"],
)
async def criar_modulo(
    trilha_id: int, data: ModuloCreate, db: AsyncSession = Depends(get_async_session)
) -> Modulo:
    return await service.criar_modulo(db, trilha_id, data)


@router.get(
    "/trilhas/{trilha_id}/modulos", response_model=list[ModuloRead], tags=["modulos"]
)
async def listar_modulos(
    trilha_id: int, db: AsyncSession = Depends(get_async_session)
) -> list[Modulo]:
    return await service.listar_modulos(db, trilha_id)


@router.get("/modulos/{modulo_id}", response_model=ModuloRead, tags=["modulos"])
async def obter_modulo(
    modulo_id: int, db: AsyncSession = Depends(get_async_session)
) -> Modulo:
    return await service.buscar_modulo(db, modulo_id)


@router.patch("/modulos/{modulo_id}", response_model=ModuloRead, tags=["modulos"])
async def atualizar_modulo(
    modulo_id: int, data: ModuloUpdate, db: AsyncSession = Depends(get_async_session)
) -> Modulo:
    return await service.atualizar_modulo(db, modulo_id, data)


@router.delete(
    "/modulos/{modulo_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["modulos"]
)
async def deletar_modulo(
    modulo_id: int, db: AsyncSession = Depends(get_async_session)
) -> None:
    await service.deletar_modulo(db, modulo_id)


### conteudos


@router.post(
    "/modulos/{modulo_id}/conteudos",
    response_model=ConteudoRead,
    status_code=status.HTTP_201_CREATED,
    tags=["conteudos"],
)
async def criar_conteudo(
    modulo_id: int, data: ConteudoCreate, db: AsyncSession = Depends(get_async_session)
) -> Conteudo:
    return await service.criar_conteudo(db, modulo_id, data)


@router.get(
    "/modulos/{modulo_id}/conteudos",
    response_model=list[ConteudoRead],
    tags=["conteudos"],
)
async def listar_conteudos(
    modulo_id: int, db: AsyncSession = Depends(get_async_session)
) -> list[Conteudo]:
    return await service.listar_conteudos(db, modulo_id)


@router.get("/conteudos/{conteudo_id}", response_model=ConteudoRead, tags=["conteudos"])
async def obter_conteudo(
    conteudo_id: int, db: AsyncSession = Depends(get_async_session)
) -> Conteudo:
    return await service.buscar_conteudo(db, conteudo_id)


@router.patch(
    "/conteudos/{conteudo_id}", response_model=ConteudoRead, tags=["conteudos"]
)
async def atualizar_conteudo(
    conteudo_id: int,
    data: ConteudoUpdate,
    db: AsyncSession = Depends(get_async_session),
) -> Conteudo:
    return await service.atualizar_conteudo(db, conteudo_id, data)


@router.delete(
    "/conteudos/{conteudo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["conteudos"],
)
async def deletar_conteudo(
    conteudo_id: int, db: AsyncSession = Depends(get_async_session)
) -> None:
    await service.deletar_conteudo(db, conteudo_id)


### questoes


@router.post(
    "/conteudos/{conteudo_id}/questoes",
    response_model=QuestaoRead,
    status_code=status.HTTP_201_CREATED,
    tags=["questoes"],
)
async def criar_questao(
    conteudo_id: int, data: QuestaoCreate, db: AsyncSession = Depends(get_async_session)
) -> Questao:
    return await service.criar_questao(db, conteudo_id, data)


@router.get(
    "/conteudos/{conteudo_id}/questoes",
    response_model=list[QuestaoRead],
    tags=["questoes"],
)
async def listar_questoes(
    conteudo_id: int, db: AsyncSession = Depends(get_async_session)
) -> list[Questao]:
    return await service.listar_questoes(db, conteudo_id)


@router.get("/questoes/{questao_id}", response_model=QuestaoRead, tags=["questoes"])
async def obter_questao(
    questao_id: int, db: AsyncSession = Depends(get_async_session)
) -> Questao:
    return await service.buscar_questao(db, questao_id)


@router.patch("/questoes/{questao_id}", response_model=QuestaoRead, tags=["questoes"])
async def atualizar_questao(
    questao_id: int, data: QuestaoUpdate, db: AsyncSession = Depends(get_async_session)
) -> Questao:
    return await service.atualizar_questao(db, questao_id, data)


@router.delete(
    "/questoes/{questao_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["questoes"]
)
async def deletar_questao(
    questao_id: int, db: AsyncSession = Depends(get_async_session)
) -> None:
    await service.deletar_questao(db, questao_id)


### alternativas


@router.post(
    "/questoes/{questao_id}/alternativas",
    response_model=AlternativaRead,
    status_code=status.HTTP_201_CREATED,
    tags=["alternativas"],
)
async def criar_alternativa(
    questao_id: int,
    data: AlternativaCreate,
    db: AsyncSession = Depends(get_async_session),
) -> Alternativa:
    return await service.criar_alternativa(db, questao_id, data)


@router.get(
    "/questoes/{questao_id}/alternativas",
    response_model=list[AlternativaRead],
    tags=["alternativas"],
)
async def listar_alternativas(
    questao_id: int, db: AsyncSession = Depends(get_async_session)
) -> list[Alternativa]:
    return await service.listar_alternativas(db, questao_id)


@router.get(
    "/alternativas/{alternativa_id}",
    response_model=AlternativaRead,
    tags=["alternativas"],
)
async def obter_alternativa(
    alternativa_id: int, db: AsyncSession = Depends(get_async_session)
) -> Alternativa:
    return await service.buscar_alternativa(db, alternativa_id)


@router.patch(
    "/alternativas/{alternativa_id}",
    response_model=AlternativaRead,
    tags=["alternativas"],
)
async def atualizar_alternativa(
    alternativa_id: int,
    data: AlternativaUpdate,
    db: AsyncSession = Depends(get_async_session),
) -> Alternativa:
    return await service.atualizar_alternativa(db, alternativa_id, data)


@router.delete(
    "/alternativas/{alternativa_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["alternativas"],
)
async def deletar_alternativa(
    alternativa_id: int, db: AsyncSession = Depends(get_async_session)
) -> None:
    await service.deletar_alternativa(db, alternativa_id)
