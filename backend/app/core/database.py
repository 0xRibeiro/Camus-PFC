from collections.abc import AsyncGenerator

from sqlalchemy import event, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Session

from app.core.config import settings
from app.core.security import usuario_atual_id

# Cria o engine do SQLAlchemy, que é responsável por gerenciar a conexão com o banco de dados.
engine = create_async_engine(settings.database_url, echo=settings.debug)

# Cria uma fábrica de sessões, que serão abertas e fechadas a cada requisição.
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


# Cria uma classe base para os modelos do SQLAlchemy herdarem.
class Base(DeclarativeBase):
    pass


# Dependency do FastAPI: abre a sessão, entrega pra rota usar, fecha no final.
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


# roda toda vez que uma transacao comeca. avisa o postgres quem e o usuario
# atual, pra o trigger de auditoria conseguir ler isso via current_setting
@event.listens_for(Session, "after_begin")
def marcar_usuario_na_transacao(session, transaction, connection):
    usuario_id = usuario_atual_id.get()
    if usuario_id is not None:
        sql = text("SELECT set_config('app.current_user_id', :id, true)")
        parametros = {"id": str(usuario_id)}
        connection.execute(sql, parametros)
