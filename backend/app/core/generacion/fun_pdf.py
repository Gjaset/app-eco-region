"""Rellena el Formato Único Nacional (FUN) sobre la plantilla oficial.

Estrategia: la plantilla `fun_template.pdf` se usa TAL CUAL como fondo
(pixel idéntico al oficial). Este módulo solo:
  1. limpia con rectángulos blancos los valores de ejemplo quemados,
  2. redibuja cada checkbox (fondo gris + borde) y marca X según datos,
  3. escribe los textos en las líneas/celdas con ajuste de tamaño.

Coordenadas en puntos PDF, origen abajo-izquierda, página de 612x1008.
Medidas calibradas por visión + detección sobre la plantilla real.
"""

import io
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas

from app.config import settings

PAGE_W, PAGE_H = 612, 1008
BOX_FILL = HexColor("#E7E6E6")
BOX_BORDER = HexColor("#404040")
INK = HexColor("#000000")


def _template_path() -> Path:
    candidates = [
        Path(settings.TEMPLATES_PATH) / "fun_template.pdf",
        Path(__file__).resolve().parent.parent.parent.parent / "templates" / "fun_template.pdf",
    ]
    for path in candidates:
        if path.exists():
            return path
    raise FileNotFoundError(
        "No se encontró fun_template.pdf (buscado en "
        f"{', '.join(str(c) for c in candidates)})"
    )


# (pagina, cx, cy, campo, valor_esperado) — cy en origen abajo
CHECKS: list[tuple[int, float, float, str, str]] = [
    (0, 162, 801, "tipoSolicitud", "nueva"),
    (0, 221, 801, "tipoSolicitud", "prorroga"),
    (0, 134, 756, "tipoPersona", "natural"),
    (0, 214, 756, "tipoPersona", "juridicaPublica"),
    (0, 296, 756, "tipoPersona", "juridicaPrivada"),
    (0, 135, 714, "tipoIdentificacion", "CC"),
    (0, 183, 714, "tipoIdentificacion", "CE"),
    (0, 231, 714, "tipoIdentificacion", "PA"),
    (0, 280, 714, "tipoIdentificacion", "NIT"),
    (0, 135, 651, "apoderadoTipoIdentificacion", "CC"),
    (0, 179, 651, "apoderadoTipoIdentificacion", "CE"),
    (0, 222, 651, "apoderadoTipoIdentificacion", "PA"),
    (0, 84, 609, "calidadPredio", "propietario"),
    (0, 152, 609, "calidadPredio", "poseedor"),
    (0, 212, 609, "calidadPredio", "tenedor"),
    (0, 278, 609, "calidadPredio", "ocupante"),
    (0, 340, 609, "calidadPredio", "autorizado"),
    (0, 411, 609, "calidadPredio", "enteTerritorial"),
    (0, 116, 588, "calidadPredio", "consejoComunitario"),
    (0, 216, 588, "calidadPredio", "resguardoIndigena"),
    (0, 261, 590, "calidadPredio", "otro"),
    (0, 132, 547, "tipoPredio", "publico"),
    (0, 192, 547, "tipoPredio", "colectivo"),
    (0, 246, 547, "tipoPredio", "privado"),
    (0, 170, 295, "modoAdquirirDerecho", "permisoPublico"),
    (0, 235, 295, "modoAdquirirDerecho", "asociacionPublico"),
    (0, 326, 295, "modoAdquirirDerecho", "concesionForestalPublico"),
    (0, 226, 273, "modoAdquirirDerecho", "autorizacionPrivadaColectiva"),
    (0, 172, 213, "categoriaProducto", "maderables"),
    (0, 332, 169, "categoriaProducto", "floraSilvestreNoMaderables"),
    (0, 255, 192, "claseAprovechamientoMaderables", "persistente"),
    (0, 306, 192, "claseAprovechamientoMaderables", "unico"),
    (0, 370, 192, "claseAprovechamientoMaderables", "domestico"),
    (0, 484, 192, "claseAprovechamientoMaderables", "manejoForestalUnificado"),
    (0, 248, 150, "claseManejoSostenible", "domestico"),
    (0, 320, 150, "claseManejoSostenible", "persistente"),
    (1, 119, 841, "categoriaPersistente", "pequenos"),
    (1, 182, 841, "categoriaPersistente", "medianos"),
    (1, 247, 841, "categoriaPersistente", "grandes"),
    (1, 113, 799, "categoriaProducto", "arbolesAislados"),
    (1, 142, 776, "categoriaProducto", "guadualesBambusales"),
    (1, 68, 736, "tipoAprovechamientoGuaduales", "tipo1"),
    (1, 117, 736, "tipoAprovechamientoGuaduales", "tipo2"),
    (1, 251, 736, "tipoAprovechamientoGuaduales", "cambioUsoSuelo"),
    (1, 360, 736, "tipoAprovechamientoGuaduales", "establecimientoManejo"),
    (2, 117, 606, "tipoCoordenadas", "planar"),
    (2, 231, 606, "tipoCoordenadas", "geografica"),
    (2, 315, 787, "urbanoRural", "urbano"),
    (2, 369, 787, "urbanoRural", "rural"),
    (3, 244, 790, "metodoAprovechamiento", "mecanico"),
    (3, 298, 790, "metodoAprovechamiento", "manual"),
    (3, 383, 790, "metodoAprovechamiento", "mecanicoManual"),
    (3, 275, 366, "arbolesAisladosUbicacion", "dentroCoberturaBosque"),
    (3, 274, 253, "arbolesAisladosUbicacion", "fueraCoberturaBosque"),
    (3, 236, 231, "arbolesAisladosUbicacion", "talaPodaEmergenciaUrbana"),
    (3, 210, 121, "arbolesAisladosUbicacion", "obraPublicaPrivadaUrbana"),
    (3, 142, 321, "estadoIndividuo", "caidoCausasNaturales"),
    (3, 146, 299, "estadoIndividuo", "muertoCausasNaturales"),
    (3, 154, 277, "estadoIndividuo", "razonesFitosanitarias"),
    (3, 138, 186, "estadoIndividuo", "caido"),
    (3, 191, 186, "estadoIndividuo", "muerto"),
    (3, 251, 186, "estadoIndividuo", "enfermo"),
    (3, 180, 165, "causaPerjuicio", "estabilidadSuelos"),
    (3, 262, 165, "causaPerjuicio", "canalAgua"),
    (3, 416, 165, "causaPerjuicio", "obrasInfraestructuraEdificaciones"),
    (3, 123, 143, "causaPerjuicio", "otro"),
    (3, 137, 57, "actividadInfraestructura", "construccionRealizacion"),
    (3, 216, 57, "actividadInfraestructura", "remodelacion"),
    (3, 293, 57, "actividadInfraestructura", "ampliacion"),
    (3, 361, 57, "actividadInfraestructura", "instalacion"),
    (5, 174, 800, "notificacionElectronica", "si"),
    (5, 53, 788, "notificacionElectronica", "no"),
]

# Limpieza de valores de ejemplo quemados: (pagina, x0, y_top, x1, y_bot) origen ARRIBA
WIPES_TOP: list[tuple[int, float, float, float, float]] = [
    (0, 44, 492, 354, 511),    # $ 20.568.708.950 (conserva el signo $)
    (0, 87, 514, 582, 529),    # Valor en letras L1
    (0, 36, 528, 549, 540),    # Valor en letras L2 (subrayado)
    (3, 58, 345.4, 558, 357.6),  # especie ej. fila 1 (rejilla incluida, se redibuja)
    (3, 58, 357.2, 558, 369.4),  # especie ej. fila 2 (rejilla incluida, se redibuja)
    (3, 98, 464, 555, 482),    # Cantidad Total 48,4...
    (3, 36, 534, 251, 556),    # rótulo uso + Donación (el rótulo se redibuja)
]

# Líneas a redibujar tras limpiar (página, x0, x1, y_top)
RELINES_TOP: list[tuple[int, float, float, float]] = [
    (0, 42, 354, 507),    # $ costo
    (0, 88, 580, 527),    # letras L1
    (0, 36, 549, 538),    # letras L2
    (3, 36, 558, 554),    # uso L1 (el rótulo de arriba se redibuja)
    (3, 96.7, 557.6, 482.3),  # total fila inferior
]

# Campos de texto: (pagina, x, y_linea_abajo, ancho_max, campo)
FIELDS: list[tuple[int, float, float, float, str]] = [
    (0, 118, 731, 464, "nombreRazonSocial"),
    (0, 406, 711, 176, "numeroIdentificacion"),
    (0, 67, 668, 518, "apoderadoNombre"),
    (0, 325, 647, 132, "apoderadoNumeroIdentificacion"),
    (0, 470, 647, 115, "apoderadoTP"),
    (0, 333, 584, 119, "calidadPredioOtro"),
    (0, 52, 501, 300, "costoProyecto"),
    (0, 150, 423, 197, "numeroExpediente"),
    (0, 36, 388, 185, "numeroActoAdministrativo"),
    (0, 45, 104, 316, "ingresosMensualesSMLMV"),
    (2, 101, 803, 175, "nombrePredio"),
    (2, 327, 803, 107, "superficieHa"),
    (2, 105, 781, 175, "direccionPredio"),
    (2, 85, 761, 193, "departamento"),
    (2, 313, 761, 103, "municipio"),
    (2, 444, 761, 127, "vereda"),
    (2, 156, 740, 414, "matriculaInmobiliaria"),
    (2, 250, 719, 320, "cedulaCatastral"),
    (3, 227, 272, 341, "razonesFitosanitariasEspecificar"),
    (3, 135, 138, 119, "causaPerjuicioOtro"),
    (3, 474, 52, 91, "similaresEspecificar"),
    (5, 254, 797, 164, "correoElectronico"),
    (5, 465, 797, 115, "telefonos"),
    (5, 154, 783, 218, "direccionNotificacion"),
    (5, 414, 783, 168, "municipioNotificacion"),
    (5, 197, 770, 172, "nombreCentroPobladoVeredaCorregimiento"),
    (5, 428, 770, 156, "departamentoNotificacion"),
    (5, 39, 710, 257, "nombreFirmante"),
    (5, 363, 710, 170, "firmaTexto"),
]

# Letras del costo en 2 líneas: (x, y_abajo, ancho)
COSTO_LETRAS = [(90, 481, 490), (36, 470, 513)]
# Rótulo que se pisa al limpiar "Donación": se redibuja condensado
USO_LABEL = ("Indique el uso que se pretende dar a los productos a obtener:", 36, 544, 215)
# Uso de productos en 4 líneas
USO_LINES = [(58, 454, 500), (58, 443, 500), (58, 431, 500), (58, 418, 500)]

# Tabla especies pág.4 (índice 3): columnas y filas (origen ARRIBA para filas)
SP_COLS = [58.2, 96.7, 164.4, 224.5, 307.9, 387.0, 461.1, 514.8, 557.6]
SP_ROW0_TOP = 345.2
SP_ROW_H = 11.85
SP_MAX_ROWS = 10
# Tabla planas pág.3 (índice 2)
PL_COLS = [83.3, 150.7, 353.6, 532.9]
PL_ROW0_TOP = 503.0
PL_ROW_H = 12.5
PL_MAX_ROWS = 13
# Tabla geográficas pág.3
GEO_COLS = [82.2, 122.6, 172.1, 228.8, 285.5, 356.3, 419.8, 483.6, 534.0]
GEO_ROW0_TOP = 683.1
GEO_ROW_H = 11.6
GEO_MAX_ROWS = 12
GEO_ORIGEN = (130, 822.6, 833.2)  # x, y_top, y_bot


def _fit_font(text: str, font: str, size: float, max_w: float, canvas_obj) -> float:
    while size > 6.0 and canvas_obj.stringWidth(text, font, size) > max_w:
        size -= 0.5
    return size


def _draw_checkbox(c: canvas.Canvas, cx: float, cy: float, checked: bool) -> None:
    w, h = 17.0, 9.5
    c.setFillColor(BOX_FILL)
    c.setStrokeColor(BOX_BORDER)
    c.setLineWidth(0.7)
    c.roundRect(cx - w / 2, cy - h / 2, w, h, 1.2, fill=0, stroke=1)
    c.setFillColor(BOX_FILL)
    c.setStrokeColor(BOX_FILL)
    c.roundRect(cx - w / 2 + 1.1, cy - h / 2 + 1.1, w - 2.2, h - 2.2, 0.8, fill=1, stroke=0)
    if checked:
        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 10.5)
        c.drawCentredString(cx, cy - 3.7, "X")


def _draw_field(c: canvas.Canvas, x: float, y_line: float, text: str, max_w: float, size: float = 9.0) -> None:
    text = (text or "").strip()
    if not text:
        return
    size = _fit_font(text, "Helvetica", size, max_w, c)
    c.setFillColor(INK)
    c.setFont("Helvetica", size)
    c.drawString(x, y_line + 2.5, text)


def _wrap(text: str, font: str, size: float, max_w: float, canvas_obj) -> list[str]:
    words = text.split()
    lines, current = [], ""
    for word in words:
        trial = f"{current} {word}".strip()
        if canvas_obj.stringWidth(trial, font, size) <= max_w:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines or [""]


def _draw_narrow(c: canvas.Canvas, x: float, y_base_bottom: float, text: str,
                 size: float, target_w: float) -> None:
    """Redibuja un rótulo Arial-Narrow con Helvetica condensada al mismo ancho."""
    w = c.stringWidth(text, "Helvetica-Bold", size)
    scale = target_w / w if w else 1.0
    t = c.beginText()
    t.setFont("Helvetica-Bold", size)
    t.setTextTransform(scale, 0, 0, 1, x, y_base_bottom)
    t.textOut(text)
    c.setFillColor(INK)
    c.drawText(t)


def generar_fun_pdf(datos: dict) -> bytes:
    """Rellena la plantilla FUN con `datos` (dict plano) y devuelve el PDF."""
    template = _template_path()

    overlay = io.BytesIO()
    c = canvas.Canvas(overlay, pagesize=(PAGE_W, PAGE_H))

    pages: dict[int, list] = {}
    for idx, (pg, cx, cy, field, value) in enumerate(CHECKS):
        pages.setdefault(pg, []).append(("check", (cx, cy, field, value)))
    for pg, x0, yt, x1, yb in WIPES_TOP:
        pages.setdefault(pg, []).append(("wipe", (x0, PAGE_H - yt, x1, PAGE_H - yb)))
    for pg, x0, x1, yt in RELINES_TOP:
        pages.setdefault(pg, []).append(("reline", (x0, x1, PAGE_H - yt)))
    for pg, x, yl, mw, field in FIELDS:
        pages.setdefault(pg, []).append(("field", (x, yl, mw, field)))
    pages.setdefault(0, []).append(("costo_letras", ()))
    pages.setdefault(3, []).append(("especies", ()))
    pages.setdefault(3, []).append(("uso", ()))
    pages.setdefault(2, []).append(("coords", ()))

    reader_probe = PdfReader(str(template))
    n_pages = len(reader_probe.pages)

    for pg in range(n_pages):
        # Limpieza primero
        for kind, args in pages.get(pg, []):
            if kind == "wipe":
                x0, y0, x1, y1 = args
                c.setFillColor(HexColor("#FFFFFF"))
                c.setStrokeColor(HexColor("#FFFFFF"))
                c.rect(x0, y1, x1 - x0, y0 - y1, fill=1, stroke=0)
        # Redibujar líneas borradas
        for kind, args in pages.get(pg, []):
            if kind == "reline":
                x0, x1, y = args
                c.setStrokeColor(HexColor("#000000"))
                c.setLineWidth(0.6)
                c.line(x0, y, x1, y)
        # Rejilla de especies filas 1-2 (pág.4): se limpió con líneas incluidas
        if pg == 3:
            c.setStrokeColor(HexColor("#000000"))
            c.setLineWidth(0.6)
            for yt in (345.5, 357.4, 369.2):
                y = PAGE_H - yt
                c.line(SP_COLS[0], y, SP_COLS[-1], y)
            for xv in SP_COLS:
                c.line(xv, PAGE_H - 369.2, xv, PAGE_H - 345.5)
            # Rótulo pisado por la limpieza de "Donación"
            label, lx, lyt, lw = USO_LABEL
            _draw_narrow(c, lx, PAGE_H - lyt, label, 9.0, lw)
        # Checkboxes
        for kind, args in pages.get(pg, []):
            if kind == "check":
                cx, cy, field, value = args
                selected = str(datos.get(field, "") or "") == value
                _draw_checkbox(c, cx, cy, selected)
        # Textos simples
        for kind, args in pages.get(pg, []):
            if kind == "field":
                x, yl, mw, field = args
                _draw_field(c, x, yl, str(datos.get(field, "") or ""), mw)
        # Costo en letras (2 líneas, ajuste por línea)
        if pg == 0:
            text = str(datos.get("costoProyectoLetras", "") or "").strip()
            if text:
                size = 9.0
                (x0, yl0, mw0), (_x1, _yl1, mw1) = COSTO_LETRAS
                lines = _wrap(text, "Helvetica", size, mw0, c)
                while len(lines) > 2 and size > 6.0:
                    size -= 0.5
                    lines = _wrap(text, "Helvetica", size, mw0, c)
                first, rest = lines[0], " ".join(lines[1:])
                first = first.strip()
                size0 = _fit_font(first, "Helvetica", size, mw0, c)
                size1 = _fit_font(rest, "Helvetica", size, mw1, c)
                c.setFillColor(INK)
                c.setFont("Helvetica", size0)
                c.drawString(x0, yl0 + 2.5, first)
                if rest.strip():
                    c.setFont("Helvetica", size1)
                    c.drawString(_x1, _yl1 + 2.5, rest.strip())
        # Especies + total
        if pg == 3:
            especies = datos.get("especies") or []
            if isinstance(especies, dict):
                especies = list(especies.values())
            c.setFillColor(INK)
            for i, esp in enumerate(especies[:SP_MAX_ROWS]):
                if not isinstance(esp, dict):
                    continue
                y_top = SP_ROW0_TOP + i * SP_ROW_H
                y_base = PAGE_H - y_top - 6.6
                vals = [
                    str(esp.get("cantidad", "") or ""),
                    str(esp.get("unidadMedida", "") or ""),
                    str(esp.get("nombreComun", "") or ""),
                    str(esp.get("nombreCientifico", "") or ""),
                    str(esp.get("parteAprovechada", "") or ""),
                    str(esp.get("habitos", "") or ""),
                    str(esp.get("vedaNacionalRegional", "") or ""),
                    str(esp.get("categoriaAmenaza", "") or ""),
                ]
                for col, val in enumerate(vals):
                    x0, x1 = SP_COLS[col] + 2, SP_COLS[col + 1] - 2
                    val = val.strip()
                    if not val:
                        continue
                    size = _fit_font(val, "Helvetica", 8.5, x1 - x0, c)
                    c.setFont("Helvetica", size)
                    if col == 0:
                        c.drawCentredString((x0 + x1) / 2, y_base, val)
                    else:
                        c.drawString(x0, y_base, val)
            # Total = suma cantidades + unidad predominante
            total = 0.0
            unidad = ""
            for esp in especies[:SP_MAX_ROWS]:
                if not isinstance(esp, dict):
                    continue
                try:
                    total += float(str(esp.get("cantidad", "") or "0").replace(",", "."))
                    if not unidad:
                        unidad = str(esp.get("unidadMedida", "") or "")
                except ValueError:
                    continue
            if especies:
                total_txt = f"{str(round(total, 2)).replace('.', ',')} {unidad}".strip()
                size = _fit_font(total_txt, "Helvetica", 10, 450, c)
                c.setFont("Helvetica", size)
                c.drawString(100, PAGE_H - 482.3 + 3.5, total_txt)
        # Uso de productos (4 líneas)
        if pg == 3:
            text = str(datos.get("usoProductos", "") or "").strip()
            if not text:
                primer_uso = ""
                for esp in (datos.get("especies") or [])[:1]:
                    if isinstance(esp, dict):
                        primer_uso = str(esp.get("usoProductos", "") or "")
                text = primer_uso.strip()
            if text:
                wrapped = _wrap(text, "Helvetica", 9.0, 500, c)
                c.setFillColor(INK)
                c.setFont("Helvetica", 9.0)
                for (x, yl, _mw), line in zip(USO_LINES, wrapped[:4]):
                    c.drawString(x, yl + 2.5, line)
        # Coordenadas
        if pg == 2:
            c.setFillColor(INK)
            planar = datos.get("coordenadasPlanar") or []
            for i, row in enumerate(planar[:PL_MAX_ROWS]):
                if not isinstance(row, dict):
                    continue
                y_top = PL_ROW0_TOP + i * PL_ROW_H
                y_base = PAGE_H - y_top - 7.2
                for col, key in enumerate(("punto", "x", "y")):
                    val = str(row.get(key, "") or "").strip()
                    if not val:
                        continue
                    x0, x1 = PL_COLS[col] + 2, PL_COLS[col + 1] - 2
                    size = _fit_font(val, "Helvetica", 8.5, x1 - x0, c)
                    c.setFont("Helvetica", size)
                    c.drawCentredString((x0 + x1) / 2, y_base, val)
            geo = datos.get("coordenadasGeografica") or []
            for i, row in enumerate(geo[:GEO_MAX_ROWS]):
                if not isinstance(row, dict):
                    continue
                y_top = GEO_ROW0_TOP + i * GEO_ROW_H
                y_base = PAGE_H - y_top - 6.8
                lat = f"{row.get('gradosLat', '') or ''} {row.get('latitud', '') or ''}".strip()
                lon = f"{row.get('gradosLong', '') or ''} {row.get('longitud', '') or ''}".strip()
                vals = [
                    str(row.get("punto", "") or ""),
                    lat,
                    str(row.get("minutosLat", "") or ""),
                    str(row.get("segundosLat", "") or ""),
                    lon,
                    str(row.get("minutosLong", "") or ""),
                    str(row.get("segundosLong", "") or ""),
                    str(row.get("altitud", "") or ""),
                ]
                for col, val in enumerate(vals):
                    val = val.strip()
                    if not val:
                        continue
                    x0, x1 = GEO_COLS[col] + 2, GEO_COLS[col + 1] - 2
                    size = _fit_font(val, "Helvetica", 8.0, x1 - x0, c)
                    c.setFont("Helvetica", size)
                    c.drawCentredString((x0 + x1) / 2, y_base, val)
            origen = str(datos.get("coordenadasGeografica_origen", "") or "").strip()
            if not origen and geo and isinstance(geo[0], dict):
                origen = str(geo[0].get("origen", "") or "").strip()
            if origen:
                x0, yt, yb = GEO_ORIGEN
                size = _fit_font(origen, "Helvetica", 8.5, 400, c)
                c.setFont("Helvetica", size)
                c.drawString(x0, PAGE_H - yb + 3.5, origen)
        c.showPage()
    c.save()
    overlay.seek(0)

    base = PdfReader(str(template))
    over = PdfReader(overlay)
    writer = PdfWriter()
    for i, page in enumerate(base.pages):
        if i < len(over.pages):
            page.merge_page(over.pages[i])
        writer.add_page(page)
    out = io.BytesIO()
    writer.write(out)
    return out.getvalue()
