from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class ErroBase(Exception):
    status_code: int = 400
    headers: dict | None = None

    def __init__(self, detail: str):
        self.detail = detail
        super().__init__(detail)


class NaoEncontradoError(ErroBase):
    status_code = 404


class ConflitoError(ErroBase):
    status_code = 400


class NaoAutorizadoError(ErroBase):
    status_code = 401


class AcessoNegadoError(ErroBase):
    status_code = 403


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(ErroBase)
    async def erro_base_handler(request: Request, err: ErroBase):
        return JSONResponse(
            status_code=err.status_code,
            content={"detail": err.detail},
            headers=err.headers,
        )
