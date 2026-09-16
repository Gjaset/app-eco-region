from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session
from typing import cast

from app.core.seguridad import (
    create_access_token,
    get_current_user,
    hash_password,
    require_admin,
    verify_password,
)
from app.database import get_db
from app.models.usuario import Usuario
from app.schemas.auth import RegistroUsuario, Token, UsuarioRead

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/register", response_model=UsuarioRead, status_code=201)
def registrar_usuario(datos: RegistroUsuario, db: Session = Depends(get_db)):
    if datos.rol not in {"admin", "consultor", "cliente"}:
        raise HTTPException(status_code=422, detail="Rol de usuario no válido.")
    if db.scalar(select(Usuario).where(Usuario.email == datos.email.lower())):
        raise HTTPException(status_code=409, detail="Ya existe un usuario con ese email.")

    usuario = Usuario(
        email=datos.email.lower(),
        nombre=datos.nombre,
        password_hash=hash_password(datos.password),
        rol=datos.rol,
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


@router.post("/login", response_model=Token)
def iniciar_sesion(
    formulario: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    usuario = db.scalar(select(Usuario).where(Usuario.email == formulario.username.lower()))
    if usuario is None or not usuario.activo or not verify_password(
        formulario.password, cast(str, usuario.password_hash)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"access_token": create_access_token(usuario), "token_type": "bearer"}


@router.get("/me", response_model=UsuarioRead)
def obtener_perfil(usuario: Usuario = Depends(get_current_user)):
    return usuario


class ActualizarUsuario(BaseModel):
    rol: str | None = None
    activo: bool | None = None


@router.get("/usuarios", response_model=list[UsuarioRead])
def listar_usuarios(db: Session = Depends(get_db), _admin: Usuario = Depends(require_admin)):
    return list(db.scalars(select(Usuario).order_by(Usuario.creado_en.desc())))


@router.patch("/usuarios/{usuario_id}", response_model=UsuarioRead)
def actualizar_usuario(
    usuario_id: int,
    datos: ActualizarUsuario,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(require_admin),
):
    usuario = db.get(Usuario, usuario_id)
    if usuario is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    if datos.rol is not None:
        if datos.rol not in {"admin", "consultor", "cliente"}:
            raise HTTPException(status_code=422, detail="Rol de usuario no válido.")
        usuario.rol = datos.rol
    if datos.activo is not None:
        if usuario.id == admin.id and datos.activo is False:
            raise HTTPException(status_code=422, detail="No puedes desactivar tu propia cuenta.")
        usuario.activo = datos.activo
    db.commit()
    db.refresh(usuario)
    return usuario


@router.delete("/usuarios/{usuario_id}", status_code=204)
def eliminar_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(require_admin),
):
    usuario = db.get(Usuario, usuario_id)
    if usuario is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    if usuario.id == admin.id:
        raise HTTPException(status_code=422, detail="No puedes eliminar tu propia cuenta.")
    db.delete(usuario)
    db.commit()
