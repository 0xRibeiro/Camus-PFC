import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


# client q chama a api direto na memoria sem precisar subir servidor real
@pytest.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client
