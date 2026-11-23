from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from fastcrud.exceptions.http_exceptions import (
    BadRequestException,
    DuplicateValueException,
    ForbiddenException,
    NotFoundException,
)

from app.domains.denuncia import service
from app.domains.denuncia.schema import DenunciaCreate, DenunciaUpdate

# o service so le id e id_dono, entao um objeto simples ja basta no lugar do model
GRUPO = SimpleNamespace(id=1, id_dono=10)
MEMBRO = SimpleNamespace(id=20)


async def test_dono_nao_pode_denunciar_o_proprio_grupo(repo):
    dono = SimpleNamespace(id=GRUPO.id_dono)
    data = DenunciaCreate(motivo="spam")

    with pytest.raises(ForbiddenException):
        await service.criar_denuncia(AsyncMock(), GRUPO, data, dono)

    repo.criar.assert_not_called()


async def test_conteudo_de_outro_grupo_nao_pode_ser_denunciado(repo):
    repo.conteudo_pertence_ao_grupo.return_value = False
    data = DenunciaCreate(motivo="spam", id_conteudo=99)

    with pytest.raises(NotFoundException):
        await service.criar_denuncia(AsyncMock(), GRUPO, data, MEMBRO)

    repo.criar.assert_not_called()


async def test_denuncia_repetida_enquanto_pendente_e_recusada(repo):
    repo.buscar_pendente.return_value = SimpleNamespace(id=5)
    data = DenunciaCreate(motivo="assedio")

    with pytest.raises(DuplicateValueException):
        await service.criar_denuncia(AsyncMock(), GRUPO, data, MEMBRO)

    repo.criar.assert_not_called()
