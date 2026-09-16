"""Validación estricta del Formato Único Nacional (FUN) para exportación.

El schema Pydantic (`app.schemas.fun.FormularioFUN`) admite campos parciales
porque también transporta borradores. En cambio, exportar el PDF oficial y
guardar la solicitud exige completitud y coherencia: este validador devuelve
un dict `{campo: mensaje}` (vacío = válido) que el endpoint convierte en 422.
"""

from __future__ import annotations

import re
import unicodedata

try:
    from app.core.normalizacion.municipios import MUNICIPIOS_DANE
except Exception:  # dataset no disponible: se omite solo esa verificación
    MUNICIPIOS_DANE = []

REQUERIDOS = [
    "tipoSolicitud",
    "tipoPersona",
    "nombreRazonSocial",
    "tipoIdentificacion",
    "numeroIdentificacion",
    "calidadPredio",
    "tipoPredio",
    "costoProyecto",
    "costoProyectoLetras",
    "modoAdquirirDerecho",
    "categoriaProducto",
    "metodoAprovechamiento",
    "nombrePredio",
    "superficieHa",
    "direccionPredio",
    "urbanoRural",
    "departamento",
    "municipio",
    "nombreFirmante",
]

# Colombia continental aproximada (margen generoso para no rechazar bordes)
LAT_MIN, LAT_MAX = -5.0, 14.0
LNG_MIN, LNG_MAX = -80.0, -66.0


def _texto(valor: object) -> str:
    return str(valor or "").strip()


def _sin_acentos(texto: str) -> str:
    nfkd = unicodedata.normalize("NFD", texto.lower())
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def _normalizar_nombre(texto: str) -> str:
    texto = _sin_acentos(texto)
    texto = re.sub(r"[^a-z0-9\s]", " ", texto)
    return re.sub(r"\s+", " ", texto).strip()


def parse_moneda(texto: str) -> tuple[int, int] | None:
    """Acepta 1.000.000,00 / 1,000,000.00 / 1000000. Devuelve (enteros, centavos)."""
    limpio = _texto(texto).replace("$", "").replace(" ", "")
    if not limpio:
        return None
    if "," in limpio and "." in limpio:
        # El separador decimal es el último símbolo
        if limpio.rfind(",") > limpio.rfind("."):
            limpio = limpio.replace(".", "").replace(",", ".")
        else:
            limpio = limpio.replace(",", "")
    elif "," in limpio:
        partes = limpio.split(",")
        limpio = limpio.replace(",", "") if len(partes[-1]) == 3 and len(partes) > 2 else limpio.replace(",", ".")
    if not re.fullmatch(r"\d+(\.\d{1,2})?", limpio):
        return None
    enteros_s, _, dec_s = limpio.partition(".")
    return int(enteros_s), int((dec_s + "00")[:2])


def parse_numero(texto: str) -> float | None:
    """Número general con coma o punto decimal (superficie, coordenadas)."""
    limpio = _texto(texto).replace(" ", "")
    if not limpio:
        return None
    if "," in limpio:
        limpio = limpio.replace(".", "").replace(",", ".") if limpio.count(",") == 1 and "." in limpio else limpio.replace(",", ".")
        if limpio.count(".") > 1:
            return None
    try:
        return float(limpio)
    except ValueError:
        return None


# --- Número a letras (pesos colombianos, canónico) ---

_UNIDADES = ["cero", "uno", "dos", "tres", "cuatro", "cinco", "seis", "siete",
             "ocho", "nueve", "diez", "once", "doce", "trece", "catorce", "quince"]
_DIECIS = {16: "dieciseis", 17: "diecisiete", 18: "dieciocho", 19: "diecinueve"}
_VEINTIS = {20: "veinte", 21: "veintiuno", 22: "veintidos", 23: "veintitres",
            24: "veinticuatro", 25: "veinticinco", 26: "veintiseis",
            27: "veintisiete", 28: "veintiocho", 29: "veintinueve"}
_DECENAS = {30: "treinta", 40: "cuarenta", 50: "cincuenta", 60: "sesenta",
            70: "setenta", 80: "ochenta", 90: "noventa"}
_CENTENAS = {100: "cien", 200: "doscientos", 300: "trescientos", 400: "cuatrocientos",
             500: "quinientos", 600: "seiscientos", 700: "setecientos",
             800: "ochocientos", 900: "novecientos"}


def _menor_cien(n: int) -> str:
    if n < 16:
        return _UNIDADES[n]
    if n < 20:
        return _DIECIS[n]
    if n < 30:
        return _VEINTIS[n]
    dec, resto = divmod(n, 10)
    base = _DECENAS[dec * 10]
    return base if resto == 0 else f"{base} y {_UNIDADES[resto]}"


def _menor_mil(n: int) -> str:
    if n < 100:
        return _menor_cien(n)
    if n == 100:
        return "cien"
    cent, resto = divmod(n, 100)
    base = "ciento" if cent == 1 else _CENTENAS[cent * 100]
    return base if resto == 0 else f"{base} {_menor_cien(resto)}"


def _entero_a_letras(n: int) -> str | None:
    if n < 0 or n >= 10**12:
        return None
    if n < 1000:
        return _menor_mil(n)
    if n < 10**6:
        miles, resto = divmod(n, 1000)
        base = "mil" if miles == 1 else f"{_menor_mil(miles)} mil"
        return base if resto == 0 else f"{base} {_menor_mil(resto)}"
    if n < 10**9:
        millones, resto = divmod(n, 10**6)
        base = "un millon" if millones == 1 else f"{_entero_a_letras(millones)} millones"
        if resto == 0:
            return base
        resto_txt = _entero_a_letras(resto)
        return base if resto_txt is None else f"{base} {resto_txt}"
    miles_mill, resto = divmod(n, 10**9)
    base = "mil millones" if miles_mill == 1 else f"{_menor_mil(miles_mill)} mil millones"
    if resto == 0:
        return base
    resto_txt = _entero_a_letras(resto)
    return base if resto_txt is None else f"{base} {resto_txt}"


_RELLENO_LETRAS = {"peso", "pesos", "mcte", "m", "cte", "ct", "moneda", "legal",
                   "colombiana", "colombiano", "colombianos", "exactos", "exacta",
                   "exacto", "son", "de", "la", "suma", "valor", "por"}


def normalizar_letras(texto: str) -> str:
    """Minúsculas sin acentos, sin relleno y con variantes comunes unificadas."""
    t = _normalizar_nombre(texto)
    t = re.sub(r"\bveinte y (\w+)", r"veinti\1", t)
    t = re.sub(r"\bun mil\b", "mil", t)
    t = re.sub(r"\bciento un\b", "ciento uno", t)
    tokens = [tok for tok in t.split() if tok not in _RELLENO_LETRAS]
    return " ".join(tokens)


def letras_a_numero_0_99(texto: str) -> int | None:
    """Convierte palabras de 0-99 a entero (para centavos escritos en letras)."""
    t = normalizar_letras(texto)
    mapa = {v: k for k, v in enumerate(_UNIDADES)}
    mapa.update({v: k for k, v in _DIECIS.items()})
    mapa.update({v: k for k, v in _VEINTIS.items()})
    mapa.update({v: k for k, v in _DECENAS.items()})
    if t in mapa:
        return mapa[t]
    m = re.fullmatch(r"(treinta|cuarenta|cincuenta|sesenta|setenta|ochenta|noventa) y (uno|dos|tres|cuatro|cinco|seis|siete|ocho|nueve)", t)
    if m:
        return mapa[m.group(1)] + mapa[m.group(2)]
    return None


def validar_costo_letras(costo: str, letras: str) -> str | None:
    """Verifica que el valor en letras corresponda al valor numérico."""
    monto = parse_moneda(costo)
    if monto is None:
        return None  # el error de formato ya se reporta en costoProyecto
    enteros, centavos = monto
    esperado_entero = _entero_a_letras(enteros)
    if esperado_entero is None:
        return None  # fuera de rango del conversor: no se puede verificar
    partes = _texto(letras).lower().split("con")
    entero_txt = normalizar_letras(partes[0])
    if entero_txt != esperado_entero:
        return (
            "No coincide con el valor numérico "
            f"(para {enteros:,} debería decir algo como «{esperado_entero} pesos»)."
        )
    if len(partes) > 1:
        cent_txt = _texto(partes[1]).replace("/100", "").replace("centavos", "").replace("centavo", "").strip()
        centavos_txt = _sin_acentos(cent_txt)
        if centavos_txt.isdigit():
            if int(centavos_txt) != centavos:
                return f"Los centavos no coinciden ({centavos:02d}/100)."
        elif centavos_txt:
            num = letras_a_numero_0_99(centavos_txt)
            if num is None or num != centavos:
                return f"Los centavos no coinciden ({centavos:02d}/100)."
        elif centavos != 0:
            return f"Faltan los centavos ({centavos:02d}/100)."
    elif centavos != 0:
        return f"Faltan los centavos ({centavos:02d}/100)."
    return None


# --- Documentos de identidad ---

_PESOS_NIT = [3, 7, 13, 17, 19, 23, 29, 37, 41, 43, 47, 53, 59, 67, 71]


def digito_verificacion_nit(nit: str) -> int:
    total = sum(int(d) * p for d, p in zip(reversed(nit), _PESOS_NIT))
    residuo = total % 11
    return residuo if residuo < 2 else 11 - residuo


def validar_identificacion(tipo: str, numero: str) -> str | None:
    numero = _texto(numero).replace(" ", "").replace(".", "")
    if tipo == "NIT":
        m = re.fullmatch(r"(\d{5,10})-(\d)", numero)
        if not m:
            return "Incluye el dígito de verificación con guion (ej. 900123456-7)."
        nit, dv = m.groups()
        if digito_verificacion_nit(nit) != int(dv):
            return "El dígito de verificación no corresponde al NIT."
        return None
    if tipo in ("CC", "CE"):
        if not re.fullmatch(r"\d{6,10}", numero):
            return "Debe tener entre 6 y 10 dígitos numéricos."
        return None
    if tipo == "PA":
        if not re.fullmatch(r"[A-Za-z0-9]{5,15}", numero):
            return "Debe tener entre 5 y 15 caracteres alfanuméricos."
        return None
    return None


# --- Ubicación ---

def _municipio_en_dataset(municipio: str) -> dict | None:
    buscado = _normalizar_nombre(municipio)
    for m in MUNICIPIOS_DANE:
        if _normalizar_nombre(str(m.get("nombre", ""))) == buscado:
            return m
    return None


def validar_municipio_departamento(municipio: str, departamento: str) -> str | None:
    """Solo valida cuando el municipio está en el dataset (es una muestra,
    no el DANE completo): nunca se rechaza un municipio desconocido."""
    if not _texto(municipio) or not _texto(departamento):
        return None
    registro = _municipio_en_dataset(municipio)
    if registro is None:
        return None
    esperado = _texto(registro.get("departamento", ""))
    if _normalizar_nombre(departamento) != _normalizar_nombre(esperado):
        return f"Según el DANE, {registro.get('nombre')} pertenece a {esperado}."
    return None


# --- Validador principal ---

def validar_fun(datos: dict) -> dict[str, str]:
    errores: dict[str, str] = {}

    for campo in REQUERIDOS:
        valor = datos.get(campo)
        if isinstance(valor, str):
            if not valor.strip():
                errores[campo] = "Este campo es requerido."
        elif valor in (None, "", []):
            errores[campo] = "Este campo es requerido."

    if datos.get("tipoSolicitud") == "prorroga":
        if not _texto(datos.get("numeroExpediente")):
            errores["numeroExpediente"] = "Requerido para prórroga."
        if not _texto(datos.get("numeroActoAdministrativo")):
            errores["numeroActoAdministrativo"] = "Requerido para prórroga."

    if datos.get("calidadPredio") == "otro" and not _texto(datos.get("calidadPredioOtro")):
        errores["calidadPredioOtro"] = "Especifique cuál."

    # Persona jurídica actúa con NIT; persona natural con CC/CE/PA
    tipo_persona = _texto(datos.get("tipoPersona"))
    tipo_id = _texto(datos.get("tipoIdentificacion"))
    if tipo_persona.startswith("juridica") and tipo_id and tipo_id != "NIT":
        errores["tipoIdentificacion"] = "La persona jurídica debe identificarse con NIT."
    if tipo_persona == "natural" and tipo_id == "NIT":
        errores["tipoIdentificacion"] = "La persona natural no usa NIT (usa CC, CE o pasaporte)."

    if tipo_id and _texto(datos.get("numeroIdentificacion")):
        msg = validar_identificacion(tipo_id, str(datos.get("numeroIdentificacion")))
        if msg:
            errores["numeroIdentificacion"] = msg

    if _texto(datos.get("costoProyecto")) and parse_moneda(str(datos.get("costoProyecto"))) is None:
        errores["costoProyecto"] = "Ingrese un número válido (formato: 1.000.000,00)."
    if _texto(datos.get("costoProyecto")) and _texto(datos.get("costoProyectoLetras")):
        msg = validar_costo_letras(str(datos.get("costoProyecto")), str(datos.get("costoProyectoLetras")))
        if msg:
            errores["costoProyectoLetras"] = msg

    sup = parse_numero(str(datos.get("superficieHa") or ""))
    if _texto(datos.get("superficieHa")) and (sup is None or sup <= 0):
        errores["superficieHa"] = "Debe ser un número mayor que cero."

    # Coordenadas
    tipo_coord = _texto(datos.get("tipoCoordenadas"))
    planas = datos.get("coordenadasPlanar") or []
    geos = datos.get("coordenadasGeografica") or []
    if tipo_coord == "planar":
        if len(planas) == 0:
            errores["tipoCoordenadas"] = "Debe agregar al menos un punto de coordenadas."
        for i, p in enumerate(planas):
            for eje in ("x", "y"):
                if parse_numero(str((p or {}).get(eje) or "")) is None:
                    errores[f"coordenadasPlanar[{i}].{eje}"] = "Debe ser un número."
    elif tipo_coord == "geografica":
        if len(geos) == 0:
            errores["tipoCoordenadas"] = "Debe agregar al menos un punto de coordenadas."
        for i, p in enumerate(geos):
            p = p or {}
            lat = parse_numero(str(p.get("latitud") or ""))
            lng = parse_numero(str(p.get("longitud") or ""))
            if lat is None or not (LAT_MIN <= lat <= LAT_MAX):
                errores[f"coordenadasGeografica[{i}].latitud"] = (
                    f"Latitud fuera de Colombia ({LAT_MIN} a {LAT_MAX})."
                )
            if lng is None or not (LNG_MIN <= lng <= LNG_MAX):
                errores[f"coordenadasGeografica[{i}].longitud"] = (
                    f"Longitud fuera de Colombia ({LNG_MIN} a {LNG_MAX})."
                )

    # Especies
    especies = datos.get("especies") or []
    if len(especies) == 0:
        errores["especies"] = "Debe agregar al menos una especie."
    for i, esp in enumerate(especies):
        esp = esp or {}
        cant = _texto(esp.get("cantidad"))
        if not cant:
            errores[f"especies[{i}].cantidad"] = "Requerido."
        else:
            num = parse_numero(cant)
            if num is None or num <= 0:
                errores[f"especies[{i}].cantidad"] = "Debe ser un número positivo."
        if not _texto(esp.get("nombreComun")):
            errores[f"especies[{i}].nombreComun"] = "Requerido."
        if not _texto(esp.get("nombreCientifico")):
            errores[f"especies[{i}].nombreCientifico"] = "Requerido."

    # Ubicación contra dataset DANE disponible
    msg = validar_municipio_departamento(
        str(datos.get("municipio") or ""), str(datos.get("departamento") or "")
    )
    if msg:
        errores["departamento"] = msg
    if _texto(datos.get("municipioNotificacion")) and _texto(datos.get("departamentoNotificacion")):
        msg = validar_municipio_departamento(
            str(datos.get("municipioNotificacion")), str(datos.get("departamentoNotificacion"))
        )
        if msg:
            errores["departamentoNotificacion"] = msg

    # Contacto
    correo = _texto(datos.get("correoElectronico"))
    if correo and not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", correo):
        errores["correoElectronico"] = "Correo electrónico no válido."
    telefonos = _texto(datos.get("telefonos"))
    if telefonos and len(re.sub(r"\D", "", telefonos)) < 7:
        errores["telefonos"] = "Debe contener al menos 7 dígitos."

    return errores
