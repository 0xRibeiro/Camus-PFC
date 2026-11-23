import random
from datetime import timedelta

from app.domains.grupo.model import Grupo, Participacao
from scripts.seed.config import AGORA, QTD_GRUPOS
from scripts.seed.util import inserir, inserir_sem_id, momento_entre, texto


def montar_grupos(alunos: list[dict]) -> list[dict]:
    # dono antigo pra espalhar os grupos
    donos = []
    for aluno in alunos:
        if aluno["criado_em"] < AGORA - timedelta(days=60):
            donos.append(aluno)

    grupos = []
    for _ in range(QTD_GRUPOS):
        dono = random.choice(donos)
        criado_em = momento_entre(dono["criado_em"], AGORA - timedelta(days=7))
        grupo = {
            "linha": {"nome": texto(), "criado_em": criado_em},
            "dono": dono,
            "membros": [],
        }

        # maioria entre 10 e 40
        tamanho = (
            random.randint(10, 40) if random.random() < 0.85 else random.randint(2, 9)
        )
        for aluno in random.sample(alunos, tamanho + 1):
            if aluno is dono or len(grupo["membros"]) == tamanho:
                continue
            # maioria entra logo
            entrou = momento_entre(max(criado_em, aluno["criado_em"]), AGORA, curva=3)
            grupo["membros"].append((aluno, entrou))
        grupos.append(grupo)
    return grupos


async def criar_grupos(db, alunos: list[dict]) -> list[dict]:
    grupos = montar_grupos(alunos)

    linhas = []
    for grupo in grupos:
        grupo["linha"]["id_dono"] = grupo["dono"]["id"]
        linhas.append(grupo["linha"])
    await inserir(db, Grupo, linhas)

    # dono tb participa
    participacoes = []
    for grupo in grupos:
        participacoes.append(
            {"id_grupo": grupo["linha"]["id"], "id_usuario": grupo["dono"]["id"]}
        )
        for aluno, entrou in grupo["membros"]:
            participacoes.append(
                {"id_grupo": grupo["linha"]["id"], "id_usuario": aluno["id"]}
            )
    await inserir_sem_id(db, Participacao, participacoes)
    return grupos
