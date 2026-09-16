import { ArrowDown, Sparkles, Shield, Zap, Users, FileText, Search } from 'lucide-react';
import { Link } from 'react-router-dom';
import { Navbar } from '../components/comunes/Navbar';
import { Footer } from '../components/comunes/Footer';

const MainPage: React.FC = () => {
  return (
    <div className="app-shell" id="inicio">
      <Navbar />
      <main>
        <section className="hero shell" id="inicio">
          <div className="hero-copy">
            <span className="eyebrow hero-eyebrow"><Sparkles size={15} /> Trámite guiado paso a paso</span>
            <h1>Un permiso forestal, <i>sin vueltas.</i></h1>
            <p>Organiza la información del aprovechamiento y obtén un documento técnico listo para presentar ante la autoridad.</p>
            <Link className="scroll-link" to="/formulario-fun"><span>Comenzar formulario</span><ArrowDown size={17} /></Link>
          </div>
          <div className="hero-note"><span className="note-line" /><p>Normalización automática<br /><strong>+ revisión humana</strong></p></div>
        </section>

        <section className="features shell" id="features">
          <div className="section-head">
            <span className="eyebrow">¿Qué obtienes?</span>
            <h2>Todo en un solo lugar</h2>
          </div>
          <div className="features-grid">
            <article className="feature-card">
              <div className="feature-icon"><Shield size={24} /></div>
              <h3>Validación automática</h3>
              <p>Verificamos que tu información cumpla los requisitos antes de radicarla.</p>
            </article>
            <article className="feature-card">
              <div className="feature-icon"><Zap size={24} /></div>
              <h3>Generación de documentos</h3>
              <p>Descarga el formato técnico correcto para tu trámite, sin saber de normas.</p>
            </article>
            <article className="feature-card">
              <div className="feature-icon"><Users size={24} /></div>
              <h3>Cobertura multi-autoridad</h3>
              <p>CAR Cundinamarca, Secretaría Distrital de Ambiente y Corpoboyacá.</p>
            </article>
            <article className="feature-card">
              <div className="feature-icon"><FileText size={24} /></div>
              <h3>Historial y seguimiento</h3>
              <p>Guarda tus documentos y revisa su estado cuando quieras.</p>
            </article>
            <article className="feature-card">
              <div className="feature-icon"><Search size={24} /></div>
              <h3>Búsqueda de requisitos</h3>
              <p>Descubre en segundos qué anexos necesitas según tu tipo de aprovechamiento.</p>
            </article>
          </div>
        </section>

        <section className="cta shell" id="cta">
          <div className="cta-card">
            <h2>Empieza hoy tu trámite forestal</h2>
            <p>Elige tu autoridad ambiental y completa el formulario guiado.</p>
            <Link className="primary-button" to="/formulario-fun"><Sparkles size={18} /> Comenzar ahora</Link>
          </div>
        </section>
      </main>
      <Footer />
    </div>
  );
};

export default MainPage;