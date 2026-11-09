from fastapi import APIRouter, Depends, UploadFile, status

from app.domains.grupo.service import grupo_dono
from app.domains.upload import service
from app.domains.upload.schema import ImagemRead
from app.domains.usuario.model import RoleUsuario
from app.domains.usuario.service import exige_role

# Author e admin enviam imagens globais. O dono envia imagens do grupo.
# O StaticFiles do main serve os arquivos enviados.
router = APIRouter(
    prefix="/imagens",
    tags=["imagens"],
    dependencies=[Depends(exige_role(RoleUsuario.author, RoleUsuario.admin))],
)
grupo_router = APIRouter(
    prefix="/imagens",
    tags=["imagens de grupo"],
    dependencies=[Depends(grupo_dono)],
)


@router.post("", response_model=ImagemRead, status_code=status.HTTP_201_CREATED)
@grupo_router.post("", response_model=ImagemRead, status_code=status.HTTP_201_CREATED)
async def enviar_imagem(file: UploadFile) -> ImagemRead:
    return await service.salvar_imagem(file)