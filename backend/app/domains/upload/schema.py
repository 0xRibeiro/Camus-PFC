from pydantic import BaseModel


class ImagemRead(BaseModel):
    url: str
