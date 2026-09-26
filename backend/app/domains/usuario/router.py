from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.domains.conquistas.schema import ConquistaRead
from app.domains.usuario import service
from app.domains.usuario.model import RoleUsuario, Usuario
from app.domains.usuario.schema import (
    RefreshInput,
    TokenPair,
    UsuarioAdminUpdate,
    UsuarioCreate,
    UsuarioLogin,
    UsuarioRead,
    UsuarioStaffCreate,
    UsuarioUpdate,
)

router = APIRouter()


### auth


@router.post(
    "/auth/register",
    response_model=UsuarioRead,
    status_code=status.HTTP_201_CREATED,
    tags=["auth"],
)
async def register(
    data: UsuarioCreate,
    db: AsyncSession = Depends(get_async_session),
) -> Usuario:
    return await service.criar_aluno(db, data)


@router.post("/auth/login", tags=["auth"])
async def login(
    credentials: UsuarioLogin,
    db: AsyncSession = Depends(get_async_session),
) -> TokenPair:
    user = await service.autenticar(db, credentials.email, credentials.password)
    return await service.emitir_tokens(user)


@router.post("/auth/refresh", tags=["auth"])
async def refresh(
    data: RefreshInput,
    db: AsyncSession = Depends(get_async_session),
) -> TokenPair:
    return await service.renovar_tokens(db, data.refresh_token)


@router.post("/auth/logout", status_code=status.HTTP_204_NO_CONTENT, tags=["auth"])
async def logout(data: RefreshInput) -> None:
    await service.logout(data.refresh_token)


### usuario

# tudo aqui é o proprio usuario mexendo em si mesmo


@router.get("/usuarios/me", response_model=UsuarioRead, tags=["usuarios"])
async def read_me(user: Usuario = Depends(service.get_current_user)) -> Usuario:
    return user


@router.get("/usuarios/me/aceite-termos", tags=["usuarios"])
async def verificar_meu_aceite(
    user: Usuario = Depends(service.get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    aceitou = await service.verificar_aceite_termos(db, user.id)

    return {
        "aceitou": aceitou,
        "termos_versao": service.TERMOS_VERSAO_ATUAL,
        "privacidade_versao": service.PRIVACIDADE_VERSAO_ATUAL,
    }

@router.post("/usuarios/me/aceite-termos", tags=["usuarios"])
async def registrar_meu_aceite(
    user: Usuario = Depends(service.get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    aceite = await service.registrar_aceite_termos(db, user)

    return {
        "id": aceite.id,
        "usuario_id": aceite.usuario_id,
        "termos_versao": aceite.termos_versao,
        "privacidade_versao": aceite.privacidade_versao,
        "aceito_em": aceite.aceito_em,
    }


@router.get(
    "/usuarios/me/conquistas",
    response_model=list[ConquistaRead],
    tags=["conquistas"],
)
async def listar_minhas_conquistas(
    user: Usuario = Depends(service.get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    return await service.listar_conquistas_usuario(db, user.id)


# essa rota recebede o id da conquista desbloqueada, retirando
# a necessidade de criar uma rota pra cada uma.
@router.post(
    "/usuarios/me/conquistas/{conquista_id}",
    response_model=ConquistaRead | None,
    tags=["conquistas"],
)
async def desbloquear_conquista(
    conquista_id: int,
    user: Usuario = Depends(service.get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    return await service.conceder_conquista(db, user.id, conquista_id)


@router.patch("/usuarios/me", response_model=UsuarioRead, tags=["usuarios"])
async def update_me(
    data: UsuarioUpdate,
    user: Usuario = Depends(service.get_current_user),
    db: AsyncSession = Depends(get_async_session),
) -> Usuario:
    return await service.atualizar_usuario(db, user, data)


@router.delete(
    "/usuarios/me",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["usuarios"],
)
async def delete_me(
    user: Usuario = Depends(service.get_current_user),
    db: AsyncSession = Depends(get_async_session),
) -> None:
    await service.deletar_usuario(db, user)


### admin (gestão de contas)

# o dependencies=[] no router aplica a checagem de admin em todas as rotas desse router
# list/get/delete poderiam ser fastcrud, mas create precusa hashear senha
admin_router = APIRouter(
    prefix="/admin/usuarios",
    tags=["admin"],
    dependencies=[Depends(service.exige_role(RoleUsuario.admin))],
)


@admin_router.get("", response_model=list[UsuarioRead])
async def listar_usuarios(
    db: AsyncSession = Depends(get_async_session),
) -> list[Usuario]:
    return await service.listar_usuarios(db)


@admin_router.get("/{user_id}", response_model=UsuarioRead)
async def obter_usuario(
    user_id: int,
    db: AsyncSession = Depends(get_async_session),
) -> Usuario:
    return await service.buscar_usuario(db, user_id)


@admin_router.post(
    "",
    response_model=UsuarioRead,
    status_code=status.HTTP_201_CREATED,
)
async def criar_staff(
    data: UsuarioStaffCreate,
    db: AsyncSession = Depends(get_async_session),
) -> Usuario:
    return await service.criar_staff(db, data)


@admin_router.patch("/{user_id}", response_model=UsuarioRead)
async def atualizar_staff(
    user_id: int,
    data: UsuarioAdminUpdate,
    db: AsyncSession = Depends(get_async_session),
) -> Usuario:
    return await service.atualizar_usuario_admin(db, user_id, data)


@admin_router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_usuario(
    user_id: int,
    db: AsyncSession = Depends(get_async_session),
) -> None:
    user = await service.buscar_usuario(db, user_id)
    await service.deletar_usuario(db, user)
