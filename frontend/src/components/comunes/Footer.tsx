import logo from '/logo.png';

export function Footer() {
  return (
    <footer className="site-footer" id="guia">
      <div className="shell footer-grid">
        <div className="footer-brand">
          <img src={logo} alt="EcoRegión" className="brand-logo" />
        </div>
        <p>Herramientas para trámites ambientales más claros y ordenados.</p>
        <span>© 2026 Eco Región SAS BIC</span>
      </div>
    </footer>
  );
}
