from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.domains.minigame import service
from app.domains.minigame.schema import RespostaInput, ResultadoRead, RodadaRead
from app.domains.usuario.model import Usuario
from app.domains.usuario.service import get_current_user

router = APIRouter(prefix="/minigames", tags=["minigames"])


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
