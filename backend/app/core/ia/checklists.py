"""Checklists de campos que cada formato debe tener diligenciados.

Se usan como lista de verificación en el prompt del validador IA. Las etiquetas
reflejan los campos que aparecen en las plantillas oficiales.
"""

CHECKLISTS: dict[str, dict] = {
    "f1": {
        "nombre": "F1 · Solicitud de Manejo o Aprovechamiento Forestal (SDA)",
        "autoridad": "Secretaría Distrital de Ambiente (SDA)",
        "campos": [
            "Tipo de actuación / trámite solicitado",
            "Identificación del solicitante o interesado (nombre completo, tipo y número de documento, correo y teléfono)",
            "Predio: nombre y folio de matrícula o identificación",
            "Municipio y código DANE",
            "Ubicación/vereda, dirección y coordenadas del predio",
            "Área del predio y área de intervención",
            "Detalle del aprovechamiento o intervención (especies, número de individuos, productos a obtener, número de viajes)",
            "Registro como aprovechador / expedición del visto y procedencia",
            "Observaciones y firma del solicitante",
        ],
    },
    "f2": {
        "nombre": "F2 · Recolección de Información Silvicultural, Individuo Ficha 1 (SDA)",
        "autoridad": "Secretaría Distrital de Ambiente (SDA)",
        "campos": [
            "Radicado y fecha",
            "Identificación del individuo arbóreo (especie, nombre científico, número de individuo)",
            "Municipio y ubicación exacta del individuo",
            "Diámetro a la altura del pecho (CAP/DAP) y altura total/comercial",
            "Estado físico y fitosanitario",
            "Localización del sitio de la población o individuo",
            "Responsable y firma del diligenciamiento",
        ],
    },
    "f3": {
        "nombre": "F3 · Ficha Técnica de Registro (Ficha 2, SDA)",
        "autoridad": "Secretaría Distrital de Ambiente (SDA)",
        "campos": [
            "Radicado No. y fecha de visita técnica",
            "Especie (nombre común) y nombre científico",
            "Número y código del árbol (árbol N.º y Cod.SIGAU)",
            "Localización exacta del árbol y sitio de visita",
            "Solicitante y dirección/cédula o NIT",
            "Estado físico y sanitario, causas de la intervención",
            "P.A.P. (m), altura total y comercial, volumen comercial",
            "Concepto técnico y firma del profesional forestal",
        ],
    },
    "fg1": {
        "nombre": "FGR-06 · Registro de Información para Aprovechamiento (Corpoboyacá)",
        "autoridad": "Corpoboyacá",
        "campos": [
            "Identificación del titular o solicitante (nombre, documento, contacto)",
            "Información del predio (nombre, matrícula, municipio, coordenadas)",
            "Área total y área de intervención",
            "Listado de individuos o especies a aprovechar (número y volumen estimado)",
            "Origen y destino o uso del producto",
            "Fecha y firma del responsable o profesional forestal",
        ],
    },
    "fg2": {
        "nombre": "FGR-29 · Declaración de Costos de Inversión y Operación (Corpoboyacá)",
        "autoridad": "Corpoboyacá",
        "campos": [
            "Identificación del titular y del predio",
            "Detalle de costos de inversión: compra de tierras, estudios, infraestructura, otros",
            "Detalle de costos de operación: mano de obra, maquinaria, transporte, mantenimiento",
            "Total de costos y fecha del periodo reportado",
            "Firma del representante legal y responsable del reporte",
        ],
    },
    "fun": {
        "nombre": "Formato Único Nacional para Aprovechamiento Forestal",
        "autoridad": "Autoridad ambiental competente (CAR/SDA/Corpoboyacá)",
        "campos": [
            "Sección 1: datos del interesado (tipo de solicitud y de persona, nombre, identificación, contacto)",
            "Apoderado y calidad en que actúa sobre el predio, cuando aplique",
            "Predio: nombre, folio de matrícula, municipio y código DANE",
            "Ubicación: vereda, dirección y coordenadas",
            "Descripción del aprovechamiento: especies e individuos, producto, volumen y número de viajes",
            "Antecedentes y anexos que acompañan la solicitud",
            "Declaraciones juradas y firmas",
        ],
    },
}

# El validador también admite «formulario» con el checklist del FUN.
CHECKLISTS["formulario"] = CHECKLISTS["fun"]

# Páginas unificadas por entidad: el usuario sube cualquier formato de la
# entidad y el validador contrasta contra la unión de sus checklists.
def _combinar(claves: tuple[str, ...], nombre: str, autoridad: str) -> dict:
    campos: list[str] = []
    for clave in claves:
        campos.extend(CHECKLISTS[clave]["campos"])
    return {"nombre": nombre, "autoridad": autoridad, "campos": campos}


CHECKLISTS["sda"] = _combinar(
    ("f1", "f2", "f3"),
    "Formatos PM04-PR30 (F1 / F2 / F3)",
    "Secretaría Distrital de Ambiente (SDA)",
)
CHECKLISTS["corpoboyaca"] = _combinar(
    ("fg1", "fg2"),
    "Formatos FGR-06 / FGR-29",
    "Corpoboyacá",
)


def checklist_para(tipo: str) -> dict:
    return CHECKLISTS.get(
        tipo,
        {
            "nombre": tipo,
            "autoridad": "Autoridad ambiental",
            "campos": [],
        },
    )
