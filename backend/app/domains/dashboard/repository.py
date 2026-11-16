from datetime import date

from sqlalchemy import Date, cast, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.auditoria.model import AcaoAuditoria, LogAuditoria
from app.domains.conquistas.model import Conquista, associacao_conquista_usuario
from app.domains.dispositivo.model import Dispositivo
from app.domains.grupo.model import Grupo, Participacao
from app.domains.progresso.model import ConclusaoConteudo, TentativaQuiz
from app.domains.trilha.model import Alternativa, Conteudo, Modulo, Questao, Trilha
from app.domains.usuario.model import RoleUsuario, Usuario

# dia no fuso de sp, o log fica sem fuso
DIA_DO_LOG = cast(func.timezone("America/Sao_Paulo", func.timezone("UTC", LogAuditoria.criado_em)), Date)
DIA_DA_CONCLUSAO = cast(func.timezone("America/Sao_Paulo", ConclusaoConteudo.concluido_em), Date)
DIA_DA_TENTATIVA = cast(func.timezone("America/Sao_Paulo", TentativaQuiz.criado_em), Date)


# chave pode ser dia, conteudo ou aluno
def montar_contagem(linhas) -> dict:
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

    async def contar_conquistas_por_quantidade(self) -> list[tuple[int, str, str, int]]:
        quantidade = func.count(associacao_conquista_usuario.c.usuario_id)

        # esse resultado retorna até conquistas ainda não concedidas como 0. também ordena por mais obtidas primeiro.
        resultado = await self.db.execute(select(Conquista.id, Conquista.titulo, Conquista.imagem_dir, quantidade)
        .outerjoin(associacao_conquista_usuario, associacao_conquista_usuario.c.conquista_id == Conquista.id)
        .group_by(Conquista.id).order_by(quantidade.desc(), Conquista.titulo, Conquista.id))

        return list(resultado.tuples().all())

    # conta deletado tbm, a conquista dele continua
    async def contar_alunos(self) -> int:
        consulta = select(func.count()).select_from(Usuario).where(Usuario.role == RoleUsuario.aluno)
        return await self.db.scalar(consulta) or 0

    # conclusao e tentativa n tem FK, entao filtra pelos conteudos atuais da trilha
    # na ordem q o aluno ve
    async def listar_conteudos_da_trilha(self, trilha_id: int) -> list[tuple[Conteudo, str]]:
        consulta = (
            select(Conteudo, Modulo.titulo)
            .join(Modulo, Modulo.id == Conteudo.modulo_id)
            .where(Modulo.trilha_id == trilha_id)
            .order_by(Modulo.ordem, Conteudo.ordem)
        )
        resultado = await self.db.execute(consulta)
        return list(resultado.tuples().all())

    async def contar_conclusoes_por_conteudo(self, conteudos: list[int]) -> dict[int, int]:
        consulta = (
            select(ConclusaoConteudo.conteudo_id, func.count())
            .where(ConclusaoConteudo.conteudo_id.in_(conteudos))
            .group_by(ConclusaoConteudo.conteudo_id)
        )
        resultado = await self.db.execute(consulta)
        return montar_contagem(resultado.all())

    # por aluno quantos concluiu, o 1o dia e o ultimo
    async def listar_progresso_por_aluno(self, conteudos: list[int]) -> list[tuple[int, int, date, date]]:
        consulta = (
            select(
                ConclusaoConteudo.usuario_id,
                func.count(),
                func.min(DIA_DA_CONCLUSAO),
                func.max(DIA_DA_CONCLUSAO),
            )
            .where(ConclusaoConteudo.conteudo_id.in_(conteudos))
            .group_by(ConclusaoConteudo.usuario_id)
        )
        resultado = await self.db.execute(consulta)
        return list(resultado.tuples().all())

    async def listar_questoes(self, quizzes: list[int]) -> list[Questao]:
        consulta = select(Questao).where(Questao.conteudo_id.in_(quizzes)).order_by(Questao.conteudo_id, Questao.ordem)
        resultado = await self.db.scalars(consulta)
        return list(resultado.all())

    async def listar_alternativas_corretas(self, questoes: list[int]) -> set[int]:
        consulta = select(Alternativa.id).where(Alternativa.questao_id.in_(questoes), Alternativa.correta.is_(True))
        resultado = await self.db.scalars(consulta)
        return set(resultado.all())

    # so a versao atual, a antiga pode ter outras alternativas
    async def listar_respostas(self, conteudo_id: int, versao: int) -> list[dict]:
        consulta = select(TentativaQuiz.respostas).where(
            TentativaQuiz.conteudo_id == conteudo_id,
            TentativaQuiz.versao_conteudo == versao,
        )
        resultado = await self.db.scalars(consulta)
        return list(resultado.all())

    async def buscar_trilha(self, trilha_id: int) -> Trilha | None:
        return await self.db.get(Trilha, trilha_id)

    # dono fica de fora, ele so cria
    async def contar_membros(self, grupo_id: int) -> int:
        consulta = (
            select(func.count())
            .select_from(Participacao)
            .join(Grupo, Grupo.id == Participacao.id_grupo)
            .where(Participacao.id_grupo == grupo_id, Participacao.id_usuario != Grupo.id_dono)
        )
        return await self.db.scalar(consulta) or 0

    async def contar_conclusoes_por_dia(self, conteudos: list[int], inicio: date, fim: date) -> dict[date, int]:
        consulta = (
            select(DIA_DA_CONCLUSAO, func.count())
            .where(
                ConclusaoConteudo.conteudo_id.in_(conteudos),
                DIA_DA_CONCLUSAO >= inicio,
                DIA_DA_CONCLUSAO <= fim,
            )
            .group_by(DIA_DA_CONCLUSAO)
        )
        resultado = await self.db.execute(consulta)
        return montar_contagem(resultado.all())

    async def contar_tentativas_por_dia(self, conteudos: list[int], inicio: date, fim: date) -> dict[date, int]:
        consulta = (
            select(DIA_DA_TENTATIVA, func.count())
            .where(
                TentativaQuiz.conteudo_id.in_(conteudos),
                DIA_DA_TENTATIVA >= inicio,
                DIA_DA_TENTATIVA <= fim,
            )
            .group_by(DIA_DA_TENTATIVA)
        )
        resultado = await self.db.execute(consulta)
        return montar_contagem(resultado.all())

    # quem concluiu ou tentou algo no periodo
    async def listar_alunos_ativos(self, conteudos: list[int], inicio: date, fim: date) -> set[int]:
        concluiram = await self.db.scalars(
            select(ConclusaoConteudo.usuario_id).distinct().where(
                ConclusaoConteudo.conteudo_id.in_(conteudos),
                DIA_DA_CONCLUSAO >= inicio,
                DIA_DA_CONCLUSAO <= fim,
            )
        )
        tentaram = await self.db.scalars(
            select(TentativaQuiz.usuario_id).distinct().where(
                TentativaQuiz.conteudo_id.in_(conteudos),
                DIA_DA_TENTATIVA >= inicio,
                DIA_DA_TENTATIVA <= fim,
            )
        )
        return set(concluiram.all()) | set(tentaram.all())

    # soma de acertos e questoes das tentativas
    async def somar_acertos(self, conteudos: list[int], inicio: date, fim: date) -> tuple[int, int]:
        consulta = select(func.sum(TentativaQuiz.acertos), func.sum(TentativaQuiz.total)).where(
            TentativaQuiz.conteudo_id.in_(conteudos),
            DIA_DA_TENTATIVA >= inicio,
            DIA_DA_TENTATIVA <= fim,
        )
        acertos, total = (await self.db.execute(consulta)).one()
        if acertos is None:
            return 0, 0
        return acertos, total

    # pegando a data direto do postgres pra garantir que seja a mesma pra todos os cálculos.
    async def buscar_data_atual(self) -> date:
        return (await self.db.execute(select(cast(func.timezone("America/Sao_Paulo", func.now()), Date)))).scalar_one()