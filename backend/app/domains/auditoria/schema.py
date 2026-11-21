from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict, field_validator

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
    # vem do join com usuarios, pro front n precisar carregar a lista toda
    usuario_nome: str | None = None

    # a coluna e sem fuso mas guarda utc. marca como utc pro navegador
    # converter pro horario de quem ta vendo, se n ele acha q ja e local
    @field_validator("criado_em")
    @classmethod
    def marca_utc(cls, v: datetime) -> datetime:
        if v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v
