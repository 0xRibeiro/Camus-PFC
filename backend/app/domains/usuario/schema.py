from pydantic import BaseModel, ConfigDict, EmailStr

from app.domains.usuario.model import RoleUsuario

###### auth: entrada do login e formato dos tokens

class UsuarioLogin(BaseModel):
    email: EmailStr
    password: str


class TokenPair(BaseModel):  # resposta do login e do refresh
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


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
    username: str
    email: EmailStr
    password: str


class UsuarioUpdate(BaseModel):
    username: str | None = None
    email: EmailStr | None = None
    password: str | None = None


###### schemas usados so pelo admin (tem role/is_active q o usuario normal n mexe)

class UsuarioStaffCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: RoleUsuario


class UsuarioAdminUpdate(BaseModel):
    username: str | None = None
    email: EmailStr | None = None
    password: str | None = None
    role: RoleUsuario | None = None
    is_active: bool | None = None
