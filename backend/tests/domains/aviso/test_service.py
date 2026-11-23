from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from fastcrud.exceptions.http_exceptions import NotFoundException

from app.domains.aviso import service

USUARIO = SimpleNamespace(id=3)


async def test_listar_avisos_busca_so_os_nao_lidos_do_usuario(repo):
    repo.listar_nao_lidos.return_value = ["a", "b"]

    avisos = await service.listar_avisos(AsyncMock(), USUARIO)

    assert avisos == ["a", "b"]
    repo.listar_nao_lidos.assert_awaited_once_with(USUARIO.id)


async def test_marcar_aviso_inexistente_da_404(repo):
    repo.buscar.return_value = None

    with pytest.raises(NotFoundException):
        await service.marcar_como_lido(AsyncMock(), 1, USUARIO)
