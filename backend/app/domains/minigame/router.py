from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.domains.minigame import service
from app.domains.minigame.schema import (
    PalpiteInput,
    RecordeRead,
    RespostaInput,
    ResultadoMaisOuMenosRead,
    ResultadoRead,
    RodadaMaisOuMenosRead,
    RodadaRead,
)
from app.domains.usuario.model import Usuario
from app.domains.usuario.service import get_current_user

router = APIRouter(prefix="/minigames", tags=["minigames"])


@router.get("/recordes", response_model=list[RecordeRead])
async def meus_recordes(
    db: AsyncSession = Depends(get_async_session),
    usuario: Usuario = Depends(get_current_user),
) -> list[RecordeRead]:
    return await service.meus_recordes(db, usuario)


@router.post("/quem-e-esse-peixe/rodadas", response_model=RodadaRead, status_code=201)
async def nova_rodada(
    db: AsyncSession = Depends(get_async_session),
    usuario: Usuario = Depends(get_current_user),
) -> RodadaRead:
    return await service.nova_rodada(db, usuario)


@router.post("/quem-e-esse-peixe/rodadas/{rodada_id}/resposta", response_model=ResultadoRead)
async def responder(
    rodada_id: int,
    resposta: RespostaInput,
    db: AsyncSession = Depends(get_async_session),
    usuario: Usuario = Depends(get_current_user),
) -> ResultadoRead:
    return await service.responder(db, usuario, rodada_id, resposta.taxon_id)


# devolve a rodada aberta se tiver, por isso n é 201
@router.post("/meio-peixe-meio-fotografo/rodadas", response_model=RodadaMaisOuMenosRead)
async def nova_rodada_mais_ou_menos(
    db: AsyncSession = Depends(get_async_session),
    usuario: Usuario = Depends(get_current_user),
) -> RodadaMaisOuMenosRead:
    return await service.nova_rodada_mais_ou_menos(db, usuario)


@router.post("/meio-peixe-meio-fotografo/rodadas/{rodada_id}/resposta", response_model=ResultadoMaisOuMenosRead)
async def responder_mais_ou_menos(
    rodada_id: int,
    palpite: PalpiteInput,
    db: AsyncSession = Depends(get_async_session),
    usuario: Usuario = Depends(get_current_user),
) -> ResultadoMaisOuMenosRead:
    return await service.responder_mais_ou_menos(db, usuario, rodada_id, palpite.palpite)
