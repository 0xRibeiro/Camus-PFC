import colorsys
import random

# avatares liberados pelo sistema. o usuario so escolhe uma dessas chaves
# a chave e o nome do arquivo da imagem no front (ex: betta -> betta.png)
# pra adicionar um avatar novo: coloca a chave aqui e a imagem no front
AVATARES = (
    "peixe-palhaco",
    "betta",
    "neon",
    "guppy",
    "peixe-dourado",
    "cavalo-marinho",
)


# avatares que so liberam depois de ganhar uma conquista
# a imagem tambem fica no front, igual aos de cima
AVATARES_BLOQUEADOS = {
    "peixonauta": 13,
    "marina": 14,
    "zico": 15,
}

# tudo que o usuario pode ter, liberado ou nao
TODOS_AVATARES = AVATARES + tuple(AVATARES_BLOQUEADOS)





AVATAR_PADRAO = AVATARES[0]
COR_FUNDO_PADRAO = "#0EA5E9"


# matiz qualquer, saturacao e luz fixas pra n sair cor apagada nem quase preta/branca
def sortear_cor_fundo() -> str:
    r, g, b = colorsys.hls_to_rgb(random.random(), 0.5, 0.75)
    return f"#{round(r * 255):02X}{round(g * 255):02X}{round(b * 255):02X}"


def sortear_avatar() -> str:
    return random.choice(AVATARES)
