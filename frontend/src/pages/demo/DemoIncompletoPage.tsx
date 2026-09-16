import { DEMO_INCOMPLETO, DemoDictamenPanel } from '../../components/formatos/DemoEjemplosIA';
import { Navbar } from '../../components/comunes/Navbar';
import { Footer } from '../../components/comunes/Footer';

export const DemoIncompletoPage: React.FC = () => {
  return (
    <div className="app-shell">
      <Navbar />
      <main className="formato-page">
        <DemoDictamenPanel demo={DEMO_INCOMPLETO} />
      </main>
      <Footer />
    </div>
  );
};

export default DemoIncompletoPage;
