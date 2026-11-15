import random
from datetime import datetime, timezone

import httpx
from fastapi import HTTPException
from fastcrud.exceptions.http_exceptions import BadRequestException, NotFoundException
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.minigame import inat
from app.domains.minigame.model import JOGO_QUEM_E_ESSE_PEIXE, RodadaMinigame
from app.domains.minigame.repository import MinigameRepository
from app.domains.minigame.schema import ResultadoRead, RodadaRead
from app.domains.pontuacao.model import OrigemLancamento
from app.domains.pontuacao.service import registrar_lancamento
from app.domains.usuario.model import Usuario

XP_POR_ACERTO = 5
# dps disso continua jogando mas sem xp, se n da pra farmar no chute
LIMITE_ACERTOS_COM_XP = 20
ERRO_INAT = "Não foi possível carregar o minigame, tente de novo"


# tem especie sem foto livre, tenta outra
async def sortear_certa_com_foto(especies: list[dict]) -> tuple[dict, dict]:
    for tentativa in range(5):
        certa = random.choice(especies)
        foto = await inat.sortear_foto(certa["taxon_id"])
        if foto is not None:
            return certa, foto
    raise HTTPException(status_code=503, detail=ERRO_INAT)


# erradas do msm grupo da certa, se o grupo for pequeno completa com outros
def sortear_opcoes(especies: list[dict], certa: dict) -> list[dict]:
    mesmo_grupo = []
    outros = []
    for especie in especies:
        if especie["grupo"] == certa["grupo"]:
            mesmo_grupo.append(especie)
        else:
            outros.append(especie)
    random.shuffle(mesmo_grupo)
    random.shuffle(outros)

    escolhidas = [certa]
    # especie diferente c msm nome popular deixaria 2 opcoes iguais
    nomes = {certa["nome"]}
    for especie in mesmo_grupo + outros:
        if len(escolhidas) == 4:
            break
        if especie["nome"] in nomes:
            continue
        escolhidas.append(especie)
        nomes.add(especie["nome"])
    random.shuffle(escolhidas)

    opcoes = []
    for especie in escolhidas:
        opcoes.append({"taxon_id": especie["taxon_id"], "nome": especie["nome"]})
    return opcoes


async def nova_rodada(db: AsyncSession, usuario: Usuario) -> RodadaRead:
    try:
        especies = await inat.listar_especies()
        certa, foto = await sortear_certa_com_foto(especies)
    except httpx.HTTPError:
        raise HTTPException(status_code=503, detail=ERRO_INAT)

    repo = MinigameRepository(db)
    rodada = RodadaMinigame(
        usuario_id=usuario.id,
        jogo=JOGO_QUEM_E_ESSE_PEIXE,
        resposta_taxon_id=certa["taxon_id"],
        resposta_nome_cientifico=certa["nome_cientifico"],
        opcoes=sortear_opcoes(especies, certa),
        foto_url=foto["url"],
    )
    repo.adicionar(rodada)
    await repo.salvar(rodada)

    return RodadaRead(
        id=rodada.id,
        foto_url=rodada.foto_url,
        foto_atribuicao=foto["atribuicao"],
        opcoes=rodada.opcoes,
        acertos_com_xp_hoje=await repo.contar_acertos_com_xp_hoje(usuario.id),
        limite_acertos_com_xp=LIMITE_ACERTOS_COM_XP,
    )


async def responder(db: AsyncSession, usuario: Usuario, rodada_id: int, taxon_id: int) -> ResultadoRead:
    repo = MinigameRepository(db)
    rodada = await repo.buscar_rodada(rodada_id, usuario.id)
    if rodada is None:
        raise NotFoundException("Rodada não encontrada")
    if rodada.acertou is not None:
        raise BadRequestException("Essa rodada já foi respondida")

    nome_certa = None
    escolheu_opcao = False
    for opcao in rodada.opcoes:
        if opcao["taxon_id"] == rodada.resposta_taxon_id:
            nome_certa = opcao["nome"]
        if opcao["taxon_id"] == taxon_id:
            escolheu_opcao = True
    if not escolheu_opcao:
        raise BadRequestException("Opção inválida")

    rodada.acertou = taxon_id == rodada.resposta_taxon_id
    rodada.respondida_em = datetime.now(timezone.utc)

    acertos = await repo.contar_acertos_com_xp_hoje(usuario.id)
    if rodada.acertou and acertos < LIMITE_ACERTOS_COM_XP:
        # o unique do lancamento segura pagar 2x a msm rodada
        lancamento = registrar_lancamento(db, usuario, OrigemLancamento.minigame, rodada.id, XP_POR_ACERTO)
        if lancamento is not None:
            rodada.pontos = lancamento.pontos
            acertos += 1

    await repo.salvar(rodada)

    return ResultadoRead(
        acertou=rodada.acertou,
        resposta_taxon_id=rodada.resposta_taxon_id,
        resposta_nome=nome_certa,
        resposta_nome_cientifico=rodada.resposta_nome_cientifico,
        pontos=rodada.pontos,
        acertos_com_xp_hoje=acertos,
        limite_acertos_com_xp=LIMITE_ACERTOS_COM_XP,
    )
