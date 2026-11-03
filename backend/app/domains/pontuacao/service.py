from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.pontuacao.model import LancamentoPontos, OrigemLancamento
from app.domains.pontuacao.repository import PontuacaoRepository
from app.domains.pontuacao.schema import XpRead
from app.domains.usuario.model import RoleUsuario, Usuario


async def registrar_lancamento(
    db: AsyncSession,
    usuario: Usuario,
    origem_tipo: OrigemLancamento,
    origem_id: int,
    pontos: int,
    versao: int = 1,
    grupo_id: int | None = None,
) -> LancamentoPontos | None:
    # so aluno ganha xp e n tem lancamento de 0
    if usuario.role != RoleUsuario.aluno or pontos <= 0:
        return None

    repo = PontuacaoRepository(db)
    lancamento = LancamentoPontos(
        usuario_id=usuario.id,
        origem_tipo=origem_tipo,
        origem_id=origem_id,
        versao=versao,
        pontos=pontos,
        grupo_id=grupo_id,
    )

    # o unique bloqueia pagar 2x a msm versao se chegar 2 requisicao junto
    try:
        return await repo.salvar(lancamento)
    except IntegrityError:
        await repo.desfazer()
        return None


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
    total = await PontuacaoRepository(db).somar_global(usuario.id)
    return XpRead(xp_total=total)


async def meu_extrato(db: AsyncSession, usuario: Usuario) -> list[LancamentoPontos]:
    return await PontuacaoRepository(db).listar_do_usuario(usuario.id)
