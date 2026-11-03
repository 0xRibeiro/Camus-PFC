from app.core.config import settings
from app.core.database import async_session_maker
from app.core.security import criar_hash
from app.domains.conquistas.model import Conquista
from app.domains.conquistas.repository import ConquistaRepository
from app.domains.usuario.model import RoleUsuario, Usuario
from app.domains.usuario.repository import UsuarioRepository

# id, título e condição para desbloquear cada conquista.
CONQUISTAS = [
    (1, "Cores do mar", "Troque o tema do site."),
    (2, "Horizonte aberto", "Esconda o menu lateral."),
    (3, "Conhecendo as regras", "Leia os Termos de Uso."),
    (4, "Segredo das profundezas", "Encontre a página secreta."),
    (5, "Explorador marinho", "Visite a coleção de peixes."),
    (6, "Pesquisador do iNaturalist", "Faça uma pesquisa na coleção que encontre ao menos uma espécie."),
    (7, "Olhar de biólogo", "Selecione uma espécie para consultar seus detalhes."),
    (8, "Capitão da tripulação", "Crie seu primeiro grupo de estudos."),
    (9, "Mergulho em equipe", "Entre em um grupo usando um convite."),
    (10, "Convite a bordo", "Gere um convite para o seu grupo."),
]


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


# cadastra as conquistas no sistema.
async def seed_conquistas() -> None:
    async with async_session_maker() as db:
        repo = ConquistaRepository(db)

        for conquista_id, titulo, descricao in CONQUISTAS:
            conquista = await repo.buscar(conquista_id)

            if conquista is None:
                conquista = Conquista(id=conquista_id)

            conquista.titulo = titulo
            conquista.descricao = descricao
            ## estou deixando vazio por enquanto pra testar até encontrar e salvar as imagens das conquistas no projeto
            conquista.imagem_dir = ""

            await repo.salvar(conquista)