from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.domains.auditoria.repository import AuditoriaRepository
from app.domains.auditoria.schema import LogAuditoriaRead
from app.domains.usuario.model import RoleUsuario
from app.domains.usuario.service import exige_role

router = APIRouter(
    prefix="/admin/auditoria",
    tags=["admin"],
    dependencies=[Depends(exige_role(RoleUsuario.admin))],
)


@router.get("", response_model=list[LogAuditoriaRead])
async def listar_logs(
    limite: int = 50,
    offset: int = 0,
    # lista vem repetindo o parametro: ?entidades=trilhas&entidades=modulos
    entidades: list[str] | None = Query(default=None),
    entidade_id: int | None = None,
    usuario_ids: list[int] | None = Query(default=None),
    desde: datetime | None = None,
    ate: datetime | None = None,
    db: AsyncSession = Depends(get_async_session),
):
    repo = AuditoriaRepository(db)
    resultado = await repo.listar(limite, offset, entidades, entidade_id, usuario_ids, desde, ate)

    logs = []
    for log, username in resultado:
        item = LogAuditoriaRead.model_validate(log)
        item.usuario_nome = username
        logs.append(item)
    return logs
