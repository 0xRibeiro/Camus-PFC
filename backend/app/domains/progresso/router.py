from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.domains.progresso import service
from app.domains.progresso.schema import (
    ConclusaoRead,
    ConteudoAlunoRead,
    TrilhaAlunoRead,
    TrilhaResumoRead,
)
from app.domains.usuario.model import Usuario
from app.domains.usuario.service import get_current_user

router = APIRouter(prefix="/progresso", tags=["progresso"])


###### trilhas do aluno
@router.get("/trilhas", response_model=list[TrilhaResumoRead])
async def listar_trilhas(
    db: AsyncSession = Depends(get_async_session),
    usuario: Usuario = Depends(get_current_user),
) -> list[TrilhaResumoRead]:
    return await service.listar_trilhas(db, usuario)


@router.get("/trilhas/{trilha_id}", response_model=TrilhaAlunoRead)
async def buscar_trilha(
    trilha_id: int,
    db: AsyncSession = Depends(get_async_session),
    usuario: Usuario = Depends(get_current_user),
) -> TrilhaAlunoRead:
    return await service.buscar_trilha(db, trilha_id, usuario)


###### conteudo do aluno
@router.get("/conteudos/{conteudo_id}", response_model=ConteudoAlunoRead)
async def buscar_conteudo(
    conteudo_id: int,
    db: AsyncSession = Depends(get_async_session),
    usuario: Usuario = Depends(get_current_user),
) -> ConteudoAlunoRead:
    return await service.buscar_conteudo(db, conteudo_id, usuario)


@router.post("/conteudos/{conteudo_id}/concluir", response_model=ConclusaoRead)
async def concluir_conteudo(
    conteudo_id: int,
    db: AsyncSession = Depends(get_async_session),
    usuario: Usuario = Depends(get_current_user),
) -> ConclusaoRead:
    return await service.concluir_conteudo(db, conteudo_id, usuario)
