from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.domains.aquario import service
from app.domains.aquario.model import Aquario
from app.domains.aquario.repository import AquarioRepository
from app.domains.aquario.schema import AquarioCreate, AquarioRead
from app.domains.peixe.model import Peixe
from app.domains.peixe.schema import PeixeCreate, PeixeRead
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

# rota para listar os peixes do usuario, primeiro fazendo a verificação e depois chamando a service.
@router.get("/{aquario_id}/peixes", response_model=list[PeixeRead])
async def listar_peixes(aquario_id: int, db: AsyncSession = Depends(get_async_session), usuario: Usuario = Depends(get_current_user)) -> list[Peixe]:
    return await service.listar_peixes(db, aquario_id, usuario.id)

# rota para cadastrar um peixe em determinado aquario. 
@router.post("/{aquario_id}/peixes", response_model=PeixeRead, status_code=status.HTTP_201_CREATED)
async def cadastrar_peixe(aquario_id: int, data: PeixeCreate, db: AsyncSession = Depends(get_async_session),
    usuario: Usuario = Depends(get_current_user)) -> Peixe:
    return await service.cadastrar_peixe(db, aquario_id, data, usuario.id)

# rota para buscar um aquario do usuario, caso ele nao seja dono de nenhum retorna 404
@router.get("/{aquario_id}", response_model=AquarioRead)
async def buscar_aquario(aquario_id: int, db: AsyncSession = Depends(get_async_session), usuario: Usuario = Depends(get_current_user)) -> Aquario:
    return await service.buscar_aquario_do_usuario(
        AquarioRepository(db), aquario_id, usuario.id,
    )

# mesmo o peixe tendo seu proprio domain, ficou mais facil implementar as rotas dele dentro do aquario por enquanto. se for 
# pra dividir ele pra la, sinceramente não sei como ficaria ja que ele usa o id do aquario antes do /peixes. vemos isso depois.