from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.pontuacao.model import LancamentoPontos, OrigemLancamento
from app.domains.pontuacao.repository import PontuacaoRepository
from app.domains.pontuacao.schema import LancamentoRead, XpRead
from app.domains.usuario.model import RoleUsuario, Usuario


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
    total = await PontuacaoRepository(db).somar_xp(usuario.id, db.info.get("grupo_id"))
    return XpRead(xp_total=total)


async def meu_extrato(db: AsyncSession, usuario: Usuario) -> list[LancamentoRead]:
    repo = PontuacaoRepository(db)
    lancamentos = await repo.listar_do_usuario(usuario.id, db.info.get("grupo_id"))

    # junta os ids pra buscar todos os titulos numa query so
    conteudo_ids = []
    for lancamento in lancamentos:
        if lancamento.origem_tipo == OrigemLancamento.conteudo:
            conteudo_ids.append(lancamento.origem_id)
    titulos = await repo.listar_titulos_conteudos(conteudo_ids)

    extrato = []
    for lancamento in lancamentos:
        item = LancamentoRead.model_validate(lancamento)
        if lancamento.origem_tipo == OrigemLancamento.conteudo:
            item.titulo = titulos.get(lancamento.origem_id)
        extrato.append(item)
    return extrato