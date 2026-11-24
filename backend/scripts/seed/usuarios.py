import random
from datetime import timedelta

from sqlalchemy import select

from app.core.security import criar_hash
from app.domains.documento_legal.model import AceiteDocumentoLegal, DocumentoLegal
from app.domains.usuario.avatares import AVATARES, sortear_cor_fundo
from app.domains.usuario.model import AcessoUsuario, RoleUsuario, Usuario
from scripts.seed.config import (
    AGORA,
    DOMINIO,
    INICIO,
    QTD_ADMINS,
    QTD_ALUNOS,
    QTD_AUTHORS,
    SENHA,
)
from scripts.seed.util import depois, inserir, inserir_sem_id, momento_entre, texto


def montar_usuario(senha_hash: str, role: RoleUsuario, criado_em) -> dict:
    username = texto()
    return {
        "username": username,
        "email": f"{username}@{DOMINIO}",
        "hashed_password": senha_hash,
        "role": role,
        "is_active": True,
        "criado_em": criado_em,
        "avatar": random.choice(AVATARES),
        "cor_fundo": sortear_cor_fundo(),
    }


# staff entra no 1o mes
async def criar_usuarios(db) -> tuple[list[dict], list[dict]]:
    senha_hash = criar_hash(SENHA)  # hash unico, se n demora

    staff = []
    for indice in range(QTD_ADMINS + QTD_AUTHORS):
        role = RoleUsuario.admin if indice < QTD_ADMINS else RoleUsuario.author
        staff.append(
            montar_usuario(
                senha_hash, role, momento_entre(INICIO, INICIO + timedelta(days=30))
            )
        )

    # mais alunos no fim
    alunos = []
    for _ in range(QTD_ALUNOS):
        alunos.append(
            montar_usuario(
                senha_hash, RoleUsuario.aluno, momento_entre(INICIO, AGORA, curva=0.8)
            )
        )

    await inserir(db, Usuario, staff + alunos)
    return staff, alunos


# aceita os termos atuais
async def criar_aceites(db, usuarios: list[dict]) -> None:
    documentos = await db.scalars(
        select(DocumentoLegal).where(DocumentoLegal.publicado_em.is_not(None))
    )
    atuais = {}
    for documento in documentos.all():
        if (
            documento.tipo not in atuais
            or documento.versao > atuais[documento.tipo].versao
        ):
            atuais[documento.tipo] = documento

    aceites = []
    for usuario in usuarios:
        for documento in atuais.values():
            quando = depois(
                max(usuario["criado_em"], documento.publicado_em),
                timedelta(minutes=1),
                timedelta(minutes=30),
            )
            aceites.append(
                {
                    "usuario_id": usuario["id"],
                    "documento_id": documento.id,
                    "aceito_em": min(quando, AGORA),
                }
            )
    await inserir(db, AceiteDocumentoLegal, aceites)


# aluno pela ultima atividade
async def criar_acessos(db, usuarios: list[dict], ultima_atividade: dict) -> None:
    acessos = []
    for usuario in usuarios:
        ultima = ultima_atividade.get(usuario["id"], usuario["criado_em"])
        if usuario["role"] != RoleUsuario.aluno:
            ultima = momento_entre(AGORA - timedelta(days=7), AGORA)
        acessos.append({"usuario_id": usuario["id"], "ultimo_acesso_em": ultima})
    await inserir_sem_id(db, AcessoUsuario, acessos)
