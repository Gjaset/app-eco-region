import {
  Building2,
  FileSpreadsheet,
  FileText,
  Home,
  LayoutDashboard,
  ListChecks,
  LogOut,
  Menu,
  Moon,
  Sun,
  Trees,
  User,
  X,
} from 'lucide-react';
import { useEffect, useState } from 'react';
import { Link, NavLink, useLocation, useNavigate } from 'react-router-dom';
import logo from '/logo.png';
import { useAuth } from '../../context/AuthContext';

/**
 * Navegación lateral fija (sidebar). Diseño distinto del repo principal:
 * lista plana en lugar de dropdowns, fondo oscuro, acento lima.
 */
export function Navbar() {
  const [abierto, setAbierto] = useState(false);
  const [isDark, setIsDark] = useState(true);
  const { user, isAuthenticated, isAdmin, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    const saved = localStorage.getItem('theme');
    const initial = saved ? saved === 'dark' : true; // dark por defecto
    setIsDark(initial);
    document.documentElement.setAttribute('data-theme', initial ? 'dark' : 'light');
  }, []);

  // Cierra el drawer al navegar (móvil)
  useEffect(() => {
    setAbierto(false);
  }, [location.pathname]);

  const toggleTheme = () => {
    const next = !isDark;
    setIsDark(next);
    localStorage.setItem('theme', next ? 'dark' : 'light');
    document.documentElement.setAttribute('data-theme', next ? 'dark' : 'light');
  };

  const handleLogout = () => {
    logout();
    navigate('/');
    setAbierto(false);
  };

  const navClass = ({ isActive }: { isActive: boolean }) =>
    `side-link${isActive ? ' is-active' : ''}`;

  return (
    <>
      <button
        className="side-toggle"
        onClick={() => setAbierto(!abierto)}
        aria-label={abierto ? 'Cerrar menú' : 'Abrir menú'}
        aria-expanded={abierto}
      >
        {abierto ? <X size={22} /> : <Menu size={22} />}
      </button>

      <aside className={`side-nav ${abierto ? 'is-open' : ''}`} aria-label="Navegación principal">
        <Link className="side-brand" to="/" aria-label="EcoRegión, inicio">
          <img src={logo} alt="" className="side-logo" />
          <span className="side-wordmark">
            Eco<span>Región</span>
          </span>
        </Link>

        <nav className="side-menu">
          <p className="side-section">Principal</p>
          <NavLink to="/" end className={navClass}>
            <Home size={18} /> Inicio
          </NavLink>
          <NavLink to="/formatos" className={navClass}>
            <ListChecks size={18} /> Formatos
          </NavLink>
          <NavLink to="/formulario-fun" className={navClass}>
            <FileText size={18} /> FUN
          </NavLink>

          <p className="side-section">Entidades</p>
          <NavLink to="/formulario-car" className={navClass}>
            <Building2 size={18} /> CAR · Formulario
          </NavLink>
          <NavLink to="/formatos/sda" className={navClass}>
            <FileSpreadsheet size={18} /> SDA · Subir formatos
          </NavLink>
          <NavLink to="/formatos/corpoboyaca" className={navClass}>
            <Trees size={18} /> Corpoboyacá · Subir
          </NavLink>
        </nav>

        <div className="side-bottom">
          {isAuthenticated ? (
            <div className="side-user">
              <NavLink to="/mis-solicitudes" className={navClass}>
                <FileText size={18} /> Mis solicitudes
              </NavLink>
              {isAdmin && (
                <NavLink to="/admin" className={navClass}>
                  <LayoutDashboard size={18} /> Panel admin
                </NavLink>
              )}
              <div className="side-user-row">
                <span className="side-user-name">
                  <User size={16} /> {user?.name}
                </span>
                <button className="side-icon-btn" onClick={handleLogout} aria-label="Cerrar sesión" title="Cerrar sesión">
                  <LogOut size={16} />
                </button>
              </div>
            </div>
          ) : (
            <div className="side-auth">
              <Link to="/login" className="side-btn-ghost">Iniciar sesión</Link>
              <Link to="/register" className="side-btn-solid">Registrarse</Link>
            </div>
          )}
          <button className="side-icon-btn side-theme" onClick={toggleTheme} aria-label={isDark ? 'Modo claro' : 'Modo oscuro'}>
            {isDark ? <Sun size={18} /> : <Moon size={18} />}
          </button>
        </div>
      </aside>

      {abierto && <div className="side-overlay" onClick={() => setAbierto(false)} aria-hidden />}
    </>
  );
}
