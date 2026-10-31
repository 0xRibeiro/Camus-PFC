from datetime import date

from sqlalchemy import Date, cast, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.auditoria.model import AcaoAuditoria, LogAuditoria
from app.domains.conquistas.model import Conquista, associacao_conquista_usuario
from app.domains.grupo.model import Grupo
from app.domains.trilha.model import Trilha
from app.domains.usuario.model import Usuario


# todos podem retornar 0 caso não tenha dados pra não quebrar a dash
class DashboardRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def contar_usuarios(self) -> int:
        return await self.db.scalar(select(func.count()).select_from(Usuario)) or 0

    async def contar_grupos(self) -> int:
        return await self.db.scalar(select(func.count()).select_from(Grupo)) or 0

    async def contar_conquistas_concedidas(self) -> int:
        return await self.db.scalar(select(func.count()).select_from(associacao_conquista_usuario)) or 0

    async def contar_trilhas(self) -> int:
        return await self.db.scalar(select(func.count()).select_from(Trilha)) or 0

    async def contar_cadastros_por_dia(self, inicio: date, fim: date) -> dict[date, int]:
    # usa apenas a parte da data para agrupar os registros
        dia = cast(LogAuditoria.criado_em, Date)

        # query bem especifica só pra contar os cadastros acontecidos no dia utilizando dados da auditoria.
        resultado = await self.db.execute(select(dia, func.count()).where(LogAuditoria.entidade == "usuarios",
        LogAuditoria.acao == AcaoAuditoria.create, dia >= inicio, dia <= fim).group_by(dia).order_by(dia))

        return {data: quantidade for data, quantidade in resultado.all()}

    async def contar_conquistas_por_quantidade(self) -> list[tuple[int, str, int]]:
        quantidade = func.count(associacao_conquista_usuario.c.usuario_id)

        # esse resultado retorna até conquistas ainda não concedidas como 0. também ordena por mais obtidas primeiro.
        resultado = await self.db.execute(select(Conquista.id, Conquista.titulo, quantidade).outerjoin(associacao_conquista_usuario,
        associacao_conquista_usuario.c.conquista_id == Conquista.id).group_by(Conquista.id, Conquista.titulo).order_by(quantidade.desc(),
        Conquista.titulo, Conquista.id))

        return [(conquista_id, titulo, total) for conquista_id, titulo, total in resultado.all()]

    # pegando a data direto do postgres pra garantir que seja a mesma pra todos os cálculos.
    async def buscar_data_atual(self) -> date:
        resultado = await self.db.execute(select(func.current_date()))
        return resultado.scalar_one()