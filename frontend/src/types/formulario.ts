export interface Titular {
  nombre: string;
  nit: string;
  representante_legal: string;
  direccion: string;
}

export interface Predio {
  nombre: string;
  municipio: string;
  vereda: string;
  latitud: string;
  longitud: string;
}

export interface Aprovechamiento {
  tipo: string;
  justificacion: string;
  volumen_total: number;
  unidad: string;
}

export interface Especie {
  nombre: string;
  cantidad: number;
  diametro_cm: number | null;
}

export interface FormData {
  titular: Titular;
  predio: Predio;
  aprovechamiento: Aprovechamiento;
  especies: Especie[];
}

export interface NormalizedData {
  municipio: {
    nombre_oficial: string;
    confianza: number;
    codigo_dane: string;
    requiere_confirmacion: boolean;
  };
  latitud: { valor_decimal: string; eje: string; error?: boolean; en_colombia?: boolean };
  longitud: { valor_decimal: string; eje: string; error?: boolean; en_colombia?: boolean };
  tipo_aprovechamiento: { categoria: string; error?: boolean };
  autoridad: { nombre: string; sigla: string; error?: boolean };
  especies: Array<Especie & { normalizacion: {
    nombre_comun: string;
    nombre_cientifico: string;
    metodo: string;
    confianza?: number;
    requiere_revision?: boolean;
    error?: string;
  } }>;
  requisitos?: { autoridad: string; anexos: string[] };
  requiere_revision?: boolean;
  revision_confirmada?: boolean;
  listo_para_generar: boolean;
}
