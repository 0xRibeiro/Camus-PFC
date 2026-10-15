from polyfactory.factories.pydantic_factory import ModelFactory

from app.domains.trilha.schema import TrilhaCreate


class TrilhaCreateFactory(ModelFactory[TrilhaCreate]):
    pass
