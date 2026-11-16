from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.domains.documento_legal import service
from app.domains.documento_legal.model import DocumentoLegal, TipoDocumentoLegal
from app.domains.documento_legal.schema import (
    AceiteCreate,
    AceiteStatus,
    DocumentoLegalHistorico,
    DocumentoLegalPublico,
    DocumentoLegalRead,
    DocumentoLegalResumo,
    RascunhoCreate,
    RascunhoUpdate,
)
from app.domains.usuario.model import RoleUsuario, Usuario
from app.domains.usuario.service import exige_role, get_current_user

### publico, sem login

router = APIRouter(prefix="/documentos-legais", tags=["documentos-legais"])


@router.get("/{tipo}", response_model=list[DocumentoLegalHistorico])
async def listar_historico(
    tipo: TipoDocumentoLegal,
    db: AsyncSession = Depends(get_async_session),
) -> list[DocumentoLegal]:
    return await service.listar_historico(db, tipo)


@router.get("/{tipo}/atual", response_model=DocumentoLegalPublico)
async def buscar_atual(
    tipo: TipoDocumentoLegal,
    db: AsyncSession = Depends(get_async_session),
) -> DocumentoLegal:
    return await service.buscar_atual(db, tipo)


@router.get("/{tipo}/versoes/{versao}", response_model=DocumentoLegalPublico)
async def buscar_versao(
    tipo: TipoDocumentoLegal,
    versao: int,
    db: AsyncSession = Depends(get_async_session),
) -> DocumentoLegal:
    return await service.buscar_publicada(db, tipo, versao)


### aceite

aceite_router = APIRouter(prefix="/usuarios/me/aceite-termos", tags=["usuarios"])


@aceite_router.get("", response_model=AceiteStatus)
async def status_aceite(
    usuario: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
) -> AceiteStatus:
    return await service.status_aceite(db, usuario)


@aceite_router.post("", response_model=AceiteStatus)
async def aceitar_documentos(
    data: AceiteCreate,
    usuario: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
) -> AceiteStatus:
    return await service.aceitar_documentos(db, usuario, data)


### admin

admin_router = APIRouter(
    prefix="/admin/documentos-legais",
    tags=["admin"],
    dependencies=[Depends(exige_role(RoleUsuario.admin))],
)


@admin_router.get("", response_model=list[DocumentoLegalResumo])
async def listar_documentos(
    tipo: TipoDocumentoLegal | None = None,
    db: AsyncSession = Depends(get_async_session),
) -> list[DocumentoLegalResumo]:
    return await service.listar_documentos(db, tipo)


@admin_router.get("/{documento_id}", response_model=DocumentoLegalRead)
async def buscar_documento(
    documento_id: int,
    db: AsyncSession = Depends(get_async_session),
) -> DocumentoLegal:
    return await service.buscar_documento(db, documento_id)


@admin_router.post("", response_model=DocumentoLegalRead, status_code=status.HTTP_201_CREATED)
async def criar_rascunho(
    data: RascunhoCreate,
    db: AsyncSession = Depends(get_async_session),
    admin: Usuario = Depends(get_current_user),
) -> DocumentoLegal:
    return await service.criar_rascunho(db, data, admin)


@admin_router.patch("/{documento_id}", response_model=DocumentoLegalRead)
async def editar_rascunho(
    documento_id: int,
    data: RascunhoUpdate,
    db: AsyncSession = Depends(get_async_session),
) -> DocumentoLegal:
    return await service.editar_rascunho(db, documento_id, data)


@admin_router.post("/{documento_id}/publicar", response_model=DocumentoLegalRead)
async def publicar_rascunho(
    documento_id: int,
    db: AsyncSession = Depends(get_async_session),
) -> DocumentoLegal:
    return await service.publicar_rascunho(db, documento_id)


@admin_router.delete("/{documento_id}", status_code=status.HTTP_204_NO_CONTENT)
async def descartar_rascunho(
    documento_id: int,
    db: AsyncSession = Depends(get_async_session),
) -> None:
    await service.descartar_rascunho(db, documento_id)
