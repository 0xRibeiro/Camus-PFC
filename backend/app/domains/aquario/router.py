from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.domains.aquario import service
from app.domains.aquario.model import Aquario
from app.domains.aquario.schema import (
    AquarioCreate,
    AquarioEntrar,
    AquarioRead,
    ConviteAquarioRead,
    MembroAquarioRead,
)
from app.domains.dispositivo.model import Dispositivo
from app.domains.dispositivo.schema import CodigoDispositivo, DispositivoRead
from app.domains.peixe.model import Peixe
from app.domains.peixe.schema import PeixeCreate, PeixeRead
from app.domains.usuario.model import Usuario
from app.domains.usuario.service import get_current_user

router = APIRouter(prefix="/aquarios", tags=["aquarios"])

# rota simples para retornar os aquarios do usuario.
@router.get("", response_model=list[AquarioRead])
async def listar_aquarios(db: AsyncSession = Depends(get_async_session), usuario: Usuario = Depends(get_current_user)) -> list[AquarioRead]:
    return await service.listar_aquarios(db, usuario.id)

# rota para criar um aquario, sem necessidade de cadastrar um sensor IoT.
@router.post("", response_model=AquarioRead, status_code=status.HTTP_201_CREATED)
async def criar_aquario(data: AquarioCreate, db: AsyncSession = Depends(get_async_session), usuario: Usuario = Depends(get_current_user)) -> Aquario:
    aquario = Aquario(nome=data.nome, litros=data.litros, id_dono=usuario.id)
    db.add(aquario)
    await db.commit()
    await db.refresh(aquario)
    return aquario

@router.post("/entrar-com-codigo", response_model=AquarioRead, status_code=status.HTTP_201_CREATED)
async def entrar_com_codigo(data: CodigoDispositivo, db: AsyncSession = Depends(get_async_session),
    usuario: Usuario = Depends(get_current_user)) -> AquarioRead:
    return await service.entrar_com_codigo(db, data, usuario.id)


@router.post("/entrar", response_model=AquarioRead, status_code=status.HTTP_201_CREATED)
async def entrar_com_convite(data: AquarioEntrar, db: AsyncSession = Depends(get_async_session),
    usuario: Usuario = Depends(get_current_user)) -> AquarioRead:
    return await service.entrar_com_convite(db, data, usuario.id)


@router.post("/{aquario_id}/dispositivo", response_model=DispositivoRead, status_code=status.HTTP_201_CREATED)
async def conectar_dispositivo(aquario_id: int, data: CodigoDispositivo, db: AsyncSession = Depends(get_async_session),
    usuario: Usuario = Depends(get_current_user)) -> Dispositivo:
    return await service.conectar_dispositivo(db, aquario_id, data, usuario.id)


@router.delete("/{aquario_id}/dispositivo", status_code=status.HTTP_204_NO_CONTENT)
async def desconectar_dispositivo(aquario_id: int, db: AsyncSession = Depends(get_async_session),
    usuario: Usuario = Depends(get_current_user)) -> None:
    await service.desconectar_dispositivo(db, aquario_id, usuario.id)


@router.post("/{aquario_id}/convites", response_model=ConviteAquarioRead, status_code=status.HTTP_201_CREATED)
async def gerar_convite(aquario_id: int, db: AsyncSession = Depends(get_async_session),
    usuario: Usuario = Depends(get_current_user)) -> ConviteAquarioRead:
    return await service.gerar_convite(db, aquario_id, usuario.id)


@router.get("/{aquario_id}/membros", response_model=list[MembroAquarioRead])
async def listar_membros(aquario_id: int, db: AsyncSession = Depends(get_async_session),
    usuario: Usuario = Depends(get_current_user)) -> list[MembroAquarioRead]:
    return await service.listar_membros(db, aquario_id, usuario.id)


@router.delete("/{aquario_id}/sair", status_code=status.HTTP_204_NO_CONTENT)
async def sair_do_aquario(aquario_id: int, db: AsyncSession = Depends(get_async_session),
    usuario: Usuario = Depends(get_current_user)) -> None:
    await service.sair_do_aquario(db, aquario_id, usuario.id)

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
async def buscar_aquario(aquario_id: int, db: AsyncSession = Depends(get_async_session), usuario: Usuario = Depends(get_current_user)) -> AquarioRead:
    return await service.buscar_aquario(db, aquario_id, usuario.id)

# mesmo o peixe tendo seu proprio domain, ficou mais facil implementar as rotas dele dentro do aquario por enquanto. se for 
# pra dividir ele pra la, sinceramente não sei como ficaria ja que ele usa o id do aquario antes do /peixes. vemos isso depois.