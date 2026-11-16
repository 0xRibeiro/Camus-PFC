from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.documento_legal.model import AceiteDocumentoLegal, DocumentoLegal, TipoDocumentoLegal
from app.domains.documento_legal.schema import DocumentoLegalResumo
from app.domains.usuario.model import Usuario


class DocumentoLegalRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def buscar(self, documento_id: int) -> DocumentoLegal | None:
        return await self.db.get(DocumentoLegal, documento_id)

    async def criar(self, documento: DocumentoLegal) -> DocumentoLegal:
        self.db.add(documento)
        await self.db.commit()
        await self.db.refresh(documento)
        return documento

    async def salvar(self, documento: DocumentoLegal) -> DocumentoLegal:
        await self.db.commit()
        await self.db.refresh(documento)
        return documento

    async def apagar(self, documento: DocumentoLegal) -> None:
        await self.db.delete(documento)
        await self.db.commit()

    async def buscar_rascunho(self, tipo: TipoDocumentoLegal) -> DocumentoLegal | None:
        consulta = select(DocumentoLegal).where(
            DocumentoLegal.tipo == tipo,
            DocumentoLegal.publicado_em.is_(None),
        )
        return await self.db.scalar(consulta)

    # conta rascunho tbm
    async def maior_versao(self, tipo: TipoDocumentoLegal) -> int | None:
        consulta = select(func.max(DocumentoLegal.versao)).where(DocumentoLegal.tipo == tipo)
        return await self.db.scalar(consulta)

    async def buscar_atual(self, tipo: TipoDocumentoLegal) -> DocumentoLegal | None:
        consulta = (
            select(DocumentoLegal)
            .where(DocumentoLegal.tipo == tipo, DocumentoLegal.publicado_em.is_not(None))
            .order_by(DocumentoLegal.versao.desc())
            .limit(1)
        )
        return await self.db.scalar(consulta)

    async def buscar_publicada(self, tipo: TipoDocumentoLegal, versao: int) -> DocumentoLegal | None:
        consulta = select(DocumentoLegal).where(
            DocumentoLegal.tipo == tipo,
            DocumentoLegal.versao == versao,
            DocumentoLegal.publicado_em.is_not(None),
        )
        return await self.db.scalar(consulta)

    async def listar_publicadas(self, tipo: TipoDocumentoLegal) -> list[DocumentoLegal]:
        consulta = (
            select(DocumentoLegal)
            .where(DocumentoLegal.tipo == tipo, DocumentoLegal.publicado_em.is_not(None))
            .order_by(DocumentoLegal.versao.desc())
        )
        resultado = await self.db.scalars(consulta)
        return list(resultado.all())

    async def aceitou(self, usuario_id: int, documento_id: int) -> bool:
        consulta = select(AceiteDocumentoLegal.id).where(
            AceiteDocumentoLegal.usuario_id == usuario_id,
            AceiteDocumentoLegal.documento_id == documento_id,
        )
        return await self.db.scalar(consulta) is not None

    async def registrar_aceites(self, aceites: list[AceiteDocumentoLegal]) -> None:
        self.db.add_all(aceites)
        await self.db.commit()

    async def listar(self, tipo: TipoDocumentoLegal | None) -> list[DocumentoLegalResumo]:
        consulta = (
            select(DocumentoLegal, Usuario.username)
            .join(Usuario, Usuario.id == DocumentoLegal.criado_por)
            .order_by(DocumentoLegal.tipo, DocumentoLegal.versao.desc())
        )
        if tipo is not None:
            consulta = consulta.where(DocumentoLegal.tipo == tipo)

        resultado = await self.db.execute(consulta)

        documentos = []
        for documento, autor in resultado.all():
            documentos.append(
                DocumentoLegalResumo(
                    id=documento.id,
                    tipo=documento.tipo,
                    versao=documento.versao,
                    publicado_em=documento.publicado_em,
                    criado_por=documento.criado_por,
                    autor=autor,
                    criado_em=documento.criado_em,
                )
            )
        return documentos
