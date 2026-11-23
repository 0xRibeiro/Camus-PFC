from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

# o --apagar acha o seed por esses
DOMINIO = "seed.camus"
PREFIXO = "seed-"
PREFIXO_MAC = "5EED"
SENHA = "seed1234"
DIAS = 820

QTD_ADMINS = 5
QTD_AUTHORS = 5
QTD_ALUNOS = 10000
QTD_GRUPOS = 500
QTD_TRILHAS_GLOBAIS = 15
QTD_DENUNCIAS = 30
QTD_DISPOSITIVOS = 2000

# alto pq so trilha da xp
PONTOS_ARTIGO = 20
PONTOS_QUIZ = 60

# iguais as do front
TAGS = ["iot", "limnologia", "biologia", "oceanografia", "aquarismo", "outro"]
MOTIVOS = [
    "conteudo_improprio",
    "assedio",
    "spam",
    "informacao_incorreta",
    "conteudo_com_defeito",
    "outro",
]

FUSO = ZoneInfo("America/Sao_Paulo")
AGORA = datetime.now(timezone.utc)
INICIO = AGORA - timedelta(days=DIAS)
