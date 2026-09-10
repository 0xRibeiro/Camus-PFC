from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.usuario.model import Usuario


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

    async def listar(self) -> list[Usuario]:
        resultado = await self.db.execute(select(Usuario).order_by(Usuario.id))
        return list(resultado.scalars().all())

    # serve pra criar e editar: add num objeto novo insere, num existente
    # so marca e o commit salva as mudancas
    async def salvar(self, user: Usuario) -> Usuario:
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)  # recarrega pra pegar id/defaults do banco
        return user

    async def deletar(self, user: Usuario) -> None:
        await self.db.delete(user)
        await self.db.commit()
