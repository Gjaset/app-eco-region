import { AlertTriangle, CheckCircle2, ClipboardCheck, MapPin, ShieldCheck } from 'lucide-react';
import type { NormalizedData } from '../../types/formulario';

interface NormalizationPanelProps {
  data: NormalizedData;
  loading: boolean;
  onConfirm: () => void;
}

export function NormalizationPanel({ data, loading, onConfirm }: NormalizationPanelProps) {
  const needsReview = data.requiere_revision && !data.revision_confirmada;

  return (
    <section className={`result-panel ${needsReview ? 'is-review' : 'is-ready'}`} aria-live="polite">
      <div className="result-header">
        <div className="result-icon">{needsReview ? <AlertTriangle size={22} /> : <CheckCircle2 size={22} />}</div>
        <div><span className="eyebrow">Resultado del análisis</span><h2>{needsReview ? 'Necesita una revisión' : 'Formulario listo'}</h2></div>
        <span className="result-status">{needsReview ? 'Pendiente' : 'Validado'}</span>
      </div>
      <div className="result-grid">
        <div className="result-item"><MapPin size={17} /><span>Municipio<strong>{data.municipio.nombre_oficial}</strong></span></div>
        <div className="result-item"><ShieldCheck size={17} /><span>Autoridad<strong>{data.autoridad.sigla} · {data.autoridad.nombre}</strong></span></div>
        <div className="result-item"><ClipboardCheck size={17} /><span>Tipo<strong>{data.tipo_aprovechamiento.categoria}</strong></span></div>
      </div>
      {data.especies.length > 0 && <div className="species-summary"><span className="summary-label">Especies identificadas</span>{data.especies.map((species, index) => <span className="species-pill" key={`${species.nombre}-${index}`}>{species.normalizacion.nombre_comun} <em>{species.normalizacion.confianza ? `${Math.round(species.normalizacion.confianza)}%` : 'revisar'}</em></span>)}</div>}
      {data.requisitos && <div className="requirements"><span className="summary-label">Anexos para tu radicación</span><ul>{data.requisitos.anexos.map((item) => <li key={item}>{item}</li>)}</ul></div>}
      {needsReview && <div className="review-action"><p>Revisa los datos señalados. Puedes confirmar la información para continuar bajo tu responsabilidad.</p><button className="secondary-button" onClick={onConfirm} disabled={loading}>{loading ? 'Confirmando...' : 'Confirmar revisión'}</button></div>}
    </section>
  );
}
