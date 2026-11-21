from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.auditoria.model import LogAuditoria
from app.domains.usuario.model import Usuario


def utc_sem_fuso(data: datetime) -> datetime:
    if data.tzinfo is None:
        return data
    return data.astimezone(timezone.utc).replace(tzinfo=None)


class AuditoriaRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def listar(
        self,
        limite: int = 50,
        offset: int = 0,
        entidades: list[str] | None = None,
        entidade_id: int | None = None,
        usuario_ids: list[int] | None = None,
        desde: datetime | None = None,
        ate: datetime | None = None,
    ) -> list[tuple[LogAuditoria, str | None]]:
        # outerjoin pq log do sistema (sem usuario) tb aparece, ai o nome vem None
        query = select(LogAuditoria, Usuario.username).outerjoin(
            Usuario, Usuario.id == LogAuditoria.usuario_id
        )

        # lista vazia = sem filtro
        if entidades:
            query = query.where(LogAuditoria.entidade.in_(entidades))

        if entidade_id is not None:
            query = query.where(LogAuditoria.entidade_id == entidade_id)

        if usuario_ids:
            query = query.where(LogAuditoria.usuario_id.in_(usuario_ids))

        # desde entra, ate n entra (o front manda o comeco do dia seguinte).
        # a coluna e sem fuso e guarda utc, entao passa pra utc e tira o fuso
        if desde is not None:
            query = query.where(LogAuditoria.criado_em >= utc_sem_fuso(desde))

        if ate is not None:
            query = query.where(LogAuditoria.criado_em < utc_sem_fuso(ate))

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
