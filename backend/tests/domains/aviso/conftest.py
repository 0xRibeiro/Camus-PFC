from unittest.mock import AsyncMock, Mock

import pytest

from app.domains.aviso import service


@pytest.fixture
def repo(monkeypatch):
    repo_fake = AsyncMock()
    repo_fake.salvar.side_effect = lambda aviso: aviso
    monkeypatch.setattr(service, "AvisoRepository", Mock(return_value=repo_fake))
    return repo_fake
