import { DEMO_COMPLETO, DemoDictamenPanel } from '../../components/formatos/DemoEjemplosIA';
import { Navbar } from '../../components/comunes/Navbar';
import { Footer } from '../../components/comunes/Footer';

export const DemoCompletoPage: React.FC = () => {
  return (
    <div className="app-shell">
      <Navbar />
      <main className="formato-page">
        <DemoDictamenPanel demo={DEMO_COMPLETO} />
      </main>
      <Footer />
    </div>
  );
};

export default DemoCompletoPage;
