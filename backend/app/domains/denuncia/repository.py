from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from app.domains.denuncia.model import STATUS_PENDENTE, Denuncia
from app.domains.denuncia.schema import DenunciaAdminRead
from app.domains.grupo.model import Grupo
from app.domains.trilha.model import Conteudo, Modulo, Trilha
from app.domains.usuario.model import Usuario


class DenunciaRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def buscar(self, denuncia_id: int) -> Denuncia | None:
        return await self.db.get(Denuncia, denuncia_id)

    async def criar(self, denuncia: Denuncia) -> Denuncia:
        self.db.add(denuncia)
        await self.db.commit()
        await self.db.refresh(denuncia)
        return denuncia

    async def salvar(self, denuncia: Denuncia) -> Denuncia:
        await self.db.commit()
        await self.db.refresh(denuncia)
        return denuncia

    # vê se esse usuário já tem uma denúncia pendente contra o mesmo alvo, seja o grupo ou um conteúdo
    async def buscar_pendente(self, id_denunciante: int, id_grupo: int, id_conteudo: int | None) -> Denuncia | None:
        consulta = select(Denuncia).where(
            Denuncia.id_denunciante == id_denunciante,
            Denuncia.id_grupo == id_grupo,
            Denuncia.status == STATUS_PENDENTE,
            Denuncia.id_conteudo.is_(None) if id_conteudo is None else Denuncia.id_conteudo == id_conteudo,
        )
        resultado = await self.db.execute(consulta)
        return resultado.scalars().first()

    # confere se o conteúdo faz parte de alguma trilha desse grupo (conteudo -> modulo -> trilha -> grupo)
    async def conteudo_pertence_ao_grupo(self, id_conteudo: int, id_grupo: int) -> bool:
        consulta = (
            select(Conteudo.id)
            .join(Modulo, Modulo.id == Conteudo.modulo_id)
            .join(Trilha, Trilha.id == Modulo.trilha_id)
            .where(Conteudo.id == id_conteudo, Trilha.grupo_id == id_grupo)
        )
        resultado = await self.db.execute(consulta)
        return resultado.first() is not None

    # lista pro admin com as mais recentes primeiro. dá pra filtrar passando o status.
    async def listar(self, status: str | None = None) -> list[DenunciaAdminRead]:
        denunciante = aliased(Usuario)
        dono = aliased(Usuario)

        consulta = (
            select(Denuncia, denunciante.username, Grupo.nome, dono.username, Conteudo.titulo)
            .join(denunciante, denunciante.id == Denuncia.id_denunciante)
            .join(Grupo, Grupo.id == Denuncia.id_grupo)
            .join(dono, dono.id == Grupo.id_dono)
            .outerjoin(Conteudo, Conteudo.id == Denuncia.id_conteudo)
            .order_by(Denuncia.criado_em.desc(), Denuncia.id.desc())
        )
        if status is not None:
            consulta = consulta.where(Denuncia.status == status)

        resultado = await self.db.execute(consulta)
        return [
            DenunciaAdminRead(
                id=denuncia.id,
                id_grupo=denuncia.id_grupo,
                id_conteudo=denuncia.id_conteudo,
                motivo=denuncia.motivo,
                descricao=denuncia.descricao,
                status=denuncia.status,
                criado_em=denuncia.criado_em,
                resolvido_em=denuncia.resolvido_em,
                denunciante=nome_denunciante,
                grupo=nome_grupo,
                dono=nome_dono,
                conteudo=titulo_conteudo,
            )
            for denuncia, nome_denunciante, nome_grupo, nome_dono, titulo_conteudo in resultado.all()
        ]