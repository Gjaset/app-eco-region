from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.routes.formulario import normalizar
from app.database import get_db
from app.core.seguridad import require_staff
from app.models.tramite import Cliente, EstadoTramite, Tramite
from app.schemas.tramites import EstadoUpdate, TramiteCreate, TramiteRead

router = APIRouter(prefix="/tramites", tags=["Trámites"])


@router.post("", response_model=TramiteRead, status_code=201)
async def crear_tramite(datos: TramiteCreate, db: Session = Depends(get_db), _user=Depends(require_staff)):
    if db.get(Cliente, datos.cliente_id) is None:
        raise HTTPException(status_code=404, detail="Cliente no encontrado.")

    normalizado = await normalizar(datos.formulario)
    tramite = Tramite(
        cliente_id=datos.cliente_id,
        estado=(EstadoTramite.LISTO_RADICAR
                if normalizado["listo_para_generar"]
                else EstadoTramite.EN_REVISION),
        datos_formulario=datos.formulario.model_dump(),
        datos_normalizados=normalizado,
        autoridad_sigla=normalizado.get("autoridad", {}).get("sigla"),
        municipio_dane=normalizado.get("municipio", {}).get("codigo_dane"),
    )
    db.add(tramite)
    db.commit()
    db.refresh(tramite)
    return tramite


@router.get("", response_model=list[TramiteRead])
def listar_tramites(db: Session = Depends(get_db), _user=Depends(require_staff)):
    return list(db.scalars(select(Tramite).order_by(Tramite.creado_en.desc())))


@router.get("/{tramite_id}", response_model=TramiteRead)
def obtener_tramite(tramite_id: int, db: Session = Depends(get_db), _user=Depends(require_staff)):
    tramite = db.get(Tramite, tramite_id)
    if tramite is None:
        raise HTTPException(status_code=404, detail="Trámite no encontrado.")
    return tramite


@router.patch("/{tramite_id}/estado", response_model=TramiteRead)
def actualizar_estado(tramite_id: int, datos: EstadoUpdate, db: Session = Depends(get_db), _user=Depends(require_staff)):
    tramite = db.get(Tramite, tramite_id)
    if tramite is None:
        raise HTTPException(status_code=404, detail="Trámite no encontrado.")

    tramite.estado = datos.estado
    if datos.numero_radicado is not None:
        tramite.numero_radicado = datos.numero_radicado
    db.commit()
    db.refresh(tramite)
    return tramite
