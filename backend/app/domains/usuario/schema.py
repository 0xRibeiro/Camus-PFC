from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.domains.usuario.model import RoleUsuario

###### auth: entrada do login e formato dos tokens

class UsuarioLogin(BaseModel):
    email: EmailStr
    password: str


class TokenPair(BaseModel):  # resposta do login e do refresh
    access_token: str
    refresh_token: str


class RefreshInput(BaseModel):  # body do /auth/refresh e /auth/logout
    refresh_token: str


###### schemas de usuario

class UsuarioRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: EmailStr
    is_active: bool
    role: RoleUsuario


class UsuarioCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr = Field(..., max_length=100)
    password: str = Field(..., min_length=8, max_length=128)


class UsuarioUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=3, max_length=50)
    email: EmailStr | None = Field(default=None, max_length=100)
    password: str | None = Field(default=None, min_length=8, max_length=128)


###### schemas usados so pelo admin (tem role/is_active q o usuario normal n mexe)

class UsuarioStaffCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr = Field(..., max_length=100)
    password: str = Field(..., min_length=8, max_length=128)
    role: RoleUsuario = Field(..., description="author ou admin")


class UsuarioAdminUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=3, max_length=50)
    email: EmailStr | None = Field(default=None, max_length=100)
    password: str | None = Field(default=None, min_length=8, max_length=128)
    role: RoleUsuario | None = None
    is_active: bool | None = None
