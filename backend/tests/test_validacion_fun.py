"""Validación estricta del FUN: completitud y coherencia antes de exportar."""

from app.core.validacion.fun import (
    _entero_a_letras,
    digito_verificacion_nit,
    validar_costo_letras,
    validar_fun,
)


def _base() -> dict:
    return {
        "tipoSolicitud": "nueva",
        "tipoPersona": "juridicaPrivada",
        "nombreRazonSocial": "ECO REGIÓN SAS BIC",
        "tipoIdentificacion": "NIT",
        "numeroIdentificacion": "900123456-8",
        "calidadPredio": "propietario",
        "tipoPredio": "rural",
        "costoProyecto": "1500000",
        "costoProyectoLetras": "un millón quinientos mil pesos",
        "modoAdquirirDerecho": "propiedad",
        "categoriaProducto": "maderables",
        "metodoAprovechamiento": "manual",
        "nombrePredio": "El Mirador",
        "superficieHa": "12,5",
        "direccionPredio": "Vereda El Centro",
        "urbanoRural": "rural",
        "departamento": "Cundinamarca",
        "municipio": "Bogotá D.C.",
        "nombreFirmante": "Ana Pérez",
        "especies": [
            {"cantidad": "10", "nombreComun": "Eucalipto",
             "nombreCientifico": "Eucalyptus globulus"}
        ],
    }


def test_formulario_valido_no_tiene_errores():
    assert validar_fun(_base()) == {}


def test_vacio_reporta_todos_los_requeridos():
    errores = validar_fun({})
    for campo in ("tipoSolicitud", "nombreRazonSocial", "municipio",
                  "nombreFirmante", "especies"):
        assert campo in errores


def test_costo_en_letras_debe_coincidir():
    datos = _base()
    datos["costoProyectoLetras"] = "dos millones de pesos"
    errores = validar_fun(datos)
    assert "costoProyectoLetras" in errores
    assert "un millon quinientos mil" in errores["costoProyectoLetras"]


def test_costo_en_letras_acepta_centavos_y_variantes():
    datos = _base()
    datos["costoProyecto"] = "1.234.567,89"
    datos["costoProyectoLetras"] = (
        "Un MILLON doscientos treinta y cuatro mil quinientos sesenta y siete "
        "pesos M/CTE con 89/100"
    )
    assert validar_fun(datos) == {}


def test_nit_exige_digito_correcto():
    assert digito_verificacion_nit("900123456") == 8
    datos = _base()
    datos["numeroIdentificacion"] = "900123456-7"
    assert "numeroIdentificacion" in validar_fun(datos)
    datos["numeroIdentificacion"] = "900123456"
    assert "numeroIdentificacion" in validar_fun(datos)


def test_persona_juridica_exige_nit_y_natural_no_lo_usa():
    datos = _base()
    datos["tipoIdentificacion"] = "CC"
    datos["numeroIdentificacion"] = "12345678"
    assert "tipoIdentificacion" in validar_fun(datos)

    datos = _base()
    datos["tipoPersona"] = "natural"
    assert "tipoIdentificacion" in validar_fun(datos)


def test_cc_debe_ser_numerica():
    datos = _base()
    datos["tipoPersona"] = "natural"
    datos["tipoIdentificacion"] = "CC"
    datos["numeroIdentificacion"] = "ABC123"
    assert "numeroIdentificacion" in validar_fun(datos)


def test_prorroga_exige_expediente_y_acto():
    datos = _base()
    datos["tipoSolicitud"] = "prorroga"
    errores = validar_fun(datos)
    assert "numeroExpediente" in errores
    assert "numeroActoAdministrativo" in errores


def test_coordenadas_fuera_de_colombia_se_rechazan():
    datos = _base()
    datos["tipoCoordenadas"] = "geografica"
    datos["coordenadasGeografica"] = [{"latitud": "40.7", "longitud": "-74.0"}]
    errores = validar_fun(datos)
    assert "coordenadasGeografica[0].latitud" in errores

    datos["coordenadasGeografica"] = [{"latitud": "4.6", "longitud": "-74.0"}]
    assert validar_fun(datos) == {}


def test_municipio_departamento_inconsistente():
    datos = _base()
    datos["municipio"] = "Medellín"
    datos["departamento"] = "Cundinamarca"
    errores = validar_fun(datos)
    assert "departamento" in errores
    assert "Antioquia" in errores["departamento"]


def test_municipio_fuera_del_dataset_no_se_rechaza():
    # El dataset incluido es una muestra, no el DANE completo.
    datos = _base()
    datos["municipio"] = "San José del Guaviare"
    datos["departamento"] = "Guaviare"
    assert validar_fun(datos) == {}


def test_contacto_invalido():
    datos = _base()
    datos["correoElectronico"] = "no-es-correo"
    datos["telefonos"] = "123"
    errores = validar_fun(datos)
    assert "correoElectronico" in errores
    assert "telefonos" in errores


def test_conversor_cubre_casos_borde():
    assert _entero_a_letras(0) == "cero"
    assert _entero_a_letras(100) == "cien"
    assert _entero_a_letras(101) == "ciento uno"
    assert _entero_a_letras(1000) == "mil"
    assert _entero_a_letras(1_000_000) == "un millon"
    assert _entero_a_letras(2_000_000_000) == "dos mil millones"
    assert validar_costo_letras("100", "cien pesos") is None
