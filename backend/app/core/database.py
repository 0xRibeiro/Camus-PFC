from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


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
