from datetime import date, datetime

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
        # na trilha de grupo o dono pode fazer os conteudos, mas n entra nos graficos
        self.dono = db.info.get("grupo_dono")

    # no grupo tira o dono, na global so conta aluno (author e admin ficam de fora)
    def so_alunos(self, consulta, coluna):
        if self.dono is not None:
            return consulta.where(coluna != self.dono)
        alunos = select(Usuario.id).where(Usuario.role == RoleUsuario.aluno)
        return consulta.where(coluna.in_(alunos))

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
        consulta = self.so_alunos(consulta, ConclusaoConteudo.usuario_id)
        resultado = await self.db.execute(consulta)
        return montar_contagem(resultado.all())

    # por aluno quantos concluiu, a 1a e a ultima conclusao com hora (pro tempo ate terminar)
    async def listar_progresso_por_aluno(self, conteudos: list[int]) -> list[tuple[int, int, datetime, datetime]]:
        consulta = (
            select(
                ConclusaoConteudo.usuario_id,
                func.count(),
                func.min(ConclusaoConteudo.concluido_em),
                func.max(ConclusaoConteudo.concluido_em),
            )
            .where(ConclusaoConteudo.conteudo_id.in_(conteudos))
            .group_by(ConclusaoConteudo.usuario_id)
        )
        consulta = self.so_alunos(consulta, ConclusaoConteudo.usuario_id)
        resultado = await self.db.execute(consulta)
        return list(resultado.tuples().all())

    # 1 por aluno e versao, o service separa a versao atual
    async def listar_tentativas_dos_quizzes(self, quizzes: list[int]) -> list[TentativaQuiz]:
        consulta = select(TentativaQuiz).where(TentativaQuiz.conteudo_id.in_(quizzes))
        consulta = self.so_alunos(consulta, TentativaQuiz.usuario_id)
        resultado = await self.db.scalars(consulta)
        return list(resultado.all())

    async def listar_questoes(self, quizzes: list[int]) -> list[Questao]:
        consulta = select(Questao).where(Questao.conteudo_id.in_(quizzes)).order_by(Questao.conteudo_id, Questao.ordem)
        resultado = await self.db.scalars(consulta)
        return list(resultado.all())

    async def listar_alternativas(self, questoes: list[int]) -> list[Alternativa]:
        consulta = select(Alternativa).where(Alternativa.questao_id.in_(questoes)).order_by(Alternativa.id)
        resultado = await self.db.scalars(consulta)
        return list(resultado.all())

    # so a versao atual, a antiga pode ter outras alternativas
    async def listar_tentativas_da_versao(self, conteudo_id: int, versao: int) -> list[TentativaQuiz]:
        consulta = select(TentativaQuiz).where(
            TentativaQuiz.conteudo_id == conteudo_id,
            TentativaQuiz.versao_conteudo == versao,
        )
        consulta = self.so_alunos(consulta, TentativaQuiz.usuario_id)
        resultado = await self.db.scalars(consulta)
        return list(resultado.all())

    # trilha vem junto pro funil e o voltar
    async def buscar_conteudo(self, conteudo_id: int) -> tuple[Conteudo, int] | None:
        consulta = select(Conteudo, Modulo.trilha_id).join(Modulo, Modulo.id == Conteudo.modulo_id).where(Conteudo.id == conteudo_id)
        resultado = await self.db.execute(consulta)
        return resultado.tuples().one_or_none()

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

    # membros sem o dono, ele so cria
    async def listar_membros(self, grupo_id: int) -> list[Usuario]:
        consulta = (
            select(Usuario)
            .join(Participacao, Participacao.id_usuario == Usuario.id)
            .join(Grupo, Grupo.id == Participacao.id_grupo)
            .where(Participacao.id_grupo == grupo_id, Participacao.id_usuario != Grupo.id_dono)
            .order_by(Usuario.username)
        )
        resultado = await self.db.scalars(consulta)
        return list(resultado.all())

    async def buscar_membro(self, grupo_id: int, usuario_id: int) -> Usuario | None:
        consulta = (
            select(Usuario)
            .join(Participacao, Participacao.id_usuario == Usuario.id)
            .join(Grupo, Grupo.id == Participacao.id_grupo)
            .where(
                Participacao.id_grupo == grupo_id,
                Participacao.id_usuario == usuario_id,
                Participacao.id_usuario != Grupo.id_dono,
            )
        )
        return await self.db.scalar(consulta)

    async def listar_conclusoes_do_aluno(self, usuario_id: int, conteudos: list[int]) -> list[ConclusaoConteudo]:
        consulta = select(ConclusaoConteudo).where(
            ConclusaoConteudo.usuario_id == usuario_id,
            ConclusaoConteudo.conteudo_id.in_(conteudos),
        )
        resultado = await self.db.scalars(consulta)
        return list(resultado.all())

    # 1 por versao, o service escolhe qual mostrar
    async def listar_tentativas_do_aluno(self, usuario_id: int, quizzes: list[int]) -> list[TentativaQuiz]:
        consulta = select(TentativaQuiz).where(
            TentativaQuiz.usuario_id == usuario_id,
            TentativaQuiz.conteudo_id.in_(quizzes),
        )
        resultado = await self.db.scalars(consulta)
        return list(resultado.all())

    # quem concluiu ou tentou algo no periodo
    async def listar_alunos_ativos(self, conteudos: list[int], inicio: date, fim: date) -> set[int]:
        concluiram = await self.db.scalars(self.so_alunos(
            select(ConclusaoConteudo.usuario_id).distinct().where(
                ConclusaoConteudo.conteudo_id.in_(conteudos),
                DIA_DA_CONCLUSAO >= inicio,
                DIA_DA_CONCLUSAO <= fim,
            ),
            ConclusaoConteudo.usuario_id,
        ))
        tentaram = await self.db.scalars(self.so_alunos(
            select(TentativaQuiz.usuario_id).distinct().where(
                TentativaQuiz.conteudo_id.in_(conteudos),
                DIA_DA_TENTATIVA >= inicio,
                DIA_DA_TENTATIVA <= fim,
            ),
            TentativaQuiz.usuario_id,
        ))
        return set(concluiram.all()) | set(tentaram.all())

    # cada dia q o aluno concluiu ou tentou algo, sem repetir
    async def listar_dias_de_atividade(self, conteudos: list[int], inicio: date,
        fim: date) -> set[tuple[int, date]]:
        concluiram = await self.db.execute(self.so_alunos(
            select(ConclusaoConteudo.usuario_id, DIA_DA_CONCLUSAO).distinct().where(
                ConclusaoConteudo.conteudo_id.in_(conteudos),
                DIA_DA_CONCLUSAO >= inicio,
                DIA_DA_CONCLUSAO <= fim,
            ),
            ConclusaoConteudo.usuario_id,
        ))
        tentaram = await self.db.execute(self.so_alunos(
            select(TentativaQuiz.usuario_id, DIA_DA_TENTATIVA).distinct().where(
                TentativaQuiz.conteudo_id.in_(conteudos),
                DIA_DA_TENTATIVA >= inicio,
                DIA_DA_TENTATIVA <= fim,
            ),
            TentativaQuiz.usuario_id,
        ))
        return set(concluiram.tuples().all()) | set(tentaram.tuples().all())

    # dia em q a entidade foi criada, pela auditoria. None se n tiver log
    async def buscar_dia_de_criacao(self, entidade: str, entidade_id: int) -> date | None:
        consulta = select(func.min(DIA_DO_LOG)).where(
            LogAuditoria.entidade == entidade,
            LogAuditoria.entidade_id == entidade_id,
            LogAuditoria.acao == AcaoAuditoria.create,
        )
        return await self.db.scalar(consulta)

    # dia do update q mudou a versao do conteudo pra essa
    async def buscar_dia_da_versao(self, conteudo_id: int, versao: int) -> date | None:
        consulta = select(func.min(DIA_DO_LOG)).where(
            LogAuditoria.entidade == "conteudos",
            LogAuditoria.entidade_id == conteudo_id,
            LogAuditoria.acao == AcaoAuditoria.update,
            LogAuditoria.alteracoes["novo"]["versao"].astext == str(versao),
            LogAuditoria.alteracoes["antigo"]["versao"].astext != str(versao),
        )
        return await self.db.scalar(consulta)

    # 1o registro do sistema, é o comeco do todo o periodo no admin
    async def buscar_primeiro_dia(self) -> date | None:
        return await self.db.scalar(select(func.min(DIA_DO_LOG)))

    # pegando a data direto do postgres pra garantir que seja a mesma pra todos os cálculos.
    async def buscar_data_atual(self) -> date:
        return (await self.db.execute(select(cast(func.timezone("America/Sao_Paulo", func.now()), Date)))).scalar_one()