import secrets

from fastcrud.exceptions.http_exceptions import (
    DuplicateValueException,
    ForbiddenException,
    NotFoundException,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.redis import redis_client
from app.domains.aquario.model import Aquario, PapelAquario
from app.domains.aquario.repository import AquarioRepository
from app.domains.aquario.schema import (
    AquarioEntrar,
    AquarioRead,
    ConviteAquarioRead,
    MembroAquarioRead,
)
from app.domains.dispositivo import service as dispositivo_service
from app.domains.dispositivo.model import Dispositivo
from app.domains.dispositivo.repository import DispositivoRepository
from app.domains.dispositivo.schema import CodigoDispositivo, ComandoModulo, DispositivoRead, ModuloIotRead
from app.domains.peixe.model import Peixe
from app.domains.peixe.schema import PeixeCreate

CONVITE_VALIDADE_SEGUNDOS = 900


# so o dono passa
async def buscar_aquario_do_usuario(repo: AquarioRepository, aquario_id: int, usuario_id: int) -> Aquario:
    aquario = await repo.buscar_do_usuario(aquario_id, usuario_id)
    if aquario is None:
        raise NotFoundException("Aquário não encontrado")

    return aquario


async def papel_do_usuario(repo: AquarioRepository, aquario: Aquario, usuario_id: int) -> PapelAquario | None:
    if aquario.id_dono == usuario_id:
        return PapelAquario.dono

    membro = await repo.buscar_membro(aquario.id, usuario_id)
    if membro is None:
        return None

    return membro.papel


# sem acesso da 404 pra n revelar q existe
async def buscar_com_papel(repo: AquarioRepository, aquario_id: int, usuario_id: int) -> tuple[Aquario, PapelAquario]:
    aquario = await repo.buscar(aquario_id)
    if aquario is None:
        raise NotFoundException("Aquário não encontrado")

    papel = await papel_do_usuario(repo, aquario, usuario_id)
    if papel is None:
        raise NotFoundException("Aquário não encontrado")

    return aquario, papel


def exigir_edicao(papel: PapelAquario) -> None:
    if papel == PapelAquario.leitor:
        raise ForbiddenException("Leitor só pode ver esse aquário")


async def montar_read(db: AsyncSession, aquario: Aquario, papel: PapelAquario) -> AquarioRead:
    dispositivo = await DispositivoRepository(db).buscar_do_aquario(aquario.id)

    dispositivo_read = None
    if dispositivo is not None:
        dispositivo_read = DispositivoRead.model_validate(dispositivo)

    return AquarioRead(id=aquario.id, nome=aquario.nome, litros=aquario.litros, papel=papel, dispositivo=dispositivo_read)


async def listar_aquarios(db: AsyncSession, usuario_id: int) -> list[AquarioRead]:
    repo = AquarioRepository(db)

    aquarios = []
    for aquario in await repo.listar_do_usuario(usuario_id):
        papel = await papel_do_usuario(repo, aquario, usuario_id)
        if papel is not None:
            aquarios.append(await montar_read(db, aquario, papel))
    return aquarios


async def buscar_aquario(db: AsyncSession, aquario_id: int, usuario_id: int) -> AquarioRead:
    aquario, papel = await buscar_com_papel(AquarioRepository(db), aquario_id, usuario_id)
    return await montar_read(db, aquario, papel)


async def listar_peixes(db: AsyncSession, aquario_id: int, usuario_id: int) -> list[Peixe]:
    repo = AquarioRepository(db)
    await buscar_com_papel(repo, aquario_id, usuario_id)
    return await repo.listar_peixes(aquario_id)


async def cadastrar_peixe(db: AsyncSession, aquario_id: int, data: PeixeCreate, usuario_id: int) -> Peixe:
    repo = AquarioRepository(db)
    aquario, papel = await buscar_com_papel(repo, aquario_id, usuario_id)
    exigir_edicao(papel)

    peixe = Peixe(aquario_id=aquario.id, nome=data.nome, especie=data.especie)
    return await repo.criar_peixe(peixe)


# so o dono conecta, e so iot livre
async def conectar_dispositivo(db: AsyncSession, aquario_id: int, data: CodigoDispositivo, usuario_id: int) -> Dispositivo:
    aquario = await buscar_aquario_do_usuario(AquarioRepository(db), aquario_id, usuario_id)
    dispositivo = await dispositivo_service.buscar_por_codigo(db, data.codigo)

    if dispositivo.id_aquario == aquario.id:
        raise DuplicateValueException("Esse IoT já está nesse aquário")

    if dispositivo.id_aquario is not None:
        raise DuplicateValueException("Esse IoT já está em outro aquário, use 'Entrar com código'")

    dispositivo_repo = DispositivoRepository(db)

    if await dispositivo_repo.buscar_do_aquario(aquario.id) is not None:
        raise DuplicateValueException("Esse aquário já tem um IoT")

    dispositivo.id_aquario = aquario.id
    await dispositivo_repo.salvar(dispositivo)
    await dispositivo_service.apagar_codigo(data.codigo)
    return dispositivo


# quem digita o codigo vira operador do aquario do iot, leitor sobe pra operador
async def entrar_com_codigo(db: AsyncSession, data: CodigoDispositivo, usuario_id: int) -> AquarioRead:
    dispositivo = await dispositivo_service.buscar_por_codigo(db, data.codigo)

    if dispositivo.id_aquario is None:
        raise NotFoundException("Esse IoT ainda não está em um aquário")

    repo = AquarioRepository(db)
    aquario = await repo.buscar(dispositivo.id_aquario)

    if aquario is None:
        raise NotFoundException("Aquário não encontrado")

    if aquario.id_dono == usuario_id:
        raise DuplicateValueException("Você já é dono desse aquário")

    membro = await repo.buscar_membro(aquario.id, usuario_id)

    if membro is not None and membro.papel == PapelAquario.operador:
        raise DuplicateValueException("Você já é operador desse aquário")

    await repo.salvar_membro(aquario.id, usuario_id, PapelAquario.operador)
    await dispositivo_service.apagar_codigo(data.codigo)
    return await montar_read(db, aquario, PapelAquario.operador)


# mesmo efeito do desvincular todos do aparelho
async def desconectar_dispositivo(db: AsyncSession, aquario_id: int, usuario_id: int) -> None:
    aquario = await buscar_aquario_do_usuario(AquarioRepository(db), aquario_id, usuario_id)
    dispositivo = await DispositivoRepository(db).buscar_do_aquario(aquario.id)

    if dispositivo is None:
        raise NotFoundException("Esse aquário não tem IoT")

    await dispositivo_service.tirar_do_aquario(db, dispositivo)


async def listar_modulos(db: AsyncSession, aquario_id: int, usuario_id: int, minutos: int) -> list[ModuloIotRead]:
    aquario, papel = await buscar_com_papel(AquarioRepository(db), aquario_id, usuario_id)
    dispositivo = await DispositivoRepository(db).buscar_do_aquario(aquario.id)

    if dispositivo is None:
        return []

    return await dispositivo_service.listar_modulos(db, dispositivo, minutos)


# leitor so ve, dono e operador ligam/desligam
async def comandar_modulo(db: AsyncSession, aquario_id: int, usuario_id: int, serial: str, comando: ComandoModulo) -> None:
    aquario, papel = await buscar_com_papel(AquarioRepository(db), aquario_id, usuario_id)
    exigir_edicao(papel)

    dispositivo = await DispositivoRepository(db).buscar_do_aquario(aquario.id)
    if dispositivo is None:
        raise NotFoundException("Aquário sem IoT conectado")

    await dispositivo_service.enviar_comando(db, dispositivo, serial, comando)


async def gerar_convite(db: AsyncSession, aquario_id: int, usuario_id: int) -> ConviteAquarioRead:
    aquario = await buscar_aquario_do_usuario(AquarioRepository(db), aquario_id, usuario_id)

    while True:
        convite = secrets.token_urlsafe(9)
        criado = await redis_client.set(f"aquario:convite:{convite}", str(aquario.id), ex=CONVITE_VALIDADE_SEGUNDOS, nx=True)

        if criado:
            return ConviteAquarioRead(convite=convite, expira_em_segundos=CONVITE_VALIDADE_SEGUNDOS)


# convite sempre entra como leitor
async def entrar_com_convite(db: AsyncSession, data: AquarioEntrar, usuario_id: int) -> AquarioRead:
    aquario_id = await redis_client.get(f"aquario:convite:{data.convite}")

    if aquario_id is None:
        raise NotFoundException("Convite inválido ou expirou")

    repo = AquarioRepository(db)
    aquario = await repo.buscar(int(aquario_id))

    if aquario is None:
        raise NotFoundException("Aquário não encontrado")

    if aquario.id_dono == usuario_id or await repo.buscar_membro(aquario.id, usuario_id) is not None:
        raise DuplicateValueException("Você já participa desse aquário")

    await repo.salvar_membro(aquario.id, usuario_id, PapelAquario.leitor)
    return await montar_read(db, aquario, PapelAquario.leitor)


async def listar_membros(db: AsyncSession, aquario_id: int, usuario_id: int) -> list[MembroAquarioRead]:
    repo = AquarioRepository(db)
    aquario, meu_papel = await buscar_com_papel(repo, aquario_id, usuario_id)

    membros = []
    if aquario.id_dono is not None:
        dono = await repo.buscar_username(aquario.id_dono)
        if dono is not None:
            membros.append(MembroAquarioRead(username=dono, papel=PapelAquario.dono))

    for username, papel in await repo.listar_membros(aquario.id):
        membros.append(MembroAquarioRead(username=username, papel=papel))
    return membros


async def sair_do_aquario(db: AsyncSession, aquario_id: int, usuario_id: int) -> None:
    repo = AquarioRepository(db)
    membro = await repo.buscar_membro(aquario_id, usuario_id)

    if membro is None:
        raise NotFoundException("Você não é membro desse aquário")

    await repo.remover_membro(membro)