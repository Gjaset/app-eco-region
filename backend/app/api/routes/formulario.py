import io
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.normalizacion import municipios, especies, coordenadas, tipo_aprovechamiento
from app.core.reglas import car_selector
from app.core.reglas import requisitos
from app.core.validacion.fun import validar_fun
from app.core.generacion import documento_word
from app.core.generacion.fun_pdf import generar_fun_pdf
from app.core.seguridad import get_current_user
from app.core.solicitudes import guardar_solicitud
from app.database import get_db
from app.models.usuario import Usuario
from app.schemas.formulario import FormularioCompleto
from app.schemas.fun import FormularioFUN

router = APIRouter(prefix="/formulario", tags=["Formulario"])

@router.post("/normalizar")
async def normalizar(datos: FormularioCompleto):
    muni = municipios.normalizar_municipio(datos.predio.municipio)
    lat = coordenadas.normalizar_coordenada(datos.predio.latitud)
    lng = coordenadas.normalizar_coordenada(datos.predio.longitud)
    tipo = tipo_aprovechamiento.clasificar_tipo(datos.aprovechamiento.tipo)
    auth = car_selector.seleccionar_autoridad(muni.get("codigo_dane", ""))
    selected_authorities = {
        "CAR": {"nombre": "CAR Cundinamarca", "sigla": "CAR"},
        "SDA": {"nombre": "Secretaría Distrital de Ambiente", "sigla": "SDA"},
        "CORPOBOYACA": {"nombre": "Corpoboyacá", "sigla": "CORPOBOYACA"},
    }
    if datos.autoridad_seleccionada:
        selected = selected_authorities.get(datos.autoridad_seleccionada)
        if selected is None:
            raise HTTPException(
                status_code=422,
                detail="La autoridad seleccionada no está disponible.",
            )
        auth = selected
    checklist = requisitos.obtener_requisitos(auth.get("sigla", ""))
    esps = [
        {**e.model_dump(), "normalizacion": especies.normalizar_especie(e.nombre, datos.predio.municipio)}
        for e in datos.especies
    ]
    especies_requieren_revision = any(
        especie.get("normalizacion", {}).get("requiere_revision")
        or especie.get("normalizacion", {}).get("error")
        for especie in esps
    )
    requiere_revision = any([
        muni.get("requiere_confirmacion"),
        lat.get("error"),
        not lat.get("en_colombia", False),
        lng.get("error"),
        not lng.get("en_colombia", False),
        tipo.get("error"),
        auth.get("error"),
        checklist.get("error"),
        especies_requieren_revision,
    ])
    listo = not requiere_revision or datos.confirmar_revision
    return {"municipio": muni, "latitud": lat, "longitud": lng,
            "tipo_aprovechamiento": tipo, "autoridad": auth,
            "requisitos": checklist,
            "especies": esps, "listo_para_generar": listo,
            "requiere_revision": requiere_revision,
            "revision_confirmada": datos.confirmar_revision}

@router.post("/generar-documento")
async def generar_documento(
    datos: FormularioCompleto,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    norm = await normalizar(datos)
    if not norm["listo_para_generar"]:
        raise HTTPException(422, "Hay campos pendientes de confirmación.")
    doc_bytes = documento_word.generar_documento({
        **norm,
        "titular": datos.titular.model_dump(),
        "predio": datos.predio.model_dump(),
        "aprovechamiento": datos.aprovechamiento.model_dump(),
    })
    guardar_solicitud(
        db,
        usuario_id=usuario.id,
        tipo="formulario",
        contenido=doc_bytes,
        nombre_base=datos.titular.nombre or datos.predio.nombre or "aprovechamiento",
        extension=".docx",
        resumen={
            "titular": datos.titular.nombre,
            "predio": datos.predio.nombre,
            "municipio": datos.predio.municipio,
            "autoridad": norm.get("autoridad", {}).get("sigla"),
        },
    )
    return StreamingResponse(
        io.BytesIO(doc_bytes),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": "attachment; filename=aprovechamiento_forestal.docx"},
    )

@router.post("/fun/exportar-pdf")
async def exportar_fun_pdf(
    datos: FormularioFUN,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Rellena la plantilla oficial FUN (PDF idéntico) y la devuelve lista."""
    errores = validar_fun(datos.model_dump())
    if errores:
        raise HTTPException(
            status_code=422,
            detail={
                "message": "El formulario tiene campos pendientes o inconsistentes.",
                "errores": errores,
            },
        )
    try:
        pdf_bytes = generar_fun_pdf(datos.model_dump())
    except FileNotFoundError as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    guardar_solicitud(
        db,
        usuario_id=usuario.id,
        tipo="fun",
        contenido=pdf_bytes,
        nombre_base=datos.nombreRazonSocial or datos.nombrePredio or "formato_unico",
        extension=".pdf",
        resumen={
            "nombre": datos.nombreRazonSocial,
            "predio": datos.nombrePredio,
            "municipio": datos.municipio,
            "tipo_solicitud": datos.tipoSolicitud,
        },
    )
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=formato_unico_nacional.pdf"},
    )