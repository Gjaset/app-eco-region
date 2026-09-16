from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.seguridad import require_staff
from app.models.tramite import Cliente
from app.schemas.tramites import ClienteCreate, ClienteRead

router = APIRouter(prefix="/clientes", tags=["Clientes"])


@router.post("", response_model=ClienteRead, status_code=201)
def crear_cliente(datos: ClienteCreate, db: Session = Depends(get_db), _user=Depends(require_staff)):
    existente = db.scalar(select(Cliente).where(Cliente.nit == datos.nit))
    if existente:
        raise HTTPException(status_code=409, detail="Ya existe un cliente con ese NIT.")

    cliente = Cliente(**datos.model_dump())
    db.add(cliente)
    db.commit()
    db.refresh(cliente)
    return cliente


@router.get("", response_model=list[ClienteRead])
def listar_clientes(db: Session = Depends(get_db), _user=Depends(require_staff)):
    return list(db.scalars(select(Cliente).order_by(Cliente.nombre)))


@router.get("/{cliente_id}", response_model=ClienteRead)
def obtener_cliente(cliente_id: int, db: Session = Depends(get_db), _user=Depends(require_staff)):
    cliente = db.get(Cliente, cliente_id)
    if cliente is None:
        raise HTTPException(status_code=404, detail="Cliente no encontrado.")
    return cliente
