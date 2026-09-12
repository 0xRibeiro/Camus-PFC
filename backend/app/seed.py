from app.core.config import settings
from app.core.database import async_session_maker
from app.core.security import criar_hash
from app.domains.conquistas.model import Conquista
from app.domains.conquistas.repository import ConquistaRepository
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


# Método teste para gerar conquistas hardcoded.
async def seed_conquistas() -> None:
    
    async with async_session_maker() as db:
        repo = ConquistaRepository(db)
        if await repo.listar():
            return

        await repo.salvar(Conquista(
            titulo="Primeira Conquista",
            descricao="Mude a cor do site",
            imagem_dir="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSQlGmYfDo0sQajoEu2Uaa_9FuPzcBLsXjpPJ4r56H83w&s=10"
        ))
