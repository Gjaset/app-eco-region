import type { ChangeEvent } from 'react';

export interface AuthorityFieldsProps {
  details: Record<string, string | boolean>;
  onChange: (event: ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => void;
}

function TextField({ label, name, value, onChange, placeholder, required = false }: {
  label: string;
  name: string;
  value: string | boolean | undefined;
  onChange: AuthorityFieldsProps['onChange'];
  placeholder?: string;
  required?: boolean;
}) {
  return <label className="field"><span>{label}{required && <b aria-hidden="true"> *</b>}</span><input name={name} value={String(value ?? '')} onChange={onChange} placeholder={placeholder} required={required} /></label>;
}

export function SDAFields({ details, onChange }: AuthorityFieldsProps) {
  return <section className="authority-section"><div className="section-heading"><span className="eyebrow">SDA / Fichas</span><h2>Información silvicultural</h2><p>Datos adicionales de las fichas PM04-PR30-F1, F2 y F3.</p></div><div className="section-fields"><TextField label="Código del trámite o expediente" name="codigo_expediente" value={details.codigo_expediente} onChange={onChange} /><TextField label="Dirección del arbolado" name="direccion_arbolado" value={details.direccion_arbolado} onChange={onChange} required /><TextField label="Tipo de intervención" name="tipo_intervencion" value={details.tipo_intervencion} onChange={onChange} placeholder="Tala, poda, traslado o tratamiento" required /><TextField label="Estado fitosanitario" name="estado_fitosanitario" value={details.estado_fitosanitario} onChange={onChange} placeholder="Sano, enfermo, muerto, riesgo" /><TextField label="Destino del material vegetal" name="destino_material" value={details.destino_material} onChange={onChange} /><TextField label="Medida de compensación propuesta" name="compensacion" value={details.compensacion} onChange={onChange} /></div></section>;
}

export function CARFields({ details, onChange }: AuthorityFieldsProps) {
  return <section className="authority-section"><div className="section-heading"><span className="eyebrow">CAR / Soportes</span><h2>Propiedad y localización</h2><p>Información complementaria exigida por la CAR Cundinamarca.</p></div><div className="section-fields"><label className="field"><span>Relación con el predio <b aria-hidden="true"> *</b></span><select name="relacion_predio" value={String(details.relacion_predio ?? '')} onChange={onChange} required><option value="">Selecciona una opción</option><option value="propietario">Propietario</option><option value="poseedor">Poseedor o tenedor</option><option value="autorizado">Autorizado por el propietario</option></select></label><TextField label="Matrícula inmobiliaria" name="matricula_inmobiliaria" value={details.matricula_inmobiliaria} onChange={onChange} /><TextField label="Fecha del certificado de tradición" name="fecha_tradicion" value={details.fecha_tradicion} onChange={onChange} placeholder="DD/MM/AAAA" /><TextField label="Acceso o referencia del croquis" name="referencia_croquis" value={details.referencia_croquis} onChange={onChange} required /><TextField label="Motivo de la solicitud" name="motivo_solicitud" value={details.motivo_solicitud} onChange={onChange} placeholder="Riesgo, obra, sanitario u otro" required /><TextField label="¿Actúa mediante apoderado?" name="actua_apoderado" value={details.actua_apoderado} onChange={onChange} /></div></section>;
}

export function CorpoboyacaFields({ details, onChange }: AuthorityFieldsProps) {
  return <section className="authority-section"><div className="section-heading"><span className="eyebrow">Corpoboyacá / Escenario</span><h2>Clasificación del trámite</h2><p>Define el escenario que determina los formatos FGR-06, FGR-29 y soportes.</p></div><div className="section-fields"><label className="field field-wide"><span>Origen de los árboles <b aria-hidden="true"> *</b></span><select name="origen_arboles" value={String(details.origen_arboles ?? '')} onChange={onChange} required><option value="">Selecciona una opción</option><option value="nativo">Especies nativas</option><option value="exotico">Especies exóticas o introducidas</option></select></label><label className="field field-wide"><span>Finalidad <b aria-hidden="true"> *</b></span><select name="finalidad" value={String(details.finalidad ?? '')} onChange={onChange} required><option value="">Selecciona una opción</option><option value="domestico">Uso doméstico</option><option value="obra">Obra pública o privada</option><option value="comercial">Aprovechamiento comercial</option><option value="emergencia">Tala de emergencia o prioritaria</option></select></label><TextField label="Volumen estimado en m³" name="volumen_estimado_m3" value={details.volumen_estimado_m3} onChange={onChange} required /><TextField label="Código o referencia FGR-29" name="referencia_fgr29" value={details.referencia_fgr29} onChange={onChange} /><TextField label="Correo de radicación" name="correo_radicacion" value={details.correo_radicacion} onChange={onChange} placeholder="ousuario@corpoboyaca.gov.co" /><TextField label="Número de predios o unidades" name="numero_unidades" value={details.numero_unidades} onChange={onChange} /></div></section>;
}
