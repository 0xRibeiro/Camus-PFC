import re
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.domains.usuario.avatares import AVATARES
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


class ForgotPasswordInput(BaseModel):
    email: EmailStr


class ResetPasswordInput(BaseModel):  
    email: EmailStr
    code: str
    password: str = Field(..., min_length=8, max_length=128)


###### schemas de usuario

class UsuarioRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: EmailStr
    is_active: bool
    role: RoleUsuario
    deletado_em: datetime | None
    avatar: str
    cor_fundo: str


class UsuarioCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr = Field(..., max_length=100)
    password: str = Field(..., min_length=8, max_length=128)
    aceitou_termos: bool = Field(..., description="Usuário deve aceitar os Termos de Uso")
    
    @field_validator("aceitou_termos")
    @classmethod
    def exige_aceite(cls, v: bool) -> bool:
        if not v:
            raise ValueError(
                "É necessário aceitar os Termos de Uso e a Política de Privacidade"
            )
        return v


class UsuarioUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=3, max_length=50)
    email: EmailStr | None = Field(default=None, max_length=100)
    password: str | None = Field(default=None, min_length=8, max_length=128)
    avatar: str | None = None
    cor_fundo: str | None = None

    # so aceita avatar da lista liberada pelo sistema
    @field_validator("avatar")
    @classmethod
    def valida_avatar(cls, v: str | None) -> str | None:
        if v is not None and v not in AVATARES:
            raise ValueError("avatar inválido")
        return v

    # cor no formato #RRGGBB (o mesmo que o UColorPicker devolve)
    @field_validator("cor_fundo")
    @classmethod
    def valida_cor_fundo(cls, v: str | None) -> str | None:
        if v is not None and not re.fullmatch(r"#[0-9a-fA-F]{6}", v):
            raise ValueError("cor inválida, use o formato #RRGGBB")
        return v.upper() if v is not None else v
    

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
