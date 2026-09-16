import { ArrowDown, Download, Loader2, Sparkles } from 'lucide-react';
import { Link } from 'react-router-dom';
import { Footer } from './components/comunes/Footer';
import { Navbar } from './components/comunes/Navbar';
import { AuthoritySelector } from './components/formulario/AuthoritySelector';
import FormularioCAR from './components/formulario/FormularioCAR';
import FormularioCOR from './components/formulario/FormularioCOR';
import FormularioSDA from './components/formulario/FormularioSDA';
import { NormalizationPanel } from './components/formulario/NormalizationPanel';
import { StepProgress } from './components/formulario/StepProgress';
import { useTramiteWizard } from './hooks/useTramiteWizard';

function App() {
  const {
    formData,
    normalizedData,
    loading,
    error,
    authority,
    authorityDetails,
    draftSync,
    updateSection,
    updateSpecies,
    updateAuthorityDetail,
    normalize,
    downloadDocument,
    addSpecies,
    removeSpecies,
    changeAuthority,
  } = useTramiteWizard();

  return (
    <div className="app-shell" id="inicio">
      <Navbar />
      <main>
        <section className="hero shell" id="formulario">
          <div className="hero-copy">
            <span className="eyebrow hero-eyebrow"><Sparkles size={15} /> Trámite guiado</span>
            <h1>Un permiso forestal, <i>sin vueltas.</i></h1>
            <p>Organiza la información del aprovechamiento y recibe un documento técnico listo para revisar.</p>
            <a className="scroll-link" href="#datos"><span>Comenzar formulario</span><ArrowDown size={17} /></a>
          </div>
          <div className="hero-note"><span className="note-line" /><p>Normalización automática<br /><strong>+ revisión humana</strong></p></div>
        </section>
        <section className="workflow shell" id="datos">
          <div className="workflow-top"><div><span className="eyebrow">Solicitud nueva</span><h2>Cuéntanos sobre el aprovechamiento</h2></div><StepProgress activeStep={normalizedData ? 3 : 0} /></div>
          <div role="status">
            {draftSync.status === 'saving' ? 'Guardando…' : draftSync.status === 'offline' ? 'Guardado en este dispositivo' : 'Guardado automáticamente'}
            {draftSync.conflict && ` ${draftSync.conflict}`}
          </div>
          <AuthoritySelector value={authority} onChange={changeAuthority} />
          {authority === 'SDA' && <FormularioSDA formData={formData} details={authorityDetails} onSectionChange={updateSection} onSpeciesChange={updateSpecies} onAddSpecies={addSpecies} onRemoveSpecies={removeSpecies} onDetailChange={updateAuthorityDetail} />}
          {authority === 'CAR' && <FormularioCAR formData={formData} details={authorityDetails} onSectionChange={updateSection} onSpeciesChange={updateSpecies} onAddSpecies={addSpecies} onRemoveSpecies={removeSpecies} onDetailChange={updateAuthorityDetail} />}
          {authority === 'CORPOBOYACA' && <FormularioCOR formData={formData} details={authorityDetails} onSectionChange={updateSection} onSpeciesChange={updateSpecies} onAddSpecies={addSpecies} onRemoveSpecies={removeSpecies} onDetailChange={updateAuthorityDetail} />}
          <div className="form-actions"><div><span className="action-hint">Paso final</span><p>Revisaremos y normalizaremos tus datos antes de generar el documento.</p></div><button className="primary-button" onClick={() => normalize()} disabled={loading}>{loading ? <><Loader2 className="spin" size={18} /> Revisando…</> : <><Sparkles size={18} /> Revisar y continuar</>}</button></div>
        </section>
        {normalizedData && <section className="shell result-wrap"><NormalizationPanel data={normalizedData} loading={loading} onConfirm={() => normalize(true)} />{normalizedData.listo_para_generar && <button className="download-button" onClick={downloadDocument} disabled={loading}>{loading ? <Loader2 className="spin" size={18} /> : <Download size={18} />} {loading ? 'Generando documento…' : 'Descargar documento (.docx)'}</button>}</section>}
        {error && <div className="shell error-message" role="alert">{error}</div>}
        <section className="shell" id="formulario-general">
          <div className="shell-inner">
            <h2 className="section-title">¿Estás tramitando ante la CAR, la SDA o Corpoboyacá?</h2>
            <p>Completa el Formato Único Nacional (FUN) con todos sus anexos.</p>
            <Link className="primary-button" to="/formulario-fun">Ir al Formato Único Nacional</Link>
          </div>
        </section>
      </main>
      <Footer />
    </div>
  );
}

export default App;
