import { Navbar } from '../components/comunes/Navbar';
import { Footer } from '../components/comunes/Footer';
import { FormatUpload } from '../components/formatos/FormatUpload';
import '../components/formatos/formatos.css';

const FormularioFUNPage: React.FC = () => {
  return (
    <div className="app-shell">
      <Navbar />
      <main>
        <div className="form-shell" style={{ paddingTop: '24px', paddingBottom: '48px' }}>
          <div className="formato-container">
            <header className="formato-header">
              <h1>FUN · Formato Único Nacional de Aprovechamiento Forestal</h1>
              <p>Descarga la plantilla oficial, diligénciala y súbela para analizarla</p>
            </header>
            <FormatUpload
              tipo="fun"
              accept=".pdf,.docx,.xlsx,.xls"
              plantillaUrl="/formatos/FUN_Formato_Unico_Nacional.pdf"
              plantillaNombre="FUN_Formato_Unico_Nacional.pdf"
              ayuda="Sube el FUN diligenciado. La IA verificará todas las secciones: datos del interesado, predio, ubicación, aprovechamiento y firmas."
            />
          </div>
        </div>
      </main>
      <Footer />
    </div>
  );
};

export default FormularioFUNPage;
