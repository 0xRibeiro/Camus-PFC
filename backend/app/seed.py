from app.core.config import settings
from app.core.database import async_session_maker
from app.core.security import criar_hash
from app.domains.usuario.model import RoleUsuario, Usuario
from app.domains.usuario.repository import UsuarioRepository


# cria o primeiro admin no boot 
async def seed_admin() -> None:
    if not settings.admin_email or not settings.admin_password:
        return

    async with async_session_maker() as db:
        repo = UsuarioRepository(db)
        if await repo.buscar_por_username(settings.admin_username) is not None:
            return

        await repo.salvar(
            Usuario(
                username=settings.admin_username,
                email=settings.admin_email,
                hashed_password=criar_hash(settings.admin_password),
                role=RoleUsuario.admin,
            )
        )
