from unittest.mock import AsyncMock

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.domains.usuario.service import get_current_user
from app.main import app
from tests.domains.usuario.factories import UsuarioFactory


# client q chama a api direto na memoria sem precisar subir servidor real
@pytest.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client


# troca o get_current_user por um falso q devolve o user podenedo escolher role
@pytest.fixture
def usuario_logado():
    usuario = UsuarioFactory.build()

    def get_current_user_fake():
        return usuario

    app.dependency_overrides[get_current_user] = get_current_user_fake
    yield usuario
    app.dependency_overrides.clear()  # tira o override no final


@pytest.fixture
def db():
    db_fake = AsyncMock(spec=AsyncSession)  # spec copia o formato da sessao real

    async def get_async_session_fake():
        yield db_fake

    app.dependency_overrides[get_async_session] = get_async_session_fake
    yield db_fake
    app.dependency_overrides.clear()
