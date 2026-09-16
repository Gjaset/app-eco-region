import { Plus, Trash2 } from 'lucide-react';
import type { ChangeEvent, ReactNode } from 'react';
import type { Aprovechamiento, Especie, FormData, Predio, Titular } from '../../types/formulario';

interface ApplicationFormProps {
  formData: FormData;
  onSectionChange: (event: ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>, section: 'titular' | 'predio' | 'aprovechamiento') => void;
  onSpeciesChange: (index: number, event: ChangeEvent<HTMLInputElement>) => void;
  onAddSpecies: () => void;
  onRemoveSpecies: (index: number) => void;
  children?: ReactNode;
}

function Field({ label, name, value, onChange, type = 'text', placeholder, required = true }: {
  label: string;
  name: string;
  value: string | number;
  onChange: (event: ChangeEvent<HTMLInputElement>) => void;
  type?: string;
  placeholder?: string;
  required?: boolean;
}) {
  return (
    <label className="field">
      <span>{label}{required && <b aria-hidden="true"> *</b>}</span>
      <input name={name} type={type} value={value} onChange={onChange} placeholder={placeholder} required={required} />
    </label>
  );
}

function Section({ eyebrow, title, description, children }: { eyebrow: string; title: string; description: string; children: ReactNode }) {
  return (
    <section className="form-section">
      <div className="section-heading"><span className="eyebrow">{eyebrow}</span><h2>{title}</h2><p>{description}</p></div>
      <div className="section-fields">{children}</div>
    </section>
  );
}

export function ApplicationForm({ formData, onSectionChange, onSpeciesChange, onAddSpecies, onRemoveSpecies, children }: ApplicationFormProps) {
  const sectionChange = (section: 'titular' | 'predio' | 'aprovechamiento') =>
    (event: ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => onSectionChange(event, section);

  return (
    <div className="form-stack">
      <Section eyebrow="01 / Responsable" title="Datos del titular" description="Identifica a la persona o entidad que solicita el trámite.">
        <Field label="Nombre o razón social" name="nombre" value={formData.titular.nombre} onChange={sectionChange('titular')} placeholder="Ej. ECO REGIÓN SAS BIC" />
        <Field label="NIT o documento" name="nit" value={formData.titular.nit} onChange={sectionChange('titular')} placeholder="900000000-1" />
        <Field label="Representante legal" name="representante_legal" value={formData.titular.representante_legal} onChange={sectionChange('titular')} />
        <Field label="Dirección de contacto" name="direccion" value={formData.titular.direccion} onChange={sectionChange('titular')} />
      </Section>

      <Section eyebrow="02 / Ubicación" title="Datos del predio" description="La ubicación define la autoridad ambiental competente y valida las coordenadas.">
        <Field label="Nombre del predio" name="nombre" value={formData.predio.nombre} onChange={sectionChange('predio')} placeholder="Ej. Finca El Roble" />
        <Field label="Municipio" name="municipio" value={formData.predio.municipio} onChange={sectionChange('predio')} placeholder="Ej. Bogotá D.C." />
        <Field label="Vereda" name="vereda" value={formData.predio.vereda} onChange={sectionChange('predio')} required={false} />
        <Field label="Latitud" name="latitud" value={formData.predio.latitud} onChange={sectionChange('predio')} placeholder={'4.6639 o 4°39\'50"N'} />
        <Field label="Longitud" name="longitud" value={formData.predio.longitud} onChange={sectionChange('predio')} placeholder="-74.0721" />
      </Section>

      <Section eyebrow="03 / Solicitud" title="Datos del aprovechamiento" description="Describe el uso previsto y la cantidad estimada de material forestal.">
        <Field label="Tipo de aprovechamiento" name="tipo" value={formData.aprovechamiento.tipo} onChange={sectionChange('aprovechamiento')} placeholder="Ej. Tala por obra civil" />
        <label className="field field-wide"><span>Justificación <b aria-hidden="true">*</b></span><textarea name="justificacion" value={formData.aprovechamiento.justificacion} onChange={sectionChange('aprovechamiento')} placeholder="Explica brevemente el motivo de la solicitud." rows={3} required /></label>
        <Field label="Volumen total" name="volumen_total" type="number" value={formData.aprovechamiento.volumen_total} onChange={sectionChange('aprovechamiento')} />
        <label className="field"><span>Unidad <b aria-hidden="true">*</b></span><select name="unidad" value={formData.aprovechamiento.unidad} onChange={sectionChange('aprovechamiento')}><option value="m3">Metros cúbicos (m³)</option><option value="ton">Toneladas</option></select></label>
      </Section>

      <Section eyebrow="04 / Inventario" title="Especies forestales" description="Añade las especies que serán incluidas en el documento técnico.">
        <div className="species-list">
          {formData.especies.map((especie: Especie, index) => (
            <div className="species-row" key={`${index}-${especie.nombre}`}>
              <span className="species-number">{String(index + 1).padStart(2, '0')}</span>
              <Field label="Nombre común" name="nombre" value={especie.nombre} onChange={(event) => onSpeciesChange(index, event)} placeholder="Ej. Pino" />
              <Field label="Cantidad" name="cantidad" type="number" value={especie.cantidad} onChange={(event) => onSpeciesChange(index, event)} />
              <Field label="Diámetro medio (cm)" name="diametro_cm" type="number" value={especie.diametro_cm ?? ''} onChange={(event) => onSpeciesChange(index, event)} required={false} />
              {formData.especies.length > 1 && <button type="button" className="icon-button danger" onClick={() => onRemoveSpecies(index)} aria-label={`Eliminar especie ${index + 1}`}><Trash2 size={17} /></button>}
            </div>
          ))}
          <button type="button" className="text-button" onClick={onAddSpecies}><Plus size={17} /> Añadir otra especie</button>
        </div>
      </Section>
      {children}
    </div>
  );
}

export type { Titular, Predio, Aprovechamiento };
