from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.auditoria.model import LogAuditoria


class AuditoriaRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def listar(
        self,
        limite: int = 50,
        offset: int = 0,
        entidade: str | None = None,
        entidade_id: int | None = None,
        usuario_id: int | None = None,
    ) -> list[LogAuditoria]:
        query = select(LogAuditoria)

        if entidade is not None:
            query = query.where(LogAuditoria.entidade == entidade)

        if entidade_id is not None:
            query = query.where(LogAuditoria.entidade_id == entidade_id)

        if usuario_id is not None:
            query = query.where(LogAuditoria.usuario_id == usuario_id)

        query = query.order_by(LogAuditoria.criado_em.desc()).limit(limite).offset(offset)

        resultado = await self.db.execute(query)
        return list(resultado.scalars().all())
