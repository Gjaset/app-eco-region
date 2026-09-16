import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Mail, Lock, Eye, EyeOff } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { Navbar } from '../../components/comunes/Navbar';
import { Footer } from '../../components/comunes/Footer';

const LoginPage: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      await login(email, password);
      navigate('/formulario-fun');
    } catch (err: any) {
      setError(err.message || 'Error al iniciar sesión');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app-shell">
      <Navbar />
      <main className="auth-page">
        <div className="auth-shell">
          <div className="auth-card">
            <header className="auth-header">
              <h1>Iniciar sesión</h1>
              <p>Accede para guardar y dar seguimiento a tus trámites.</p>
            </header>

            {error && <div className="auth-error">{error}</div>}

            <form onSubmit={handleSubmit} className="auth-form">
              <div className="field">
                <label htmlFor="email">Email</label>
                <div className="input-with-icon">
                  <Mail size={18} className="input-icon" />
                  <input
                    id="email"
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="tu@email.com"
                    required
                    disabled={isLoading}
                  />
                </div>
              </div>

              <div className="field">
                <label htmlFor="password">Contraseña</label>
                <div className="input-with-icon">
                  <Lock size={18} className="input-icon" />
                  <input
                    id="password"
                    type={showPassword ? 'text' : 'password'}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••"
                    required
                    disabled={isLoading}
                  />
                  <button
                    type="button"
                    className="toggle-password"
                    onClick={() => setShowPassword(!showPassword)}
                    aria-label={showPassword ? 'Ocultar contraseña' : 'Mostrar contraseña'}
                  >
                    {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                  </button>
                </div>
              </div>

              <button type="submit" className="btn-primary btn-full" disabled={isLoading}>
                {isLoading ? 'Entrando…' : 'Entrar'}
              </button>
            </form>

            <footer className="auth-footer">
              <p>¿Primera vez? <Link to="/register">Crea tu cuenta</Link></p>
            </footer>
          </div>
        </div>
      </main>
      <Footer />
    </div>
  );
};

export default LoginPage;