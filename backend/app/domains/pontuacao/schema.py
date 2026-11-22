from datetime import date, datetime

from pydantic import BaseModel, ConfigDict

from app.domains.pontuacao.model import OrigemLancamento


class XpRead(BaseModel):
    xp_total: int
    # so no xp global de aluno com algum ponto
    posicao: int | None = None


class XpDiaRead(BaseModel):
    data: date
    pontos: int


class RankingItemRead(BaseModel):
    posicao: int
    usuario_id: int
    username: str
    avatar: str
    cor_fundo: str
    xp_total: int


class LancamentoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    origem_tipo: OrigemLancamento
    origem_id: int
    # titulo da origem, None se o conteudo foi excluido
    titulo: str | None = None
    versao: int
    pontos: int
    grupo_id: int | None = None
    criado_em: datetime
