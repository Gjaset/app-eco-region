import { FormatCorpoboyaca } from '../../components/formatos/FormatCorpoboyaca';
import { Navbar } from '../../components/comunes/Navbar';
import { Footer } from '../../components/comunes/Footer';

export const FormatCorpoboyacaPage: React.FC = () => {
  return (
    <div className="app-shell">
      <Navbar />
      <main className="formato-page">
        <FormatCorpoboyaca />
      </main>
      <Footer />
    </div>
  );
};

export default FormatCorpoboyacaPage;
