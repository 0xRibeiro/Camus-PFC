from unittest.mock import AsyncMock, Mock

import pytest

from app.core import security
from app.domains.usuario import service


# repo falso q todo teste usa e vem limpo em cada teste
@pytest.fixture
def repo(monkeypatch):
    repo_fake = AsyncMock()  # async pq o service chama os metodos do repo com await
    # troca a classe la dentro do service com o monkeypatch pra ela devolver o repo falso
    monkeypatch.setattr(service, "UsuarioRepository", Mock(return_value=repo_fake))
    return repo_fake


# redis falso pros testes q mexem com token e quem ta online
@pytest.fixture
def redis(monkeypatch):
    redis_fake = AsyncMock()  # async msm motivo repo
    # troca nos dois lugares q usam o redis_client o security dos tokens e o service do online
    monkeypatch.setattr(security, "redis_client", redis_fake)
    monkeypatch.setattr(service, "redis_client", redis_fake)
    return redis_fake
