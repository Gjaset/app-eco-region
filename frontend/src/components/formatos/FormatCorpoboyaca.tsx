import { FormatUpload } from './FormatUpload';
import './formatos.css';

export const FormatCorpoboyaca: React.FC = () => {
  return (
    <div className="formato-container">
      <header className="formato-header">
        <h1>Corpoboyacá</h1>
        <p>Formatos FGR-06 y FGR-29 — descarga la plantilla, diligénciala y súbela para analizarla</p>
      </header>
      <FormatUpload
        tipo="corpoboyaca"
        accept=".pdf,.docx,.xlsx,.xls"
        ayuda="Sube cualquier formato de Corpoboyacá (FGR-06 · Registro de información, FGR-29 · Declaración de costos). La IA verificará los campos del formato correspondiente."
        plantillas={[
          {
            url: '/formatos/formatosFG/FGR-06-REGISTRO_INFOR.xlsx',
            nombre: 'FGR-06 · Registro de Información para Aprovechamiento (.xlsx)',
          },
          {
            url: '/formatos/formatosFG/FGR-29-DECLARACION-COSTOS-INVERSION-V3.xlsx',
            nombre: 'FGR-29 · Declaración de Costos de Inversión y Operación (.xlsx)',
          },
        ]}
      />
    </div>
  );
};

export default FormatCorpoboyaca;
