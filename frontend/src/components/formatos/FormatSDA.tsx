import { FormatUpload } from './FormatUpload';
import './formatos.css';

export const FormatSDA: React.FC = () => {
  return (
    <div className="formato-container">
      <header className="formato-header">
        <h1>Secretaría Distrital de Ambiente</h1>
        <p>Formatos F1, F2 y F3 — descarga la plantilla, diligénciala y súbela para analizarla</p>
      </header>
      <FormatUpload
        tipo="sda"
        accept=".pdf,.docx,.xlsx,.xls"
        ayuda="Sube cualquier formato de la Secretaría (F1 · Solicitud de aprovechamiento, F2 · Ficha silvicultural, F3 · Ficha técnica). La IA verificará los campos del formato correspondiente."
        plantillas={[
          {
            url: '/formatos/formatospm/PM04-PR30-F1 Formulario solicitud manejo aprovechamiento forestal.xlsx',
            nombre: 'F1 · Solicitud de Manejo o Aprovechamiento Forestal (.xlsx)',
          },
          {
            url: '/formatos/formatospm/PM04-PR30-F2 Recoleccion informacion silvicultural individuo ficha1.xlsx',
            nombre: 'F2 · Recolección de Información Silvicultural (.xlsx)',
          },
          {
            url: '/formatos/formatospm/PM04-PR30-F3 Ficha tecnica de registro Ficha 2.docx',
            nombre: 'F3 · Ficha Técnica de Registro (.docx)',
          },
        ]}
      />
    </div>
  );
};

export default FormatSDA;
