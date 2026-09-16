from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RegistroUsuario(BaseModel):
    email: EmailStr
    nombre: str = Field(min_length=1)
    password: str = Field(min_length=8)
    rol: str = "cliente"


class UsuarioRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    nombre: str
    rol: str
    activo: bool
    creado_en: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
