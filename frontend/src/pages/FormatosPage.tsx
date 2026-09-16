import React, { useState } from 'react';
import { LayoutDashboard, FileSpreadsheet, ChevronRight } from 'lucide-react';
import { FormatSDA } from '../components/formatos/FormatSDA';
import { FormatCorpoboyaca } from '../components/formatos/FormatCorpoboyaca';
import { Navbar } from '../components/comunes/Navbar';
import { Footer } from '../components/comunes/Footer';
import { useAuth } from '../context/AuthContext';
import '../components/formatos/formatos.css';

type EntidadType = 'sda' | 'corpoboyaca';

interface EntidadInfo {
  id: EntidadType;
  title: string;
  subtitle: string;
  icon: React.ReactNode;
  description: string;
  formatos: string;
}

const ENTIDADES: EntidadInfo[] = [
  {
    id: 'sda',
    title: 'Secretaría Distrital de Ambiente',
    subtitle: 'Formatos F1 · F2 · F3',
    icon: <FileSpreadsheet size={24} />,
    description: 'Sube cualquier plantilla de la Secretaría (solicitud de aprovechamiento, ficha silvicultural o ficha técnica) y la IA verificará que esté correctamente diligenciada.',
    formatos: 'F1 · F2 · F3',
  },
  {
    id: 'corpoboyaca',
    title: 'Corpoboyacá',
    subtitle: 'Formatos FGR-06 · FGR-29',
    icon: <FileSpreadsheet size={24} />,
    description: 'Sube la plantilla de registro de información o de declaración de costos y la IA verificará que esté correctamente diligenciada.',
    formatos: 'FGR-06 · FGR-29',
  },
];

export const FormatosPage: React.FC = () => {
  const { isAdmin } = useAuth();
  const [activeEntidad, setActiveEntidad] = useState<EntidadType | null>(null);
  const [view, setView] = useState<'list' | 'detail'>('list');

  return (
    <div className="app-shell">
      <Navbar />
      <main>
        <div className="formatos-shell">
          <header className="formatos-header">
            <div className="formatos-header-content">
              <div className="formatos-breadcrumb">
                <LayoutDashboard size={18} />
                <span>Formatos</span>
              </div>
              <h1>Formatos Forestales</h1>
              <p>Selecciona la entidad para subir tu documento y analizarlo</p>
            </div>
            {isAdmin && (
              <div className="formatos-admin-badge">
                <span>Panel de Administración</span>
                <ChevronRight size={16} />
              </div>
            )}
          </header>

          {view === 'list' ? (
            <div className="formatos-grid">
              {ENTIDADES.map((entidad) => (
                <article
                  key={entidad.id}
                  className="formato-card"
                  onClick={() => { setActiveEntidad(entidad.id); setView('detail'); }}
                >
                  <div className="formato-card-icon">{entidad.icon}</div>
                  <div className="formato-card-content">
                    <h3>{entidad.title}</h3>
                    <h4>{entidad.subtitle}</h4>
                    <p>{entidad.description}</p>
                    <span className="formato-extension">{entidad.formatos}</span>
                  </div>
                  <ChevronRight size={20} className="formato-card-arrow" />
                </article>
              ))}
            </div>
          ) : (
            <div className="formato-detail">
              <button className="back-button" onClick={() => { setActiveEntidad(null); setView('list'); }}>
                <ChevronRight size={18} />
                Volver a formatos
              </button>
              {activeEntidad === 'sda' && <FormatSDA />}
              {activeEntidad === 'corpoboyaca' && <FormatCorpoboyaca />}
            </div>
          )}
        </div>
      </main>
      <Footer />
    </div>
  );
};

export default FormatosPage;
