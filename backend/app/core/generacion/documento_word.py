import io
import zipfile
from pathlib import Path
from datetime import datetime
from docxtpl import DocxTemplate

TEMPLATES_PATH = Path(__file__).parent.parent.parent.parent / "templates"

def generar_documento(datos: dict) -> bytes:
    template_path = TEMPLATES_PATH / "aprovechamiento_forestal_fixed.docx"
    if not template_path.exists():
        raise FileNotFoundError(f"No existe la plantilla Word: {template_path}")

    tpl = DocxTemplate(_abrir_plantilla(template_path))
    tpl.render(_construir_contexto(datos))
    buf = io.BytesIO()
    tpl.save(buf)
    buf.seek(0)
    return buf.read()


def _abrir_plantilla(template_path: Path) -> io.BytesIO:
    """Open the supplied DOCX, repairing its relative document target if needed."""
    source = template_path.read_bytes()
    output = io.BytesIO()

    with zipfile.ZipFile(io.BytesIO(source)) as original, zipfile.ZipFile(
        output, "w", zipfile.ZIP_DEFLATED
    ) as repaired:
        for item in original.infolist():
            content = original.read(item.filename)
            if item.filename == "word/_rels/document.xml.rels":
                content = content.replace(
                    b'Target="word/document.xml"', b'Target="document.xml"'
                )
            repaired.writestr(item, content)

    output.seek(0)
    return output

def _construir_contexto(d: dict) -> dict:
    return {
        "nombre_titular":       d.get("titular", {}).get("nombre", ""),
        "nit":                  d.get("titular", {}).get("nit", ""),
        "representante_legal":  d.get("titular", {}).get("representante_legal", ""),
        "direccion_titular":    d.get("titular", {}).get("direccion", ""),
        "nombre_predio":        d.get("predio", {}).get("nombre", ""),
        "municipio":            d.get("municipio", {}).get("nombre_oficial", ""),
        "departamento":         d.get("municipio", {}).get("departamento", ""),
        "vereda":               d.get("predio", {}).get("vereda", ""),
        "latitud":              d.get("latitud", {}).get("valor_decimal", ""),
        "longitud":             d.get("longitud", {}).get("valor_decimal", ""),
        "tipo_aprovechamiento": d.get("tipo_aprovechamiento", {}).get("categoria", ""),
        "justificacion":        d.get("aprovechamiento", {}).get("justificacion", ""),
        "volumen_total_m3":     d.get("aprovechamiento", {}).get("volumen_total", ""),
        "especies":             d.get("especies", []),
        "nombre_autoridad":     d.get("autoridad", {}).get("nombre", ""),
        "sigla_autoridad":      d.get("autoridad", {}).get("sigla", ""),
        "fecha_generacion":     datetime.now().strftime("%d de %B de %Y"),
        "referencia_legal":     "Decreto 1076 de 2015 · Decreto 1791 de 1996 · Ley 99 de 1993",
    }