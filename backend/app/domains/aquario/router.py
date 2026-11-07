from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.domains.aquario.model import Aquario
from app.domains.aquario.schema import AquarioCreate, AquarioRead
from app.domains.usuario.model import Usuario
from app.domains.usuario.service import get_current_user

router = APIRouter(prefix="/aquarios", tags=["aquarios"])


# rota simples para retornar os aquarios do usuario.
@router.get("", response_model=list[AquarioRead])
async def listar_aquarios(db: AsyncSession = Depends(get_async_session), usuario: Usuario = Depends(get_current_user)) -> list[Aquario]:
    consulta = (select(Aquario).where(Aquario.id_dono == usuario.id).order_by(Aquario.id))
    return list((await db.scalars(consulta)).all())

# rota para criar um aquario, sem necessidade de cadastrar um sensor IoT.
@router.post("", response_model=AquarioRead, status_code=status.HTTP_201_CREATED)
async def criar_aquario(data: AquarioCreate, db: AsyncSession = Depends(get_async_session), usuario: Usuario = Depends(get_current_user)) -> Aquario:
    aquario = Aquario(nome=data.nome, litros=data.litros, id_dono=usuario.id)
    db.add(aquario)
    await db.commit()
    await db.refresh(aquario)
    return aquario