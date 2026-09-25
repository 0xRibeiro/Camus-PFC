import enum
from datetime import datetime

from sqlalchemy import event, insert
from sqlalchemy.orm.attributes import get_history

from app.core.database import Base
from app.core.security import usuario_atual_id
from app.domains.auditoria.model import AcaoAuditoria, LogAuditoria


# colunas em tabelas q tiver enum e datetime nao entram no JSON sem isso
def serializar(valor):
    if isinstance(valor, enum.Enum):
        return valor.value
    if isinstance(valor, datetime):
        return valor.isoformat()
    return valor


# usa a mesma connection do flush em andamento, entao fica na mesma
# transacao da mudanca que gerou o log
def inserir_log(connection, acao, entidade, entidade_id, alteracoes):
    if not alteracoes:
        return
    connection.execute(
        insert(LogAuditoria).values(
            usuario_id=usuario_atual_id.get(),
            acao=acao,
            entidade=entidade,
            entidade_id=entidade_id,
            alteracoes=alteracoes,
        )
    )


# todo model do projeto usa "id" como pk
def id_da_instancia(target):
    return target.id


# propagate=True faz esse listener valer pra toda classe que herda de
# Base, sem precisar registrar um por um. after_insert roda depois do
# INSERT, entao o id autoincrement do target ja existe
@event.listens_for(Base, "after_insert", propagate=True)
def log_insert(mapper, connection, target):
    alteracoes = {}
    for coluna in mapper.columns:
        alteracoes[coluna.key] = {
            "antigo": None,
            "novo": serializar(getattr(target, coluna.key)),
        }

    inserir_log(
        connection, AcaoAuditoria.create, target.__tablename__,
        id_da_instancia(target), alteracoes,
    )


# before_update roda antes do UPDATE, entao get_history() ainda sabe
# qual era o valor antigo de cada coluna
@event.listens_for(Base, "before_update", propagate=True)
def log_update(mapper, connection, target):
    alteracoes = {}
    for coluna in mapper.columns:
        historico = get_history(target, coluna.key)
        if not historico.has_changes():
            continue

        antigo = None
        if historico.deleted:
            antigo = historico.deleted[0]

        novo = None
        if historico.added:
            novo = historico.added[0]

        alteracoes[coluna.key] = {
            "antigo": serializar(antigo),
            "novo": serializar(novo),
        }

    inserir_log(
        connection, AcaoAuditoria.update, target.__tablename__,
        id_da_instancia(target), alteracoes,
    )


# before_delete roda antes do DELETE, entao ainda da pra ler os valores
# do target antes da linha sumir do banco
@event.listens_for(Base, "before_delete", propagate=True)
def log_delete(mapper, connection, target):
    alteracoes = {}
    for coluna in mapper.columns:
        alteracoes[coluna.key] = {
            "antigo": serializar(getattr(target, coluna.key)),
            "novo": None,
        }

    inserir_log(
        connection, AcaoAuditoria.delete, target.__tablename__,
        id_da_instancia(target), alteracoes,
    )
