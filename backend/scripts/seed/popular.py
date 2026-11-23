# seed doido
#
# uv run python -m scripts.seed.popular
# 
# uv run python -m scripts.seed.popular --apagar
#
# com --apagar tira tudo

import argparse
import asyncio
import random

from sqlalchemy import delete, select

# carrega todos os models
import app.main  # noqa: F401
from app.core.database import async_session_maker
from app.domains.auditoria.model import LogAuditoria
from app.domains.conquistas.model import associacao_conquista_usuario
from app.domains.dispositivo.model import Dispositivo
from app.domains.trilha.model import Trilha
from app.domains.usuario.model import Usuario
from scripts.seed.config import DOMINIO, PREFIXO, PREFIXO_MAC, SENHA
from scripts.seed.denuncias import criar_denuncias
from scripts.seed.dispositivos import criar_dispositivos
from scripts.seed.grupos import criar_grupos
from scripts.seed.progresso import Progresso
from scripts.seed.trilhas import (
    inserir_trilhas,
    montar_trilhas_de_grupo,
    montar_trilhas_globais,
)
from scripts.seed.usuarios import criar_aceites, criar_acessos, criar_usuarios
from scripts.seed.util import ligar_auditoria


async def ja_populado(db) -> bool:
    return (
        await db.scalar(
            select(Usuario.id).where(Usuario.email.like(f"%{DOMINIO}")).limit(1)
        )
        is not None
    )


# transacao unica
async def popular() -> None:
    random.seed(42)

    async with async_session_maker() as db:
        if await ja_populado(db):
            print("o banco já tem dados do seed, rode com --apagar antes")
            return
        await ligar_auditoria(db, False)

        staff, alunos = await criar_usuarios(db)
        usuarios = staff + alunos
        await criar_aceites(db, usuarios)

        trilhas_globais = montar_trilhas_globais(staff)
        await inserir_trilhas(db, trilhas_globais)
        grupos = await criar_grupos(db, alunos)
        trilhas_de_grupo = montar_trilhas_de_grupo(grupos)
        await inserir_trilhas(db, trilhas_de_grupo)

        progresso = Progresso()
        progresso.simular(alunos, trilhas_globais, trilhas_de_grupo)
        await progresso.salvar(db)

        denuncias = await criar_denuncias(db, trilhas_de_grupo)
        dispositivos = await criar_dispositivos(db)
        await criar_acessos(db, usuarios, progresso.ultima_atividade)

        await ligar_auditoria(db, True)
        await db.commit()

    print(f"usuários: {len(staff)} staff e {len(alunos)} alunos (senha {SENHA})")
    print(
        f"trilhas: {len(trilhas_globais)} globais e {len(trilhas_de_grupo)} de grupo, {len(grupos)} grupos"
    )
    print(
        f"conclusões: {len(progresso.conclusoes)}, tentativas: {len(progresso.tentativas)}, xp: {len(progresso.lancamentos)}"
    )
    print(f"denúncias: {len(denuncias)}, dispositivos: {dispositivos}")


async def apagar() -> None:
    async with async_session_maker() as db:
        ids = list(
            (
                await db.scalars(
                    select(Usuario.id).where(Usuario.email.like(f"%{DOMINIO}"))
                )
            ).all()
        )
        if not ids:
            print("nada do seed no banco")
            return
        await ligar_auditoria(db, False)

        # essas n tem cascade
        await db.execute(
            delete(associacao_conquista_usuario).where(
                associacao_conquista_usuario.c.usuario_id.in_(ids)
            )
        )
        await db.execute(delete(LogAuditoria).where(LogAuditoria.usuario_id.in_(ids)))
        await db.execute(
            delete(LogAuditoria).where(
                LogAuditoria.entidade == "usuarios", LogAuditoria.entidade_id.in_(ids)
            )
        )

        # sem dono, vai pelo prefixo
        await db.execute(
            delete(Trilha).where(
                Trilha.grupo_id.is_(None), Trilha.titulo.like(f"{PREFIXO}%")
            )
        )
        await db.execute(
            delete(Dispositivo).where(Dispositivo.mac.like(f"{PREFIXO_MAC}%"))
        )

        # o resto vai no cascade
        await db.execute(delete(Usuario).where(Usuario.id.in_(ids)))

        await ligar_auditoria(db, True)
        await db.commit()
    print(f"apagados {len(ids)} usuários do seed e tudo ligado a eles")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--apagar", action="store_true", help="tira os dados do seed do banco"
    )
    argumentos = parser.parse_args()
    asyncio.run(apagar() if argumentos.apagar else popular())
