from fastcrud import crud_router

from app.core.database import get_async_session
from app.domains.conquistas.model import Conquista, associacao_conquista_usuario
from app.domains.conquistas.schema import (
	ConquistaCreate,
	ConquistaRead,
	ConquistaUpdate,
	associacao_conquista_usuarioCreate,
	associacao_conquista_usuarioRead,
	associacao_conquista_usuarioUpdate,
)
from app.domains.usuario.model import RoleUsuario
from app.domains.usuario.service import exige_role

apenas_staff = [exige_role(RoleUsuario.author, RoleUsuario.admin)]


conquista_router = crud_router(
	session=get_async_session,
	model=Conquista,
	create_schema=ConquistaCreate,
	update_schema=ConquistaUpdate,
	select_schema=ConquistaRead,
	path="/conquistas",
	tags=["conquistas"],
	create_deps=apenas_staff,
	update_deps=apenas_staff,
	delete_deps=apenas_staff,
)

associar_conquista_router = crud_router(
	session=get_async_session,
	model=associacao_conquista_usuario,
    create_schema=associacao_conquista_usuarioCreate,
    update_schema=associacao_conquista_usuarioUpdate,
    select_schema=associacao_conquista_usuarioRead,
	path="/associar-conquista",
	tags=["associar-conquista"],
	create_deps=apenas_staff,
	update_deps=apenas_staff,
	delete_deps=apenas_staff,
)