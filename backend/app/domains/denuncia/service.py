from datetime import datetime, timezone

from fastcrud.exceptions.http_exceptions import (
    BadRequestException,
    DuplicateValueException,
    ForbiddenException,
    NotFoundException,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.denuncia.model import STATUS_PENDENTE, Denuncia
from app.domains.denuncia.repository import DenunciaRepository
from app.domains.denuncia.schema import (
    DenunciaAdminRead,
    DenunciaCreate,
    DenunciaUpdate,
)
from app.domains.grupo.model import Grupo
from app.domains.usuario.model import Usuario


# quem chama já entrega o grupo conferido: ele existe e o usuário participa (dependency grupo_membro)
async def criar_denuncia(db: AsyncSession, grupo: Grupo, data: DenunciaCreate, usuario: Usuario) -> Denuncia:
    if grupo.id_dono == usuario.id:
        raise ForbiddenException("O dono não pode denunciar o próprio grupo")

    repo = DenunciaRepository(db)

    # o conteúdo denunciado tem que ser mesmo desse grupo
    if data.id_conteudo is not None and not await repo.conteudo_pertence_ao_grupo(data.id_conteudo, grupo.id):
        raise NotFoundException("Conteúdo não encontrado neste grupo")

    # bloqueia denúncia repetida da mesma pessoa enquanto a anterior ainda está pendente
    if await repo.buscar_pendente(usuario.id, grupo.id, data.id_conteudo) is not None:
        raise DuplicateValueException("Você já enviou uma denúncia pendente sobre isso")

    denuncia = Denuncia(
        id_denunciante=usuario.id,
        id_grupo=grupo.id,
        id_conteudo=data.id_conteudo,
        motivo=data.motivo,
        descricao=data.descricao or None,
    )
    return await repo.criar(denuncia)


async def listar_denuncias(db: AsyncSession, status: str | None) -> list[DenunciaAdminRead]:
    return await DenunciaRepository(db).listar(status)


async def resolver_denuncia(db: AsyncSession, denuncia_id: int, data: DenunciaUpdate) -> Denuncia:
    repo = DenunciaRepository(db)
    denuncia = await repo.buscar(denuncia_id)

    if denuncia is None:
        raise NotFoundException("Denúncia não encontrada")

    if denuncia.status != STATUS_PENDENTE:
        raise BadRequestException("Essa denúncia já foi analisada")

    denuncia.status = data.status
    denuncia.resolvido_em = datetime.now(timezone.utc)
    return await repo.salvar(denuncia)