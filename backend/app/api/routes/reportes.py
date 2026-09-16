"""Reportes agregados para el panel de administración.

La agregación temporal se hace en Python para no depender del dialecto
(Postgres en producción, SQLite en tests). Los volúmenes son bajos.
"""

from collections import Counter
from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.seguridad import require_admin
from app.database import get_db
from app.models.solicitud import Solicitud
from app.models.usuario import Usuario

router = APIRouter(prefix="/reportes", tags=["Reportes"])

# Etiqueta legible por tipo de documento
TIPO_LABEL = {
    "fun": "Formato Único Nacional (FUN)",
    "formulario": "Documento Técnico (Word)",
    "sda": "SDA · Formatos F1/F2/F3",
    "corpoboyaca": "Corpoboyacá · Formatos FGR-06/FGR-29",
    "f1": "SDA · PM04-PR30-F1 (solicitud)",
    "f2": "SDA · PM04-PR30-F2 (ficha silvicultural)",
    "f3": "SDA · PM04-PR30-F3 (ficha técnica)",
    "fg1": "Corpoboyacá · FGR-06 (inventario)",
    "fg2": "Corpoboyacá · FGR-29 (costos)",
}


def _label_tipo(tipo: str) -> str:
    return TIPO_LABEL.get(tipo, tipo)


@router.get("/resumen")
def resumen(
    db: Session = Depends(get_db),
    _admin: Usuario = Depends(require_admin),
) -> dict:
    """Agregados generales listos para el módulo de reportes del panel."""

    solicitudes = db.scalars(select(Solicitud)).all()
    total_solicitudes = len(solicitudes)
    total_bytes = sum(s.tamano_bytes or 0 for s in solicitudes)
    total_usuarios = len(db.scalars(select(Usuario)).all())

    por_tipo = dict(Counter(s.tipo or "otro" for s in solicitudes))

    por_mes: dict[str, int] = {}
    for s in solicitudes:
        if s.creado_en is None:
            continue
        clave = s.creado_en.strftime("%Y-%m")
        por_mes[clave] = por_mes.get(clave, 0) + 1
    por_mes = dict(sorted(por_mes.items()))

    # Actividad por día (últimos 30 días, sin depender de fecha de ejecución de tests)
    por_dia: dict[str, int] = {}
    for s in solicitudes:
        if s.creado_en is None:
            continue
        clave = s.creado_en.date().isoformat()
        por_dia[clave] = por_dia.get(clave, 0) + 1
    actividad_reciente = [
        {"fecha": f, "total": t}
        for f, t in sorted(por_dia.items(), reverse=True)[:30]
    ]
    actividad_reciente.reverse()

    # Top usuarios por volumen
    top_usuarios = _top_usuarios(db)

    return {
        "totales": {
            "solicitudes": total_solicitudes,
            "usuarios": total_usuarios,
            "bytes": total_bytes,
        },
        "por_tipo": por_tipo,
        "por_mes": por_mes,
        "top_usuarios": top_usuarios,
        "actividad_reciente": actividad_reciente,
        "tipos_disponibles": [{"tipo": t, "label": _label_tipo(t)} for t in sorted(por_tipo)],
        "generado_en": datetime.now(timezone.utc).isoformat(),
    }


def _top_usuarios(db: Session) -> list[dict]:
    conteo: dict[int, dict] = {}
    solicitudes = db.scalars(select(Solicitud)).all()
    for s in solicitudes:
        u = db.get(Usuario, s.usuario_id)
        item = conteo.setdefault(
            s.usuario_id,
            {
                "usuario_id": s.usuario_id,
                "nombre": getattr(u, "nombre", "") or "",
                "email": getattr(u, "email", "") or "",
                "total": 0,
            },
        )
        item["total"] += 1
    top = sorted(conteo.values(), key=lambda x: x["total"], reverse=True)[:10]
    return top


@router.get("/detalle")
def detalle(
    usuario_id: int | None = None,
    tipo: str | None = None,
    fecha_desde: str | None = None,
    fecha_hasta: str | None = None,
    db: Session = Depends(get_db),
    _admin: Usuario = Depends(require_admin),
) -> dict:
    """Listado detallado de documentos con filtros por usuario, tipo y fecha.

    Cada registro lleva `detalle` con los campos relevantes según su tipo.
    """
    consulta = select(Solicitud).order_by(Solicitud.creado_en.desc(), Solicitud.id.desc())
    if usuario_id is not None:
        consulta = consulta.where(Solicitud.usuario_id == usuario_id)
    if tipo:
        consulta = consulta.where(Solicitud.tipo == tipo)

    filas = list(db.scalars(consulta))

    # filtros de fecha (aplicados en Python; formato YYYY-MM-DD)
    if fecha_desde:
        desde = _parse_fecha(fecha_desde)
        if desde:
            filas = [s for s in filas if s.creado_en and s.creado_en.date() >= desde]
    if fecha_hasta:
        hasta = _parse_fecha(fecha_hasta)
        if hasta:
            filas = [s for s in filas if s.creado_en and s.creado_en.date() <= hasta]

    registros = []
    for s in filas:
        u = db.get(Usuario, s.usuario_id)
        registros.append({
            "id": s.id,
            "usuario_id": s.usuario_id,
            "usuario_nombre": getattr(u, "nombre", "") or "",
            "usuario_email": getattr(u, "email", "") or "",
            "tipo": s.tipo,
            "tipo_label": _label_tipo(s.tipo),
            "nombre_archivo": s.nombre_archivo,
            "tamano_bytes": s.tamano_bytes,
            "creado_en": s.creado_en.isoformat() if s.creado_en else None,
            "detalle": _detalle_por_tipo(s.tipo, s.resumen or {}),
        })

    return {
        "total": len(registros),
        "filtros": {
            "usuario_id": usuario_id,
            "tipo": tipo,
            "fecha_desde": fecha_desde,
            "fecha_hasta": fecha_hasta,
        },
        "registros": registros,
        "generado_en": datetime.now(timezone.utc).isoformat(),
    }


def _parse_fecha(texto: str):
    try:
        return datetime.strptime(texto.strip(), "%Y-%m-%d").date()
    except ValueError:
        return None


def _detalle_por_tipo(tipo: str, resumen: dict) -> dict:
    """Extrae los campos relevantes del `resumen` según el tipo de documento."""
    if tipo == "fun":
        return {
            "nombre": resumen.get("nombre", ""),
            "predio": resumen.get("predio", ""),
            "municipio": resumen.get("municipio", ""),
            "tipo_solicitud": resumen.get("tipo_solicitud", ""),
        }
    if tipo == "formulario":
        return {
            "titular": resumen.get("titular", ""),
            "predio": resumen.get("predio", ""),
            "municipio": resumen.get("municipio", ""),
            "autoridad": resumen.get("autoridad", ""),
        }
    # f1/f2/f3/fg1/fg2: no llevan resumen rico (se generan en frontend).
    return {"origen": resumen.get("origen", "frontend")}