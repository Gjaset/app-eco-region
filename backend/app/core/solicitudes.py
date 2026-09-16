"""Persistencia de copias de documentos exportados (trazabilidad por usuario).

El contenido vive en la DB (columna `contenido`): funciona en serverless
sin disco persistente. En desarrollo local además se guarda una copia en
GENERATED_PATH como respaldo legible; si el disco falla, la DB manda.
"""

import os
import re
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy.orm import Session

from app.config import settings
from app.models.solicitud import Solicitud


def _slug(texto: str, max_len: int = 60) -> str:
    texto = unicodedata.normalize("NFKD", texto or "").encode("ascii", "ignore").decode()
    texto = re.sub(r"[^A-Za-z0-9]+", "_", texto).strip("_")
    return (texto or "documento")[:max_len]


def guardar_solicitud(
    db: Session,
    *,
    usuario_id: int,
    tipo: str,
    contenido: bytes,
    nombre_base: str,
    extension: str,
    resumen: dict | None = None,
) -> Solicitud:
    marca = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    nombre_archivo = f"{tipo}_{usuario_id}_{marca}_{_slug(nombre_base)}{extension}"
    ruta = Path(settings.GENERATED_PATH) / nombre_archivo
    if not os.getenv("VERCEL"):
        # Copia local opcional (best-effort): la fuente de verdad es la DB.
        try:
            ruta.parent.mkdir(parents=True, exist_ok=True)
            ruta.write_bytes(contenido)
        except OSError:
            pass
    solicitud = Solicitud(
        usuario_id=usuario_id,
        tipo=tipo,
        nombre_archivo=nombre_archivo,
        ruta_archivo=str(ruta),
        tamano_bytes=len(contenido),
        contenido=contenido,
        resumen=resumen or {},
    )
    db.add(solicitud)
    db.commit()
    db.refresh(solicitud)
    return solicitud


def leer_archivo(solicitud: Solicitud) -> bytes:
    if solicitud.contenido:
        return bytes(solicitud.contenido)
    # Filas viejas (pre-0005): respaldo en disco.
    return Path(solicitud.ruta_archivo).read_bytes()
