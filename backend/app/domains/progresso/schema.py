from pydantic import BaseModel

from app.domains.trilha.model import ConteudoTipo


###### trilha vista pelo aluno com o status de cada conteudo
class ConteudoStatusRead(BaseModel):
    id: int
    titulo: str
    tipo: ConteudoTipo
    ordem: int
    pontos: int
    versao: int
    concluido: bool
    liberado: bool
    atualizado: bool


class ModuloAlunoRead(BaseModel):
    id: int
    titulo: str
    ordem: int
    concluidos: int
    total: int
    conteudos: list[ConteudoStatusRead]


class TrilhaResumoRead(BaseModel):
    id: int
    titulo: str
    descricao: str | None = None
    foto: str | None = None
    tag: str | None = None
    concluidos: int
    total: int
    progresso: int


class TrilhaAlunoRead(TrilhaResumoRead):
    modulos: list[ModuloAlunoRead]


###### conteudo aberto pelo aluno
# alternativa sem o campo correta pro gabarito n vazar
class AlternativaAlunoRead(BaseModel):
    id: int
    texto: str


class QuestaoAlunoRead(BaseModel):
    id: int
    ordem: int
    enunciado: str
    alternativas: list[AlternativaAlunoRead]


class ConteudoAlunoRead(BaseModel):
    id: int
    modulo_id: int
    titulo: str
    tipo: ConteudoTipo
    pontos: int
    versao: int
    video_url: str | None = None
    artigo_conteudo: dict | None = None
    questoes: list[QuestaoAlunoRead]
    concluido: bool
    atualizado: bool
    proximo_conteudo_id: int | None = None


###### concluir e responder
class ConclusaoRead(BaseModel):
    xp_ganho: int


# respostas no formato {questao_id: alternativa_id}
class RespostaQuizCreate(BaseModel):
    respostas: dict[int, int]


class CorrecaoQuestaoRead(BaseModel):
    questao_id: int
    alternativa_escolhida_id: int | None = None
    alternativa_correta_id: int | None = None
    acertou: bool


class ResultadoQuizRead(BaseModel):
    acertos: int
    total: int
    xp_ganho: int
    correcao: list[CorrecaoQuestaoRead]
