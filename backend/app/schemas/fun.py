from typing import Optional

from pydantic import BaseModel, Field


class CoordenadaPlanar(BaseModel):
    punto: str = ""
    x: str = ""
    y: str = ""


class CoordenadaGeografica(BaseModel):
    punto: str = ""
    gradosLat: str = ""
    latitud: str = ""
    minutosLat: str = ""
    segundosLat: str = ""
    gradosLong: str = ""
    longitud: str = ""
    minutosLong: str = ""
    segundosLong: str = ""
    altitud: str = ""
    origen: str = ""


class EspecieFUN(BaseModel):
    cantidad: str = ""
    unidadMedida: str = ""
    nombreComun: str = ""
    nombreCientifico: str = ""
    habitos: str = ""
    parteAprovechada: str = ""
    vedaNacionalRegional: str = ""
    categoriaAmenaza: str = ""
    usoProductos: str = ""


class FormularioFUN(BaseModel):
    """Refleja FormularioFUNData del frontend. Todo opcional para permitir borradores."""

    tipoSolicitud: str = ""
    tipoPersona: str = ""
    nombreRazonSocial: str = ""
    tipoIdentificacion: str = ""
    numeroIdentificacion: str = ""
    apoderadoNombre: str = ""
    apoderadoTipoIdentificacion: str = ""
    apoderadoNumeroIdentificacion: str = ""
    apoderadoTP: str = ""
    calidadPredio: str = ""
    calidadPredioOtro: str = ""
    tipoPredio: str = ""
    costoProyecto: str = ""
    costoProyectoLetras: str = ""
    numeroExpediente: str = ""
    numeroActoAdministrativo: str = ""
    modoAdquirirDerecho: str = ""
    categoriaProducto: str = ""
    claseAprovechamientoMaderables: str = ""
    claseManejoSostenible: str = ""
    ingresosMensualesSMLMV: str = ""
    ingresosMensualesSMLMVLetras: str = ""
    categoriaPersistente: str = ""
    tipoAprovechamientoGuaduales: str = ""
    nombrePredio: str = ""
    superficieHa: str = ""
    direccionPredio: str = ""
    urbanoRural: str = ""
    departamento: str = ""
    municipio: str = ""
    vereda: str = ""
    matriculaInmobiliaria: str = ""
    cedulaCatastral: str = ""
    tipoCoordenadas: str = ""
    coordenadasPlanar: list[CoordenadaPlanar] = Field(default_factory=list)
    coordenadasGeografica: list[CoordenadaGeografica] = Field(default_factory=list)
    metodoAprovechamiento: str = ""
    especies: list[EspecieFUN] = Field(default_factory=list)
    usoProductos: str = ""
    arbolesAisladosUbicacion: str = ""
    estadoIndividuo: str = ""
    razonesFitosanitariasEspecificar: str = ""
    causaPerjuicio: str = ""
    causaPerjuicioOtro: str = ""
    actividadInfraestructura: str = ""
    similaresEspecificar: str = ""
    notificacionElectronica: str = ""
    correoElectronico: str = ""
    telefonos: str = ""
    direccionNotificacion: str = ""
    municipioNotificacion: str = ""
    nombreCentroPobladoVeredaCorregimiento: str = ""
    departamentoNotificacion: str = ""
    nombreFirmante: str = ""
    firmaTexto: Optional[str] = None
