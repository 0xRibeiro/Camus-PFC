from fastcrud.exceptions.http_exceptions import ForbiddenException, NotFoundException
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.progresso.model import ConclusaoConteudo
from app.domains.progresso.repository import ProgressoRepository
from app.domains.progresso.schema import (
    AlternativaAlunoRead,
    ConteudoAlunoRead,
    ConteudoStatusRead,
    ModuloAlunoRead,
    QuestaoAlunoRead,
    TrilhaAlunoRead,
    TrilhaResumoRead,
)
from app.domains.trilha.model import Conteudo, ConteudoTipo, Modulo, Trilha
from app.domains.usuario.model import RoleUsuario, Usuario


###### regra de liberacao sequencial
# monta todos os conteudos da trilha na ordem do modulo e dps na ordem do conteudo
async def carregar_sequencia(
    repo: ProgressoRepository, trilha_id: int
) -> tuple[list[Modulo], list[Conteudo]]:
    modulos = await repo.listar_modulos([trilha_id])

    modulo_ids = []
    for modulo in modulos:
        modulo_ids.append(modulo.id)
    conteudos = await repo.listar_conteudos(modulo_ids)

    sequencia = []
    for modulo in modulos:
        for conteudo in conteudos:
            if conteudo.modulo_id == modulo.id:
                sequencia.append(conteudo)

    return modulos, sequencia


async def carregar_conclusoes(
    repo: ProgressoRepository, usuario: Usuario, sequencia: list[Conteudo]
) -> dict[int, ConclusaoConteudo]:
    conteudo_ids = []
    for conteudo in sequencia:
        conteudo_ids.append(conteudo.id)

    conclusoes = {}
    for conclusao in await repo.listar_conclusoes(usuario.id, conteudo_ids):
        conclusoes[conclusao.conteudo_id] = conclusao
    return conclusoes


# libera se ja concluiu ou se todos os anteriores foram concluidos
def calcular_status(
    sequencia: list[Conteudo], conclusoes: dict[int, ConclusaoConteudo]
) -> dict[int, ConteudoStatusRead]:
    status = {}
    anteriores_concluidos = True

    for conteudo in sequencia:
        conclusao = conclusoes.get(conteudo.id)
        concluido = conclusao is not None

        atualizado = False
        if conclusao is not None and conteudo.versao > conclusao.versao_conteudo:
            atualizado = True

        status[conteudo.id] = ConteudoStatusRead(
            id=conteudo.id,
            titulo=conteudo.titulo,
            tipo=conteudo.tipo,
            ordem=conteudo.ordem,
            pontos=conteudo.pontos,
            versao=conteudo.versao,
            concluido=concluido,
            liberado=concluido or anteriores_concluidos,
            atualizado=atualizado,
        )

        if not concluido:
            anteriores_concluidos = False

    return status


def calcular_porcentagem(concluidos: int, total: int) -> int:
    if total == 0:
        return 0
    return concluidos * 100 // total


def contar_concluidos(status: list[ConteudoStatusRead]) -> int:
    concluidos = 0
    for item in status:
        if item.concluido:
            concluidos += 1
    return concluidos


###### trilhas do aluno
# trilha inativa so staff enxerga pra testar
async def buscar_trilha_visivel(
    repo: ProgressoRepository, trilha_id: int, usuario: Usuario
) -> Trilha:
    trilha = await repo.buscar_trilha(trilha_id)

    if trilha is None:
        raise NotFoundException("Trilha não encontrada")
    if not trilha.is_active and usuario.role == RoleUsuario.aluno:
        raise NotFoundException("Trilha não encontrada")

    return trilha


async def listar_trilhas(db: AsyncSession, usuario: Usuario) -> list[TrilhaResumoRead]:
    repo = ProgressoRepository(db)
    resumos = []

    for trilha in await repo.listar_trilhas_ativas():
        modulos, sequencia = await carregar_sequencia(repo, trilha.id)
        conclusoes = await carregar_conclusoes(repo, usuario, sequencia)
        status = calcular_status(sequencia, conclusoes)

        concluidos = contar_concluidos(list(status.values()))
        total = len(sequencia)

        resumos.append(
            TrilhaResumoRead(
                id=trilha.id,
                titulo=trilha.titulo,
                descricao=trilha.descricao,
                foto=trilha.foto,
                tag=trilha.tag,
                concluidos=concluidos,
                total=total,
                progresso=calcular_porcentagem(concluidos, total),
            )
        )

    return resumos


async def buscar_trilha(
    db: AsyncSession, trilha_id: int, usuario: Usuario
) -> TrilhaAlunoRead:
    repo = ProgressoRepository(db)
    trilha = await buscar_trilha_visivel(repo, trilha_id, usuario)

    modulos, sequencia = await carregar_sequencia(repo, trilha.id)
    conclusoes = await carregar_conclusoes(repo, usuario, sequencia)
    status = calcular_status(sequencia, conclusoes)

    modulos_aluno = []
    for modulo in modulos:
        conteudos_do_modulo = []
        for conteudo in sequencia:
            if conteudo.modulo_id == modulo.id:
                conteudos_do_modulo.append(status[conteudo.id])

        modulos_aluno.append(
            ModuloAlunoRead(
                id=modulo.id,
                titulo=modulo.titulo,
                ordem=modulo.ordem,
                concluidos=contar_concluidos(conteudos_do_modulo),
                total=len(conteudos_do_modulo),
                conteudos=conteudos_do_modulo,
            )
        )

    concluidos = contar_concluidos(list(status.values()))
    total = len(sequencia)

    return TrilhaAlunoRead(
        id=trilha.id,
        titulo=trilha.titulo,
        descricao=trilha.descricao,
        foto=trilha.foto,
        tag=trilha.tag,
        concluidos=concluidos,
        total=total,
        progresso=calcular_porcentagem(concluidos, total),
        modulos=modulos_aluno,
    )


###### conteudo aberto pelo aluno
# acha o conteudo e barra se ainda ta bloqueado, serve pra abrir concluir e responder
async def buscar_conteudo_liberado(
    repo: ProgressoRepository, conteudo_id: int, usuario: Usuario
) -> tuple[Conteudo, list[Conteudo], ConclusaoConteudo | None]:
    conteudo = await repo.buscar_conteudo(conteudo_id)
    if conteudo is None:
        raise NotFoundException("Conteúdo não encontrado")

    modulo = await repo.buscar_modulo(conteudo.modulo_id)
    if modulo is None:
        raise NotFoundException("Conteúdo não encontrado")
    await buscar_trilha_visivel(repo, modulo.trilha_id, usuario)

    modulos, sequencia = await carregar_sequencia(repo, modulo.trilha_id)
    conclusoes = await carregar_conclusoes(repo, usuario, sequencia)
    status = calcular_status(sequencia, conclusoes)

    if not status[conteudo.id].liberado:
        raise ForbiddenException("Conclua os conteúdos anteriores primeiro")

    return conteudo, sequencia, conclusoes.get(conteudo.id)


def buscar_proximo_id(sequencia: list[Conteudo], conteudo_id: int) -> int | None:
    for indice in range(len(sequencia) - 1):
        if sequencia[indice].id == conteudo_id:
            return sequencia[indice + 1].id
    return None


# monta as questoes com as alternativas de cada uma sem o campo correta
async def montar_questoes_aluno(
    repo: ProgressoRepository, conteudo_id: int
) -> list[QuestaoAlunoRead]:
    questoes = await repo.listar_questoes(conteudo_id)

    questao_ids = []
    for questao in questoes:
        questao_ids.append(questao.id)
    alternativas = await repo.listar_alternativas(questao_ids)

    questoes_aluno = []
    for questao in questoes:
        alternativas_da_questao = []
        for alternativa in alternativas:
            if alternativa.questao_id == questao.id:
                alternativas_da_questao.append(
                    AlternativaAlunoRead(id=alternativa.id, texto=alternativa.texto)
                )

        questoes_aluno.append(
            QuestaoAlunoRead(
                id=questao.id,
                ordem=questao.ordem,
                enunciado=questao.enunciado,
                alternativas=alternativas_da_questao,
            )
        )

    return questoes_aluno


async def buscar_conteudo(
    db: AsyncSession, conteudo_id: int, usuario: Usuario
) -> ConteudoAlunoRead:
    repo = ProgressoRepository(db)
    conteudo, sequencia, conclusao = await buscar_conteudo_liberado(
        repo, conteudo_id, usuario
    )

    questoes = []
    if conteudo.tipo == ConteudoTipo.quiz:
        questoes = await montar_questoes_aluno(repo, conteudo.id)

    atualizado = False
    if conclusao is not None and conteudo.versao > conclusao.versao_conteudo:
        atualizado = True

    return ConteudoAlunoRead(
        id=conteudo.id,
        modulo_id=conteudo.modulo_id,
        titulo=conteudo.titulo,
        tipo=conteudo.tipo,
        pontos=conteudo.pontos,
        versao=conteudo.versao,
        video_url=conteudo.video_url,
        artigo_conteudo=conteudo.artigo_conteudo,
        questoes=questoes,
        concluido=conclusao is not None,
        atualizado=atualizado,
        proximo_conteudo_id=buscar_proximo_id(sequencia, conteudo.id),
    )
