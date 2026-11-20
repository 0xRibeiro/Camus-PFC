from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.pontuacao.model import LancamentoPontos, OrigemLancamento
from app.domains.pontuacao.repository import PontuacaoRepository
from app.domains.pontuacao.schema import LancamentoRead, RankingItemRead, XpDiaRead, XpRead
from app.domains.usuario.model import RoleUsuario, Usuario

FUSO = ZoneInfo("America/Sao_Paulo")


def registrar_lancamento(db: AsyncSession, usuario: Usuario, origem_tipo: OrigemLancamento, origem_id: int, pontos: int,  versao: int = 1, grupo_id: int | None = None) -> LancamentoPontos | None:
    # XP global é só para alunos. No grupo, qualquer membro pode ganhar XP.
    # se tiver com zero pontos é ignorado.
    if pontos <= 0 or (grupo_id is None and usuario.role != RoleUsuario.aluno):
        return None

    lancamento = LancamentoPontos(usuario_id=usuario.id, origem_tipo=origem_tipo, origem_id=origem_id, versao=versao, pontos=pontos, grupo_id=grupo_id)

    PontuacaoRepository(db).adicionar(lancamento)
    return lancamento


async def total_ganho_na_origem(
    db: AsyncSession,
    usuario: Usuario,
    origem_tipo: OrigemLancamento,
    origem_id: int,
) -> int:
    return await PontuacaoRepository(db).somar_por_origem(
        usuario.id, origem_tipo, origem_id
    )


async def meu_xp(db: AsyncSession, usuario: Usuario) -> XpRead:
    repo = PontuacaoRepository(db)
    grupo_id = db.info.get("grupo_id")
    total = await repo.somar_xp(usuario.id, grupo_id)

    # quem tem 0 nem aparece no ranking
    posicao = None
    if grupo_id is None and usuario.role == RoleUsuario.aluno and total > 0:
        posicao = await repo.contar_na_frente(usuario, total) + 1
    return XpRead(xp_total=total, posicao=posicao)


# xp ganho em cada dia ate hoje, dia sem nada volta 0 pro grafico n pular
async def meu_xp_por_dia(db: AsyncSession, usuario: Usuario, dias: int) -> list[XpDiaRead]:
    hoje = datetime.now(FUSO).date()
    inicio = hoje - timedelta(days=dias - 1)
    pontos = await PontuacaoRepository(db).somar_por_dia(usuario.id, db.info.get("grupo_id"), inicio)

    lista = []
    for indice in range(dias):
        dia = inicio + timedelta(days=indice)
        lista.append(XpDiaRead(data=dia, pontos=pontos.get(dia, 0)))
    return lista


LIMITE_RANKING = 50


async def ranking(db: AsyncSession) -> list[RankingItemRead]:
    linhas = await PontuacaoRepository(db).listar_ranking(LIMITE_RANKING)

    itens = []
    posicao = 1
    for usuario, xp in linhas:
        itens.append(RankingItemRead(
            posicao=posicao,
            usuario_id=usuario.id,
            username=usuario.username,
            avatar=usuario.avatar,
            cor_fundo=usuario.cor_fundo,
            xp_total=xp,
        ))
        posicao += 1
    return itens


async def meu_extrato(db: AsyncSession, usuario: Usuario) -> list[LancamentoRead]:
    repo = PontuacaoRepository(db)
    lancamentos = await repo.listar_do_usuario(usuario.id, db.info.get("grupo_id"))

    # junta os ids pra buscar todos os titulos numa query so
    conteudo_ids = []
    rodada_ids = []
    for lancamento in lancamentos:
        if lancamento.origem_tipo == OrigemLancamento.conteudo:
            conteudo_ids.append(lancamento.origem_id)
        elif lancamento.origem_tipo == OrigemLancamento.minigame:
            rodada_ids.append(lancamento.origem_id)
    titulos = await repo.listar_titulos_conteudos(conteudo_ids)
    titulos_minigames = await repo.listar_titulos_minigames(rodada_ids)

    extrato = []
    for lancamento in lancamentos:
        item = LancamentoRead.model_validate(lancamento)
        if lancamento.origem_tipo == OrigemLancamento.conteudo:
            item.titulo = titulos.get(lancamento.origem_id)
        elif lancamento.origem_tipo == OrigemLancamento.minigame:
            item.titulo = titulos_minigames.get(lancamento.origem_id)
        extrato.append(item)
    return extrato