from fastapi import APIRouter, Depends
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
    entidade: str | None = None,
    entidade_id: int | None = None,
    usuario_id: int | None = None,
    db: AsyncSession = Depends(get_async_session),
):
    repo = AuditoriaRepository(db)
    return await repo.listar(limite, offset, entidade, entidade_id, usuario_id)
