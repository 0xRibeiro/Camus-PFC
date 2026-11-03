from fastapi import APIRouter, Depends, UploadFile, status

from app.domains.upload import service
from app.domains.upload.schema import ImagemRead
from app.domains.usuario.model import RoleUsuario
from app.domains.usuario.service import exige_role

# so author e admin mandam imagem, quem le e o StaticFiles do main
router = APIRouter(
    prefix="/imagens",
    tags=["imagens"],
    dependencies=[Depends(exige_role(RoleUsuario.author, RoleUsuario.admin))],
)


@router.post("", response_model=ImagemRead, status_code=status.HTTP_201_CREATED)
async def enviar_imagem(file: UploadFile) -> ImagemRead:
    return await service.salvar_imagem(file)
