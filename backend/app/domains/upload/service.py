from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status
from fastcrud.exceptions.http_exceptions import BadRequestException

from app.core.config import settings
from app.domains.upload.schema import ImagemRead

# sem svg pq ele pode ter script dentro
TIPOS_PERMITIDOS = {
    "image/png": "png",
    "image/jpeg": "jpg",
    "image/webp": "webp",
    "image/gif": "gif",
}


async def salvar_imagem(arquivo: UploadFile) -> ImagemRead:
    tipo = arquivo.content_type or ""
    extensao = TIPOS_PERMITIDOS.get(tipo)
    if extensao is None:
        raise BadRequestException("Formato não aceito, use PNG, JPG, WEBP ou GIF")

    # le 1 byte a mais q o limite so pra saber se passou
    dados = await arquivo.read(settings.upload_max_bytes + 1)
    if len(dados) > settings.upload_max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail="Imagem maior que 10 MB",
        )

    # nome aleatorio pra n repetir nem aceitar nome estranho do usuario
    nome = f"{uuid4().hex}.{extensao}"
    pasta = Path(settings.upload_dir)
    pasta.mkdir(parents=True, exist_ok=True)
    (pasta / nome).write_bytes(dados)

    return ImagemRead(url=f"{settings.api_url}/uploads/{nome}")
