import random
from datetime import datetime, timedelta

from app.domains.trilha.model import (
    Alternativa,
    Conteudo,
    ConteudoTipo,
    Modulo,
    Questao,
    Trilha,
)
from app.domains.usuario.model import RoleUsuario
from scripts.seed.config import (
    AGORA,
    INICIO,
    PONTOS_ARTIGO,
    PONTOS_QUIZ,
    QTD_TRILHAS_GLOBAIS,
    TAGS,
)
from scripts.seed.util import depois, inserir, momento_entre, texto

# ordem q o aluno ve
def percorrer_conteudos(trilhas: list[dict]) -> list[dict]:
    lista = []
    for trilha in trilhas:
        for modulo in trilha["modulos"]:
            lista.extend(modulo["conteudos"])
    return lista


def montar_questoes() -> list[dict]:
    questoes = []
    for ordem in range(random.randint(3, 5)):
        correta = random.randrange(4)
        alternativas = []
        for indice in range(4):
            alternativas.append({"texto": texto(), "correta": indice == correta})
        questoes.append(
            {
                "linha": {"ordem": ordem + 1, "enunciado": texto()},
                "alternativas": alternativas,
            }
        )
    return questoes


# leituras e fecha com quiz
def montar_modulo(ordem: int, criado_em: datetime) -> dict:
    conteudos = []
    for indice in range(random.randint(1, 2)):
        artigo = {
            "type": "doc",
            "content": [
                {"type": "paragraph", "content": [{"type": "text", "text": texto()}]}
            ],
        }
        conteudos.append(
            {
                "linha": {
                    "titulo": texto(),
                    "tipo": ConteudoTipo.artigo,
                    "ordem": indice + 1,
                    "pontos": PONTOS_ARTIGO,
                    "versao": 1,
                    "versao_desde": criado_em,
                    "criado_em": criado_em,
                    "artigo_conteudo": artigo,
                },
                "questoes": [],
            }
        )
    conteudos.append(
        {
            "linha": {
                "titulo": texto(),
                "tipo": ConteudoTipo.quiz,
                "ordem": len(conteudos) + 1,
                "pontos": PONTOS_QUIZ,
                "versao": 1,
                "versao_desde": criado_em,
                "criado_em": criado_em,
            },
            "questoes": montar_questoes(),
        }
    )
    return {"linha": {"titulo": texto(), "ordem": ordem}, "conteudos": conteudos}


def montar_trilhas_globais(staff: list[dict]) -> list[dict]:
    autores = []
    for pessoa in staff:
        if pessoa["role"] == RoleUsuario.author:
            autores.append(pessoa)

    trilhas = []
    for indice in range(QTD_TRILHAS_GLOBAIS):
        autor = random.choice(autores)
        criada = momento_entre(
            max(autor["criado_em"], INICIO + timedelta(days=5)),
            INICIO + timedelta(days=120),
        )
        trilha = {
            "linha": {
                "titulo": texto(),
                "tag": TAGS[indice % len(TAGS)],
                "descricao": texto(),
                "is_active": True,
                "criado_em": criada,
            },
            "autor": autor,
            "grupo": None,
            "modulos": [],
        }
        for ordem in range(random.randint(2, 3)):
            trilha["modulos"].append(montar_modulo(ordem + 1, criada))
        trilhas.append(trilha)
    return trilhas


def montar_trilhas_de_grupo(grupos: list[dict]) -> list[dict]:
    trilhas = []
    for grupo in grupos:
        for _ in range(random.choice([0, 1, 1, 2, 2, 3])):
            criada = depois(
                grupo["linha"]["criado_em"], timedelta(hours=2), timedelta(days=20)
            )
            criada = min(criada, AGORA - timedelta(hours=1))
            trilha = {
                "linha": {
                    "titulo": texto(),
                    "descricao": texto(),
                    "is_active": True,
                    "criado_em": criada,
                },
                "autor": grupo["dono"],
                "grupo": grupo,
                "modulos": [],
            }
            for ordem in range(random.randint(1, 2)):
                trilha["modulos"].append(montar_modulo(ordem + 1, criada))
            trilhas.append(trilha)
    return trilhas


# um nivel por vez por causa dos ids
async def inserir_trilhas(db, trilhas: list[dict]) -> None:
    linhas = []
    for trilha in trilhas:
        if trilha["grupo"] is not None:
            trilha["linha"]["grupo_id"] = trilha["grupo"]["linha"]["id"]
        linhas.append(trilha["linha"])
    await inserir(db, Trilha, linhas)

    linhas = []
    for trilha in trilhas:
        for modulo in trilha["modulos"]:
            modulo["linha"]["trilha_id"] = trilha["linha"]["id"]
            linhas.append(modulo["linha"])
    await inserir(db, Modulo, linhas)

    linhas = []
    for trilha in trilhas:
        for modulo in trilha["modulos"]:
            for conteudo in modulo["conteudos"]:
                conteudo["linha"]["modulo_id"] = modulo["linha"]["id"]
                linhas.append(conteudo["linha"])
    await inserir(db, Conteudo, linhas)

    linhas = []
    for conteudo in percorrer_conteudos(trilhas):
        for questao in conteudo["questoes"]:
            questao["linha"]["conteudo_id"] = conteudo["linha"]["id"]
            linhas.append(questao["linha"])
    await inserir(db, Questao, linhas)

    linhas = []
    for conteudo in percorrer_conteudos(trilhas):
        for questao in conteudo["questoes"]:
            for alternativa in questao["alternativas"]:
                alternativa["questao_id"] = questao["linha"]["id"]
                linhas.append(alternativa)
    await inserir(db, Alternativa, linhas)
