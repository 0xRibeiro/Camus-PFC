from unittest.mock import AsyncMock, Mock

import pytest

from app.domains.denuncia import service


# repo falso da denuncia. o service chama tudo com await, por isso o AsyncMock
@pytest.fixture
def repo(monkeypatch):
    repo_fake = AsyncMock()
    # o criar/salvar devolve o proprio objeto, igual o repo de verdade faz
    repo_fake.criar.side_effect = lambda denuncia: denuncia
    repo_fake.salvar.side_effect = lambda denuncia: denuncia
    monkeypatch.setattr(service, "DenunciaRepository", Mock(return_value=repo_fake))
    return repo_fake
