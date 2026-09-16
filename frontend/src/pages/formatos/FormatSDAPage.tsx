import { FormatSDA } from '../../components/formatos/FormatSDA';
import { Navbar } from '../../components/comunes/Navbar';
import { Footer } from '../../components/comunes/Footer';

export const FormatSDAPage: React.FC = () => {
  return (
    <div className="app-shell">
      <Navbar />
      <main className="formato-page">
        <FormatSDA />
      </main>
      <Footer />
    </div>
  );
};

export default FormatSDAPage;
