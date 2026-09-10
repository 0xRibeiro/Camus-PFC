from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError


# pega erro de constraint do bancoe devolve 400 em vez do 500 
def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(IntegrityError)
    async def integrity_handler(request: Request, err: IntegrityError):
        return JSONResponse(
            status_code=400,
            content={"detail": "dados inválidos"},
        )
