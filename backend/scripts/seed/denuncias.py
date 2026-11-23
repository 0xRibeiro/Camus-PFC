import random

from app.domains.denuncia.model import Denuncia
from scripts.seed.config import AGORA, MOTIVOS, QTD_DENUNCIAS
from scripts.seed.trilhas import percorrer_conteudos
from scripts.seed.util import inserir, momento_entre, texto


async def criar_denuncias(db, trilhas_de_grupo: list[dict]) -> list[dict]:
    possiveis = []
    for trilha in trilhas_de_grupo:
        if trilha["grupo"]["membros"]:
            possiveis.append(trilha)

    denuncias = []
    for _ in range(QTD_DENUNCIAS):
        trilha = random.choice(possiveis)
        conteudo = random.choice(percorrer_conteudos([trilha]))["linha"]
        denunciante, entrou = random.choice(trilha["grupo"]["membros"])
        denuncias.append({
            "id_denunciante": denunciante["id"],
            "id_grupo": trilha["grupo"]["linha"]["id"],
            "id_conteudo": conteudo["id"],
            "titulo_conteudo": conteudo["titulo"],
            "motivo": random.choice(MOTIVOS),
            "descricao": texto() if random.random() < 0.6 else None,
            "criado_em": momento_entre(max(entrou, conteudo["criado_em"]), AGORA),
        })

    await inserir(db, Denuncia, denuncias)
    return denuncias
