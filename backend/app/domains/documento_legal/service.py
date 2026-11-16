from datetime import datetime, timezone

from fastapi import HTTPException, status
from fastcrud.exceptions.http_exceptions import BadRequestException, NotFoundException
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.documento_legal.model import AceiteDocumentoLegal, DocumentoLegal, TipoDocumentoLegal
from app.domains.documento_legal.repository import DocumentoLegalRepository
from app.domains.documento_legal.schema import (
    AceiteCreate,
    AceiteStatus,
    DocumentoLegalResumo,
    DocumentoPendente,
    RascunhoCreate,
    RascunhoUpdate,
)
from app.domains.usuario.model import Usuario


###### publico

async def buscar_atual(db: AsyncSession, tipo: TipoDocumentoLegal) -> DocumentoLegal:
    documento = await DocumentoLegalRepository(db).buscar_atual(tipo)
    if documento is None:
        raise NotFoundException("Documento ainda não publicado")
    return documento


async def buscar_publicada(db: AsyncSession, tipo: TipoDocumentoLegal, versao: int) -> DocumentoLegal:
    documento = await DocumentoLegalRepository(db).buscar_publicada(tipo, versao)
    if documento is None:
        raise NotFoundException("Versão não encontrada")
    return documento


async def listar_historico(db: AsyncSession, tipo: TipoDocumentoLegal) -> list[DocumentoLegal]:
    return await DocumentoLegalRepository(db).listar_publicadas(tipo)


###### aceite

async def listar_atuais(db: AsyncSession) -> list[DocumentoLegal]:
    repo = DocumentoLegalRepository(db)

    atuais = []
    for tipo in TipoDocumentoLegal:
        atual = await repo.buscar_atual(tipo)
        if atual is not None:
            atuais.append(atual)
    return atuais


# pendente e a atual q ele n aceitou
async def documentos_pendentes(db: AsyncSession, usuario_id: int) -> list[DocumentoLegal]:
    repo = DocumentoLegalRepository(db)

    pendentes = []
    for atual in await listar_atuais(db):
        if not await repo.aceitou(usuario_id, atual.id):
            pendentes.append(atual)
    return pendentes


def montar_status(pendentes: list[DocumentoLegal]) -> AceiteStatus:
    itens = []
    for documento in pendentes:
        itens.append(DocumentoPendente.model_validate(documento))
    return AceiteStatus(aceitou=len(pendentes) == 0, pendentes=itens)


async def status_aceite(db: AsyncSession, usuario: Usuario) -> AceiteStatus:
    return montar_status(await documentos_pendentes(db, usuario.id))


async def aceitar_documentos(db: AsyncSession, usuario: Usuario, data: AceiteCreate) -> AceiteStatus:
    pendentes = await documentos_pendentes(db, usuario.id)

    # clique duplo
    if len(pendentes) == 0:
        return montar_status(pendentes)

    ids_pendentes = set()
    for documento in pendentes:
        ids_pendentes.add(documento.id)

    # saiu versao nova com a tela aberta
    if set(data.documento_ids) != ids_pendentes:
        raise HTTPException(status.HTTP_409_CONFLICT, "Os termos foram atualizados, recarregue a página")

    aceites = []
    for documento in pendentes:
        aceites.append(AceiteDocumentoLegal(usuario_id=usuario.id, documento_id=documento.id))
    await DocumentoLegalRepository(db).registrar_aceites(aceites)

    return montar_status([])


###### admin

async def listar_documentos(db: AsyncSession, tipo: TipoDocumentoLegal | None) -> list[DocumentoLegalResumo]:
    return await DocumentoLegalRepository(db).listar(tipo)


async def buscar_documento(db: AsyncSession, documento_id: int) -> DocumentoLegal:
    documento = await DocumentoLegalRepository(db).buscar(documento_id)
    if documento is None:
        raise NotFoundException("Documento não encontrado")
    return documento


# um rascunho por tipo
async def criar_rascunho(db: AsyncSession, data: RascunhoCreate, admin: Usuario) -> DocumentoLegal:
    repo = DocumentoLegalRepository(db)

    if await repo.buscar_rascunho(data.tipo) is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, "Já existe um rascunho desse documento")

    maior = await repo.maior_versao(data.tipo)
    versao = 1
    if maior is not None:
        versao = maior + 1

    documento = DocumentoLegal(
        tipo=data.tipo,
        versao=versao,
        conteudo=data.conteudo,
        criado_por=admin.id,
    )
    return await repo.criar(documento)


# publicada n muda
async def buscar_rascunho_por_id(db: AsyncSession, documento_id: int) -> DocumentoLegal:
    documento = await buscar_documento(db, documento_id)
    if documento.publicado_em is not None:
        raise BadRequestException("Versão publicada não pode ser alterada")
    return documento


async def editar_rascunho(db: AsyncSession, documento_id: int, data: RascunhoUpdate) -> DocumentoLegal:
    documento = await buscar_rascunho_por_id(db, documento_id)
    documento.conteudo = data.conteudo
    return await DocumentoLegalRepository(db).salvar(documento)


async def publicar_rascunho(db: AsyncSession, documento_id: int) -> DocumentoLegal:
    documento = await buscar_rascunho_por_id(db, documento_id)
    documento.publicado_em = datetime.now(timezone.utc)
    return await DocumentoLegalRepository(db).salvar(documento)


async def descartar_rascunho(db: AsyncSession, documento_id: int) -> None:
    documento = await buscar_rascunho_por_id(db, documento_id)
    await DocumentoLegalRepository(db).apagar(documento)
