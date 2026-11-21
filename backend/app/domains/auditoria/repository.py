from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.auditoria.model import LogAuditoria
from app.domains.usuario.model import Usuario


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
    ) -> list[tuple[LogAuditoria, str | None]]:
        # outerjoin pq log do sistema (sem usuario) tb aparece, ai o nome vem None
        query = select(LogAuditoria, Usuario.username).outerjoin(
            Usuario, Usuario.id == LogAuditoria.usuario_id
        )

        if entidade is not None:
            query = query.where(LogAuditoria.entidade == entidade)

        if entidade_id is not None:
            query = query.where(LogAuditoria.entidade_id == entidade_id)

        if usuario_id is not None:
            query = query.where(LogAuditoria.usuario_id == usuario_id)

        query = query.order_by(LogAuditoria.criado_em.desc()).limit(limite).offset(offset)

        resultado = await self.db.execute(query)
        logs = []
        for log, username in resultado.all():
            logs.append((log, username))
        return logs

    # log escrito na mao, pra acao q n passa pelo trigger (tipo ver um email)
    async def registrar(self, log: LogAuditoria) -> None:
        self.db.add(log)
        await self.db.commit()
