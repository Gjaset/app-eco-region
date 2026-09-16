/**
 * Ejemplos de dictámenes IA para DEMOSTRACIÓN (sin backend, sin archivos).
 * Cada componente renderiza directamente el panel del resultado simulado,
 * igual que se vería tras analizar un documento real.
 *
 * Rutas de demostración: /demo/incompleto y /demo/completo
 */

import { AlertCircle, CheckCircle, Sparkles } from 'lucide-react';
import { ValidacionIA } from '../../services/api';

interface DemoDictamen {
  formato: string;
  autoridad: string;
  archivo: string;
  validacion: ValidacionIA;
}

export const DEMO_INCOMPLETO: DemoDictamen = {
  formato: 'F1 · Solicitud de Manejo o Aprovechamiento Forestal',
  autoridad: 'Secretaría Distrital de Ambiente (SDA)',
  archivo: 'F1_solicitud_aprovechamiento_camargo.xlsx',
  validacion: {
    apto: false,
    puntaje: 55,
    faltantes: [
      { campo: 'Identificación del solicitante', detalle: 'Falta el número de documento y el correo de contacto.' },
      { campo: 'Coordenadas del predio', detalle: 'La celda de coordenadas está vacía; se requieren latitud y longitud.' },
      { campo: 'Detalle del aprovechamiento', detalle: 'Se indicaron las especies pero no el volumen ni el número de viajes.' },
      { campo: 'Firma del solicitante', detalle: 'No hay firma ni nombre en la casilla correspondiente.' },
    ],
    observaciones: [
      'El predio «La Esperanza» sí tiene nombre y municipio. Bien.',
      'Considera adjuntar el folio de matrícula inmobiliaria en observaciones.',
    ],
    resumen: 'El formato tiene la estructura correcta, pero faltan 4 campos obligatorios antes de radicarlo.',
  },
};

export const DEMO_COMPLETO: DemoDictamen = {
  formato: 'F2 · Recolección de Información Silvicultural',
  autoridad: 'Secretaría Distrital de Ambiente (SDA)',
  archivo: 'F2_ficha_silvicultural_completa.xlsx',
  validacion: {
    apto: true,
    puntaje: 97,
    faltantes: [],
    observaciones: [
      'Todos los datos del individuo, ubicación y mediciones están presentes.',
      'Detecté 3 individuos registrados con especie y nombre científico.',
    ],
    resumen: 'Excelente: el documento está completo y listo para pasar a revisión del equipo técnico.',
  },
};

export function DemoDictamenPanel({ demo }: { demo: DemoDictamen }) {
  const v = demo.validacion;
  return (
    <div className="formato-container">
      <header className="formato-header">
        <h1>{demo.formato}</h1>
        <p>{demo.autoridad} — resultado del análisis IA (demostración)</p>
      </header>

      <section className={`ia-panel ${v.apto ? 'ia-panel-ok' : 'ia-panel-alerta'}`}>
        <header className="ia-panel-header">
          {v.apto ? (
            <span className="ia-badge ia-ok"><CheckCircle size={16} /> Documento completo</span>
          ) : (
            <span className="ia-badge ia-alerta"><AlertCircle size={16} /> {v.faltantes.length} punto(s) por corregir</span>
          )}
          <span className="ia-panel-puntaje">Puntaje: {v.puntaje}/100</span>
        </header>

        <p className="demo-ia-archivo">📄 {demo.archivo} <em>(documento de ejemplo)</em></p>

        <p className="ia-panel-resumen"><Sparkles size={15} aria-hidden /> {v.resumen}</p>

        {v.faltantes.length > 0 && (
          <div className="ia-panel-bloque">
            <strong>Campos por corregir:</strong>
            <ul>
              {v.faltantes.map((f, i) => (
                <li key={i}>
                  <span className="ia-faltante-campo">{f.campo}</span>
                  {f.detalle ? ` — ${f.detalle}` : ''}
                </li>
              ))}
            </ul>
          </div>
        )}

        {v.observaciones.length > 0 && (
          <div className="ia-panel-bloque">
            <strong>Observaciones:</strong>
            <ul>
              {v.observaciones.map((o, i) => <li key={i}>{o}</li>)}
            </ul>
          </div>
        )}

        {!v.apto && (
          <p className="ia-panel-cta">Corrige el documento en tu equipo y súbelo de nuevo para re-analizarlo.</p>
        )}
      </section>
    </div>
  );
}
