from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.domains.pontuacao.model import OrigemLancamento


class XpRead(BaseModel):
    xp_total: int


class LancamentoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    origem_tipo: OrigemLancamento
    origem_id: int
    versao: int
    pontos: int
    grupo_id: int | None = None
    criado_em: datetime
