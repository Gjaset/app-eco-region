import re

COLOMBIA_LAT = (-4.23, 12.45)
COLOMBIA_LNG = (-79.00, -66.85)

def normalizar_coordenada(entrada: str) -> dict:
    entrada = entrada.strip()
    gms = re.search(r"(\d+)[°º]\s*(\d+)['\´]\s*(\d+\.?\d*)[\"\'']+\s*([NSEWnsew])", entrada)
    if gms:
        g, m, s, d = gms.groups()
        decimal = float(g) + float(m) / 60 + float(s) / 3600
        if d.upper() in ("S", "W"):
            decimal = -decimal
        eje = "latitud" if d.upper() in "NS" else "longitud"
        return _validar(decimal, eje, "gms")
    try:
        decimal = float(re.sub(r"[^\d\.\-]", "", entrada))
        eje = "latitud" if COLOMBIA_LAT[0] <= decimal <= COLOMBIA_LAT[1] else "longitud"
        return _validar(decimal, eje, "decimal")
    except ValueError:
        return {"error": "formato_no_reconocido", "entrada_original": entrada}

def _validar(valor: float, eje: str, metodo: str) -> dict:
    bounds = COLOMBIA_LAT if eje == "latitud" else COLOMBIA_LNG
    en_col = bounds[0] <= valor <= bounds[1]
    return {"valor_decimal": round(valor, 6), "eje": eje, "metodo": metodo,
            "en_colombia": en_col, "advertencia": None if en_col else "Coordenada fuera de Colombia"}