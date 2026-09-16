import io
import os
import logging
import re
import unicodedata
import zipfile
from datetime import datetime, timezone

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, Query, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified

from app.core.ia.validacion import ensamblar_dictamen, validar_documento
from app.core.seguridad import get_current_user, require_admin, require_staff
from app.core.solicitudes import guardar_solicitud, leer_archivo
from app.database import SessionLocal, get_db
from app.models.solicitud import Solicitud
from app.models.usuario import Usuario
from app.schemas.solicitudes import SolicitudRead

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/solicitudes", tags=["Solicitudes"])


def _to_read(solicitud: Solicitud) -> SolicitudRead:
    usuario = solicitud.usuario
    return SolicitudRead(
        id=solicitud.id,
        usuario_id=solicitud.usuario_id,
        usuario_email=getattr(usuario, "email", "") or "",
        usuario_nombre=getattr(usuario, "nombre", "") or "",
        tipo=solicitud.tipo,
        estado=solicitud.estado,
        nombre_archivo=solicitud.nombre_archivo,
        tamano_bytes=solicitud.tamano_bytes,
        creado_en=solicitud.creado_en,
        resumen=solicitud.resumen,
    )


def _get_visible(solicitud_id: int, usuario: Usuario, db: Session) -> Solicitud:
    solicitud = db.get(Solicitud, solicitud_id)
    if solicitud is None:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada.")
    if usuario.rol != "admin" and solicitud.usuario_id != usuario.id:
        raise HTTPException(status_code=403, detail="No tienes acceso a esta solicitud.")
    return solicitud


@router.get("/mias", response_model=list[SolicitudRead])
def mis_solicitudes(
    usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)
):
    filas = db.scalars(
        select(Solicitud)
        .where(Solicitud.usuario_id == usuario.id)
        .order_by(Solicitud.creado_en.desc(), Solicitud.id.desc())
    )
    return [_to_read(s) for s in filas]


@router.get("", response_model=list[SolicitudRead])
def listar_solicitudes(
    usuario_id: int | None = None,
    db: Session = Depends(get_db),
    _admin: Usuario = Depends(require_admin),
):
    consulta = select(Solicitud).order_by(Solicitud.creado_en.desc(), Solicitud.id.desc())
    if usuario_id is not None:
        consulta = consulta.where(Solicitud.usuario_id == usuario_id)
    return [_to_read(s) for s in db.scalars(consulta)]


@router.get("/descargar-zip")
def descargar_zip(
    ids: str = Query(..., description="IDs separados por coma"),
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        identificadores = sorted({int(parte) for parte in ids.split(",") if parte.strip()})
    except ValueError:
        raise HTTPException(status_code=422, detail="IDs inválidos.")
    if not identificadores:
        raise HTTPException(status_code=422, detail="Debes seleccionar al menos un documento.")
    if len(identificadores) > 50:
        raise HTTPException(status_code=422, detail="Máximo 50 documentos por descarga.")

    solicitudes = [_get_visible(i, usuario, db) for i in identificadores]
    marca = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M")
    duenos = {s.usuario_id for s in solicitudes}
    if len(duenos) == 1:
        base = solicitudes[0].usuario.nombre or solicitudes[0].usuario.email
        base = unicodedata.normalize("NFKD", base).encode("ascii", "ignore").decode()
        base = re.sub(r"[^A-Za-z0-9]+", "_", base).strip("_") or "usuario"
        nombre_zip = f"{base}_{marca}.zip"
    else:
        nombre_zip = f"solicitudes_{marca}.zip"

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for solicitud in solicitudes:
            try:
                zf.writestr(solicitud.nombre_archivo, leer_archivo(solicitud))
            except FileNotFoundError:
                raise HTTPException(
                    status_code=410,
                    detail=f"Archivo no disponible: {solicitud.nombre_archivo}",
                ) from None
    buffer.seek(0)
    return StreamingResponse(
        buffer,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{nombre_zip}"'},
    )


@router.get("/{solicitud_id}/descargar")
def descargar_solicitud(
    solicitud_id: int,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    solicitud = _get_visible(solicitud_id, usuario, db)
    contenido = leer_archivo(solicitud)
    media = _media_type(solicitud.nombre_archivo)
    return StreamingResponse(
        io.BytesIO(contenido),
        media_type=media,
        headers={"Content-Disposition": f'attachment; filename="{solicitud.nombre_archivo}"'},
    )


async def _validar_ia_en_segundo_plano(solicitud_id: int) -> None:
    """Valida el documento con IA y persiste el dictamen en `resumen`.

    Corre en background con su propia sesión: no bloquea la subida y nunca
    rompe el flujo si la IA falla (validar_documento devuelve dictamen
    "no disponible" en vez de lanzar).
    """
    db = SessionLocal()
    try:
        solicitud = db.get(Solicitud, solicitud_id)
        if solicitud is None:
            return
        dictamen = await validar_documento(
            solicitud.tipo, solicitud.nombre_archivo, leer_archivo(solicitud)
        )
        resumen = dict(solicitud.resumen or {})
        resumen.update(ensamblar_dictamen(solicitud.tipo, dictamen))
        solicitud.resumen = resumen
        flag_modified(solicitud, "resumen")
        db.commit()
    except Exception:  # pragma: no cover - defensivo
        logger.exception("Falló la validación IA en segundo plano (solicitud %s)", solicitud_id)
        db.rollback()
    finally:
        db.close()


@router.get("/{solicitud_id}/validacion")
def dictamen_ia(
    solicitud_id: int,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    solicitud = _get_visible(solicitud_id, usuario, db)
    dictamen = (solicitud.resumen or {}).get("validacion_ia")
    if dictamen is None:
        return {"estado_validacion": "pendiente"}
    return {"estado_validacion": "lista", "validacion": dictamen}


@router.post("/subir", response_model=SolicitudRead)
async def subir_documento(
    background_tasks: BackgroundTasks,
    archivo: UploadFile = File(...),
    tipo: str = Form(...),
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Guarda un documento subido por el usuario (F1/F2/F3/FG1/FG2/FUN) como
    solicitud y lanza en segundo plano la validación IA de su diligenciamiento."""
    contenido = await archivo.read()
    if not contenido:
        raise HTTPException(status_code=422, detail="El archivo está vacío.")
    # Límite pensado para Vercel Hobby (body máx. ~4.5 MB); deja margen para
    # el multipart/form-data y otras cabeceras.
    MAX_UPLOAD_BYTES = 4 * 1024 * 1024
    if len(contenido) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"El archivo supera el límite de {MAX_UPLOAD_BYTES // (1024 * 1024)} MB. Comprímelo o divídelo e inténtalo de nuevo.",
        )
    nombre = archivo.filename or "documento"
    # tipo limitado a las categorías conocidas para evitar ruido en el panel
    tipos_validos = {"fun", "formulario", "sda", "corpoboyaca", "f1", "f2", "f3", "fg1", "fg2"}
    if tipo not in tipos_validos:
        raise HTTPException(status_code=422, detail=f"Tipo no válido: {tipo}")
    extension = ("." + nombre.rsplit(".", 1)[1]) if "." in nombre else ""
    # Tipos extraíbles; si es otro formato no se agenda la validación.
    tipos_extraibles = {".pdf", ".docx", ".xlsx", ".xls", ".txt", ".csv"}
    solicitud = guardar_solicitud(
        db,
        usuario_id=usuario.id,
        tipo=tipo,
        contenido=contenido,
        nombre_base=nombre.rsplit(".", 1)[0],
        extension=extension,
        resumen={"origen": "frontend"},
    )
    if extension.lower() in tipos_extraibles:
        if os.getenv("VERCEL"):
            # Serverless: la función se congela tras la respuesta, así que
            # validamos inline antes de responder (~5-15 s extra en la subida).
            await _validar_ia_en_segundo_plano(solicitud.id)
        else:
            background_tasks.add_task(_validar_ia_en_segundo_plano, solicitud.id)
    return _to_read(solicitud)


ESTADOS_VALIDOS = {"pendiente", "en_revision", "aprobado", "rechazado"}


@router.patch("/{solicitud_id}/estado", response_model=SolicitudRead)
def cambiar_estado(
    solicitud_id: int,
    estado: str,
    usuario: Usuario = Depends(require_staff),
    db: Session = Depends(get_db),
):
    solicitud = db.get(Solicitud, solicitud_id)
    if solicitud is None:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada.")
    if estado not in ESTADOS_VALIDOS:
        raise HTTPException(status_code=422, detail=f"Estado no válido: {estado}")
    solicitud.estado = estado
    db.commit()
    db.refresh(solicitud)
    return _to_read(solicitud)


def _media_type(nombre_archivo: str) -> str:
    nombre = nombre_archivo.lower()
    if nombre.endswith(".pdf"):
        return "application/pdf"
    if nombre.endswith(".xlsx"):
        return "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    if nombre.endswith(".xls"):
        return "application/vnd.ms-excel"
    return "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
