from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.conquistas.model import Conquista, associacao_conquista_usuario
from app.domains.usuario.model import AcessoUsuario, Usuario


# so as queries do usuario. a lib fastcrud n serve aqui pq o create precisa
# hashear a senha (password vira hashed_password). o service faz a logica
class UsuarioRepository:
    def __init__(self, db: AsyncSession):
        self.db = db  # session recebida uma vez, todo metodo usa self.db

    async def buscar(self, user_id: int) -> Usuario | None:
        return await self.db.get(Usuario, user_id)  # get = busca por PK

    async def buscar_por_username(self, username: str) -> Usuario | None:
        resultado = await self.db.execute(
            select(Usuario).where(Usuario.username == username)
        )
        return resultado.scalar_one_or_none()

    async def buscar_por_email(self, email: str) -> Usuario | None:
        resultado = await self.db.execute(select(Usuario).where(Usuario.email == email))
        return resultado.scalar_one_or_none()

    # a busca olha o email de verdade, mas quem chama so recebe ele mascarado
    async def listar(self, busca: str | None = None, limite: int | None = None) -> list[Usuario]:
        consulta = select(Usuario).order_by(Usuario.id)
        if busca:
            termo = f"%{busca}%"
            condicao = Usuario.username.ilike(termo) | Usuario.email.ilike(termo)
            # so numero tb procura pelo id exato
            if busca.isdigit():
                condicao = condicao | (Usuario.id == int(busca))
            consulta = consulta.where(condicao)
        if limite is not None:
            consulta = consulta.limit(limite)
        resultado = await self.db.execute(consulta)
        return list(resultado.scalars().all())

    async def buscar_varios(self, ids: list[int]) -> list[Usuario]:
        resultado = await self.db.execute(select(Usuario).where(Usuario.id.in_(ids)))
        return list(resultado.scalars().all())

    ###### ultimo acesso
    # cria a linha no primeiro acesso, nos proximos so troca a data
    async def registrar_acesso(self, usuario_id: int, quando: datetime) -> None:
        acesso = await self.db.get(AcessoUsuario, usuario_id)
        if acesso is None:
            acesso = AcessoUsuario(usuario_id=usuario_id, ultimo_acesso_em=quando)
            self.db.add(acesso)
        else:
            acesso.ultimo_acesso_em = quando
        await self.db.commit()

    async def listar_acessos(self, ids: list[int]) -> dict[int, datetime]:
        resultado = await self.db.execute(
            select(AcessoUsuario.usuario_id, AcessoUsuario.ultimo_acesso_em).where(AcessoUsuario.usuario_id.in_(ids))
        )
        acessos = {}
        for usuario_id, quando in resultado.all():
            acessos[usuario_id] = quando
        return acessos

    # serve pra criar e editar: add num objeto novo insere, num existente
    # so marca e o commit salva as mudancas
    async def salvar(self, user: Usuario) -> Usuario:
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)  # recarrega pra pegar id/defaults do banco
        return user


    # esse metódo usa a tabela de associação para buscar todas as
    # conquistas que o usuario tem. antes eu queria fazer um desses
    # no repository da conquista para mostrar quais usuarios tem cada,
    # mas conclui que não tem necessidade. Só se no futuro fizermos
    # estatiscas nas conquistas.
    # mais nova primeiro, junto com a data q ganhou
    async def listar_conquistas(self, user_id: int) -> list[tuple[Conquista, datetime | None]]:
        resultado = await self.db.execute(
            select(Conquista, associacao_conquista_usuario.c.desbloqueada_em)
            .join(
                associacao_conquista_usuario,
                associacao_conquista_usuario.c.conquista_id == Conquista.id,
            )
            .where(associacao_conquista_usuario.c.usuario_id == user_id)
            .order_by(associacao_conquista_usuario.c.desbloqueada_em.desc(), Conquista.id)
        )
        conquistas = []
        for conquista, desbloqueada_em in resultado.all():
            conquistas.append((conquista, desbloqueada_em))
        return conquistas