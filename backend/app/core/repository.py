from typing import Generic, TypeVar

from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import Base

# ModelType é um TypeVar que representa qualquer modelo do SQLAlchemy que herde de Base.
ModelType = TypeVar("ModelType", bound=Base)


# Generic[ModelType]: cada domain declara BaseRepository[domain_model], e assim o tipo do model é conhecido dentro do repositório.
class BaseRepository(Generic[ModelType]):
    model: type[ModelType]

    def __init__(self, db: AsyncSession):
        self.db = db

    # Busca um objeto pelo seu ID
    async def buscar(self, id: int) -> ModelType | None:
        return await self.db.get(self.model, id)

    # Lista objetos paginados (page/size viram query params automaticamente na rota)
    async def listar(self) -> Page[ModelType]:
        return await paginate(self.db, select(self.model))

    # Cria um novo objeto no banco de dados com os campos fornecidos em kwargs(argumentos nomeados dinamicamente por dicionario)
    async def criar(self, **kwargs) -> ModelType:
        obj = self.model(**kwargs) # Cria a instância do modelo com os dados fornecidos
        self.db.add(obj)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj


    # Atualiza um objeto existente com os dados fornecidos
    async def atualizar(self, obj: ModelType, data: dict) -> ModelType:
        for field, value in data.items():
            setattr(obj, field, value) 
        await self.db.commit()
        await self.db.refresh(obj)
        return obj

    # Deleta um objeto do banco de dados
    async def deletar(self, obj: ModelType) -> None:
        await self.db.delete(obj)
        await self.db.commit()
