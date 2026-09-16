import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './context/AuthContext'
import App from './App'
import { AIAssistant } from './components/comunes/AIAssistant'
import MainPage from './pages/MainPage'
import FormularioFUNPage from './pages/FormularioFUNPage'
import FormCARPage from './pages/formulario/FormCARPage'
import LoginPage from './pages/auth/LoginPage'
import RegisterPage from './pages/auth/RegisterPage'
import AdminPage from './pages/admin/AdminPage'
import FormatosPage from './pages/FormatosPage'
import MisSolicitudesPage from './pages/MisSolicitudesPage'
import DemoIncompletoPage from './pages/demo/DemoIncompletoPage'
import DemoCompletoPage from './pages/demo/DemoCompletoPage'
import FormatSDAPage from './pages/formatos/FormatSDAPage'
import FormatCorpoboyacaPage from './pages/formatos/FormatCorpoboyacaPage'
import './index.css'

function AdminRoute({ children }: { children: React.ReactNode }) {
  const { isAdmin, isLoading } = useAuth();
  if (isLoading) return <div className="loading">Cargando...</div>;
  return isAdmin ? <>{children}</> : <Navigate to="/" replace />;
}

ReactDOM.createRoot(document.getElementById('root') as HTMLElement).render(
  <React.StrictMode>
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<MainPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/formulario-fun" element={<FormularioFUNPage />} />
          <Route path="/formulario-car" element={<FormCARPage />} />
          <Route path="/formatos" element={<FormatosPage />} />
          <Route path="/formatos/sda" element={<FormatSDAPage />} />
          <Route path="/formatos/corpoboyaca" element={<FormatCorpoboyacaPage />} />
          <Route path="/mis-solicitudes" element={<MisSolicitudesPage />} />
          <Route path="/prueba1" element={<DemoIncompletoPage />} />
          <Route path="/prueba2" element={<DemoCompletoPage />} />
          <Route path="/admin" element={
            <AdminRoute><AdminPage /></AdminRoute>
          } />
          <Route path="/app/*" element={<App />} />
        </Routes>
        <AIAssistant />
      </BrowserRouter>
    </AuthProvider>
  </React.StrictMode>,
)