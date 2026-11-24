import random
from datetime import datetime, timedelta

from sqlalchemy import insert, text

from scripts.seed.config import PREFIXO

# desliga pro log n ficar com data de hoje
TABELAS_AUDITADAS = [
    "usuarios",
    "trilhas",
    "modulos",
    "conteudos",
    "questoes",
    "alternativas",
    "conquistas",
    "documentos_legais",
    "aceites_documentos_legais",
    "denuncias",
    "avisos",
    "grupos",
]


# seed-1a2b3c4d
def texto() -> str:
    return f"{PREFIXO}{random.getrandbits(32):08x}"


# curva maior puxa pro comeco
def momento_entre(inicio: datetime, fim: datetime, curva: float = 1.0) -> datetime:
    if fim <= inicio:
        return inicio
    return inicio + (fim - inicio) * (random.random() ** curva)


def depois(momento: datetime, minimo: timedelta, maximo: timedelta) -> datetime:
    return momento + minimo + (maximo - minimo) * random.random()


# insert em lote q devolve o id
async def inserir(db, model, linhas: list[dict]) -> None:
    for inicio in range(0, len(linhas), 1000):
        lote = linhas[inicio : inicio + 1000]
        resultado = await db.execute(
            insert(model).returning(model.id, sort_by_parameter_order=True), lote
        )
        for linha, novo_id in zip(lote, resultado.scalars().all()):
            linha["id"] = novo_id


# pra tabela sem id
async def inserir_sem_id(db, tabela, linhas: list[dict]) -> None:
    for inicio in range(0, len(linhas), 1000):
        await db.execute(insert(tabela), linhas[inicio : inicio + 1000])


async def ligar_auditoria(db, ligada: bool) -> None:
    acao = "ENABLE" if ligada else "DISABLE"
    for tabela in TABELAS_AUDITADAS:
        await db.execute(
            text(f"ALTER TABLE {tabela} {acao} TRIGGER {tabela}_auditoria")
        )
