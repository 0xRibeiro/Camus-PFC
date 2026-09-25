from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.domains.auditoria.model import AcaoAuditoria


class LogAuditoriaRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    usuario_id: int | None
    acao: AcaoAuditoria
    entidade: str
    entidade_id: int
    alteracoes: dict
    criado_em: datetime
