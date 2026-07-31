from pydantic import BaseModel, ConfigDict, EmailStr



class UsuarioRead(BaseModel):
    
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: EmailStr | None = None
    is_active: bool


class UsuarioCreate(BaseModel):
    username: str
    email: EmailStr | None = None
    password: str


class UsuarioUpdate(BaseModel):
    username: str | None = None
    email: EmailStr | None = None
    password: str | None = None



