import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Mail, Lock, User, Eye, EyeOff } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { Navbar } from '../../components/comunes/Navbar';
import { Footer } from '../../components/comunes/Footer';

const RegisterPage: React.FC = () => {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (password !== confirmPassword) {
      setError('Las contraseñas no coinciden');
      return;
    }

    if (password.length < 8) {
      setError('La contraseña debe tener al menos 8 caracteres');
      return;
    }

    setIsLoading(true);

    try {
      await register(email, password, name);
      navigate('/formulario-fun');
    } catch (err: any) {
      setError(err.message || 'Error al crear la cuenta');
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
              <h1>Crear cuenta</h1>
              <p>Regístrate para acceder a los formularios</p>
            </header>

            {error && <div className="auth-error">{error}</div>}

            <form onSubmit={handleSubmit} className="auth-form">
              <div className="field">
                <label htmlFor="name">Nombre completo</label>
                <div className="input-with-icon">
                  <User size={18} className="input-icon" />
                  <input
                    id="name"
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="Juan Pérez"
                    required
                    disabled={isLoading}
                  />
                </div>
              </div>

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
                    minLength={8}
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

              <div className="field">
                <label htmlFor="confirmPassword">Confirmar contraseña</label>
                <div className="input-with-icon">
                  <Lock size={18} className="input-icon" />
                  <input
                    id="confirmPassword"
                    type={showPassword ? 'text' : 'password'}
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    placeholder="••••••••"
                    required
                    disabled={isLoading}
                    minLength={8}
                  />
                </div>
              </div>

              <button type="submit" className="btn-primary btn-full" disabled={isLoading}>
                {isLoading ? 'Creando cuenta...' : 'Crear cuenta'}
              </button>
            </form>

            <footer className="auth-footer">
              <p>¿Ya tienes cuenta? <Link to="/login">Iniciar sesión</Link></p>
            </footer>
          </div>
        </div>
      </main>
      <Footer />
    </div>
  );
};

export default RegisterPage;