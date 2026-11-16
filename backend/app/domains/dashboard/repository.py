from datetime import date

from sqlalchemy import Date, cast, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.auditoria.model import AcaoAuditoria, LogAuditoria
from app.domains.conquistas.model import Conquista, associacao_conquista_usuario
from app.domains.dispositivo.model import Dispositivo
from app.domains.trilha.model import Trilha
from app.domains.usuario.model import RoleUsuario, Usuario

# dia no fuso de sp, o log fica sem fuso
DIA_DO_LOG = cast(func.timezone("America/Sao_Paulo", func.timezone("UTC", LogAuditoria.criado_em)), Date)


def montar_contagem(linhas) -> dict[date, int]:
    contagem = {}
    for dia, quantidade in linhas:
        contagem[dia] = quantidade
    return contagem


# todos podem retornar 0 caso não tenha dados pra não quebrar a dash
class DashboardRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    # atualiza o metodo de contar trilhas pra fornecer dados pra dash
    async def contar_trilhas_por_escopo(self) -> tuple[int, int]:
        resultado = await self.db.execute(select(func.count().filter(Trilha.grupo_id.is_(None)), func.count(Trilha.grupo_id)).select_from(Trilha))
        globais, de_grupo = resultado.one()
        return globais, de_grupo

    # criacoes por dia pela auditoria, serve pra trilhas e grupos
    async def contar_criados_por_dia(self, entidade: str, inicio: date, fim: date) -> dict[date, int]:
        consulta = (
            select(DIA_DO_LOG, func.count())
            .where(
                LogAuditoria.entidade == entidade,
                LogAuditoria.acao == AcaoAuditoria.create,
                DIA_DO_LOG >= inicio,
                DIA_DO_LOG <= fim,
            )
            .group_by(DIA_DO_LOG)
        )
        resultado = await self.db.execute(consulta)
        return montar_contagem(resultado.all())

    # join pq log antigo tem outro formato de json
    async def contar_alunos_por_dia(self, inicio: date, fim: date) -> dict[date, int]:
        consulta = (
            select(DIA_DO_LOG, func.count())
            .join(Usuario, Usuario.id == LogAuditoria.entidade_id)
            .where(
                LogAuditoria.entidade == "usuarios",
                LogAuditoria.acao == AcaoAuditoria.create,
                Usuario.role == RoleUsuario.aluno,
                DIA_DO_LOG >= inicio,
                DIA_DO_LOG <= fim,
            )
            .group_by(DIA_DO_LOG)
        )
        resultado = await self.db.execute(consulta)
        return montar_contagem(resultado.all())

    async def contar_dispositivos_por_dia(self, inicio: date, fim: date) -> dict[date, int]:
        dia = cast(func.timezone("America/Sao_Paulo", Dispositivo.criado_em), Date)
        consulta = (
            select(dia, func.count())
            .where(dia >= inicio, dia <= fim)
            .group_by(dia)
        )
        resultado = await self.db.execute(consulta)
        return montar_contagem(resultado.all())

    async def contar_conquistas_por_quantidade(self) -> list[tuple[int, str, int]]:
        quantidade = func.count(associacao_conquista_usuario.c.usuario_id)

        # esse resultado retorna até conquistas ainda não concedidas como 0. também ordena por mais obtidas primeiro.
        resultado = await self.db.execute(select(Conquista.id, Conquista.titulo, quantidade).outerjoin(associacao_conquista_usuario,
        associacao_conquista_usuario.c.conquista_id == Conquista.id).group_by(Conquista.id, Conquista.titulo).order_by(quantidade.desc(),
        Conquista.titulo, Conquista.id))

        return [(conquista_id, titulo, total) for conquista_id, titulo, total in resultado.all()]

    # pegando a data direto do postgres pra garantir que seja a mesma pra todos os cálculos.
    async def buscar_data_atual(self) -> date:
        return (await self.db.execute(select(cast(func.timezone("America/Sao_Paulo", func.now()), Date)))).scalar_one()