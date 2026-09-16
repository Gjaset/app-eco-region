import { useState, useEffect, useCallback } from 'react';
import { Search, User, Mail, Shield, Trash2, Eye, Filter, BarChart2, Download, ChevronLeft, ChevronRight, Eraser } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { api, ValidacionIA } from '../../services/api';
import { Navbar } from '../../components/comunes/Navbar';
import { Footer } from '../../components/comunes/Footer';

type UserRole = 'admin' | 'consultor' | 'cliente';

interface AdminUser {
  id: number;
  email: string;
  name: string;
  role: UserRole;
  activo: boolean;
  createdAt: string;
}

interface Request {
  id: string;
  userName: string;
  userEmail: string;
  type: 'CAR' | 'SDA' | 'COR' | 'FUN';
  status: 'pendiente' | 'en_revision' | 'aprobado' | 'rechazado';
  createdAt: string;
  updatedAt: string;
}

interface SolicitDoc {
  id: number;
  usuario_id: number;
  usuario_email: string;
  usuario_nombre: string;
  tipo: string;
  estado: string;
  nombre_archivo: string;
  tamano_bytes: number;
  creado_en: string;
  resumen?: { validacion_ia?: ValidacionIA } & Record<string, unknown>;
}

interface ReporteResumen {
  totales: { solicitudes: number; usuarios: number; bytes: number };
  por_tipo: Record<string, number>;
  por_mes: Record<string, number>;
  top_usuarios: Array<{ usuario_id: number; nombre: string; email: string; total: number }>;
  actividad_reciente: Array<{ fecha: string; total: number }>;
  tipos_disponibles: Array<{ tipo: string; label: string }>;
  generado_en: string;
}

interface RegistroDetalle {
  id: number;
  usuario_id: number;
  usuario_nombre: string;
  usuario_email: string;
  tipo: string;
  tipo_label: string;
  nombre_archivo: string;
  tamano_bytes: number;
  creado_en: string | null;
  detalle: Record<string, string>;
}

const TIPOS_DOCUMENTO: Array<{ tipo: string; label: string }> = [
  { tipo: 'fun', label: 'Formato Único Nacional (FUN)' },
  { tipo: 'formulario', label: 'Documento Técnico (Word)' },
  { tipo: 'sda', label: 'SDA · Formatos F1/F2/F3' },
  { tipo: 'corpoboyaca', label: 'Corpoboyacá · Formatos FGR-06/FGR-29' },
  { tipo: 'f1', label: 'SDA · PM04-PR30-F1 (solicitud)' },
  { tipo: 'f2', label: 'SDA · PM04-PR30-F2 (ficha silvicultural)' },
  { tipo: 'f3', label: 'SDA · PM04-PR30-F3 (ficha técnica)' },
  { tipo: 'fg1', label: 'Corpoboyacá · FGR-06 (inventario)' },
  { tipo: 'fg2', label: 'Corpoboyacá · FGR-29 (costos)' },
];

const AdminPage: React.FC = () => {
  const { user, isAdmin } = useAuth();
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [docs, setDocs] = useState<SolicitDoc[]>([]);
  const [reporte, setReporte] = useState<ReporteResumen | null>(null);
  const [reportLoading, setReportLoading] = useState(false);
  const [detalle, setDetalle] = useState<RegistroDetalle[]>([]);
  const [filtroUsuario, setFiltroUsuario] = useState<number | 'all'>('all');
  const [filtroTipo, setFiltroTipo] = useState<string>('all');
  const [filtroDesde, setFiltroDesde] = useState('');
  const [filtroHasta, setFiltroHasta] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [roleFilter, setRoleFilter] = useState<'all' | UserRole>('all');
  const [statusFilter, setStatusFilter] = useState<'all' | 'pendiente' | 'en_revision' | 'aprobado' | 'rechazado'>('all');
  const [activeTab, setActiveTab] = useState<'users' | 'requests' | 'docs' | 'reports'>('users');
  const [userFilter, setUserFilter] = useState<number | 'all'>('all');
  const [docTipoFilter, setDocTipoFilter] = useState<string>('all');
  const [docDesde, setDocDesde] = useState('');
  const [docHasta, setDocHasta] = useState('');
  const [selectedDocs, setSelectedDocs] = useState<number[]>([]);
  const [downloadingZip, setDownloadingZip] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const PAGE_SIZE = 10;
  const [page, setPage] = useState(1);

  const load = useCallback(async () => {
    if (!isAdmin) return;
    setLoading(true);
    setError('');
    try {
      const [apiUsers, solicitudes] = await Promise.all([
        api.listUsers(),
        api.listSolicitudes(),
      ]);
      setUsers(apiUsers.map((u) => ({
        id: u.id,
        email: u.email,
        name: u.nombre,
        role: (u.rol as UserRole) || 'cliente',
        activo: u.activo,
        createdAt: u.creado_en,
      })));
      setDocs(solicitudes);
      setSelectedDocs([]);
    } catch {
      setError('No se pudieron cargar los datos. Verifica la conexión con el backend.');
    } finally {
      setLoading(false);
    }
  }, [isAdmin]);

  useEffect(() => {
    void load();
  }, [load]);

  useEffect(() => {
    setPage(1);
  }, [activeTab]);

  const loadReporte = useCallback(async () => {
    setReportLoading(true);
    try {
      const data = await api.getReporteResumen();
      setReporte(data);
    } catch {
      setError('No se pudo generar el reporte.');
    } finally {
      setReportLoading(false);
    }
  }, []);

  const loadDetalle = useCallback(async () => {
    try {
      const params: { usuario_id?: number; tipo?: string; fecha_desde?: string; fecha_hasta?: string } = {};
      if (filtroUsuario !== 'all') params.usuario_id = filtroUsuario;
      if (filtroTipo !== 'all') params.tipo = filtroTipo;
      if (filtroDesde) params.fecha_desde = filtroDesde;
      if (filtroHasta) params.fecha_hasta = filtroHasta;
      const data = await api.getReporteDetalle(params);
      setDetalle(data.registros);
    } catch {
      setError('No se pudo cargar el detalle del reporte.');
    }
  }, [filtroUsuario, filtroTipo, filtroDesde, filtroHasta]);

  useEffect(() => {
    if (activeTab === 'reports') {
      void loadReporte();
      void loadDetalle();
    }
  }, [activeTab, loadReporte, loadDetalle]);

  const filteredUsers = users.filter(u => {
    const matchesSearch = u.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          u.email.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesRole = roleFilter === 'all' || u.role === roleFilter;
    return matchesSearch && matchesRole;
  });

  const filteredRequests = docs.filter(r => {
    const matchesSearch = `${r.usuario_nombre} ${r.usuario_email} ${r.nombre_archivo}`.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'all' || r.estado === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const handleDeleteUser = (userId: number) => {
    if (userId === user?.id) return;
    setShowDeleteConfirm(userId);
  };

  const confirmDeleteUser = async (userId: number) => {
    try {
      await api.deleteUser(userId);
      setUsers((prev) => prev.filter((u) => u.id !== userId));
    } catch {
      setError('No se pudo eliminar el usuario.');
    } finally {
      setShowDeleteConfirm(null);
    }
  };

  const cycleUserRole = async (u: AdminUser) => {
    const next: UserRole = u.role === 'cliente' ? 'consultor' : u.role === 'consultor' ? 'admin' : 'cliente';
    try {
      const updated = await api.updateUser(u.id, { rol: next });
      setUsers((prev) => prev.map((x) => (x.id === u.id ? { ...x, role: updated.rol as UserRole } : x)));
    } catch {
      setError('No se pudo cambiar el rol.');
    }
  };

  const toggleUserActive = async (u: AdminUser) => {
    try {
      const updated = await api.updateUser(u.id, { activo: !u.activo });
      setUsers((prev) => prev.map((x) => (x.id === u.id ? { ...x, activo: updated.activo } : x)));
    } catch {
      setError('No se pudo cambiar el estado del usuario.');
    }
  };

  const actualizarEstadoSolicitud = async (solicitudId: number, estado: string) => {
    try {
      await api.updateSolicitudEstado(solicitudId, estado);
      setDocs((prev) => prev.map((d) => (d.id === solicitudId ? { ...d, estado } : d)));
    } catch {
      setError('No se pudo actualizar el estado de la solicitud.');
    }
  };

  const limpiarFiltros = () => {
    setSearchTerm('');
    setRoleFilter('all');
    setStatusFilter('all');
    setUserFilter('all');
    setDocTipoFilter('all');
    setDocDesde('');
    setDocHasta('');
    setFiltroUsuario('all');
    setFiltroTipo('all');
    setFiltroDesde('');
    setFiltroHasta('');
    setPage(1);
  };

  const filteredDocs = docs.filter((d) => {
    const matchesUser = userFilter === 'all' || d.usuario_id === userFilter;
    const matchesTipo = docTipoFilter === 'all' || d.tipo === docTipoFilter;
    const haystack = `${d.usuario_nombre} ${d.usuario_email} ${d.nombre_archivo}`.toLowerCase();
    const matchesSearch = haystack.includes(searchTerm.toLowerCase());
    const dFecha = d.creado_en ? new Date(d.creado_en) : null;
    const matchesDesde = !docDesde || (dFecha && dFecha >= new Date(docDesde + 'T00:00:00'));
    const matchesHasta = !docHasta || (dFecha && dFecha <= new Date(docHasta + 'T23:59:59'));
    return matchesUser && matchesTipo && matchesSearch && matchesDesde && matchesHasta;
  });

  const toggleDoc = (id: number) =>
    setSelectedDocs((prev) => (prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]));

  const toggleAllDocs = () =>
    setSelectedDocs((prev) => (prev.length === filteredDocs.length ? [] : filteredDocs.map((d) => d.id)));

  const downloadZip = async () => {
    if (selectedDocs.length === 0) return;
    setDownloadingZip(true);
    setError('');
    try {
      const blob = await api.downloadSolicitudesZip(selectedDocs);
      const first = docs.find((d) => d.id === selectedDocs[0]);
      const sameOwner = selectedDocs.every(
        (id) => docs.find((d) => d.id === id)?.usuario_id === first?.usuario_id
      );
      const stamp = new Date().toISOString().slice(0, 16).replace(/[-:T]/g, '');
      const base = sameOwner && first
        ? first.usuario_nombre.replace(/[^A-Za-z0-9]+/g, '_').replace(/^_+|_+$/g, '') || 'usuario'
        : 'solicitudes';
      const url = window.URL.createObjectURL(new Blob([blob], { type: 'application/zip' }));
      const anchor = document.createElement('a');
      anchor.href = url;
      anchor.download = `${base}_${stamp}.zip`;
      document.body.appendChild(anchor);
      anchor.click();
      anchor.remove();
      window.URL.revokeObjectURL(url);
    } catch {
      setError('No se pudo descargar el ZIP.');
    } finally {
      setDownloadingZip(false);
    }
  };

  const formatSize = (bytes: number) =>
    bytes < 1024 ? `${bytes} B` : bytes < 1024 * 1024 ? `${(bytes / 1024).toFixed(1)} KB` : `${(bytes / 1048576).toFixed(1)} MB`;

  const formatearDetalle = (detalle: Record<string, string>) => {
    const etiquetas: Record<string, string> = {
      nombre: 'Nombre', predio: 'Predio', municipio: 'Municipio',
      tipo_solicitud: 'Tipo solicitud', titular: 'Titular', autoridad: 'Autoridad',
      origen: 'Origen',
    };
    const pares = Object.entries(detalle)
      .filter(([, v]) => v !== undefined && v !== null && String(v).trim() !== '')
      .map(([k, v]) => `${etiquetas[k] || k}: ${v}`);
    return pares.length > 0 ? pares.join(' · ') : '—';
  };

  const paginar = <T,>(lista: T[]): { items: T[]; totalPages: number } => {
    const totalPages = Math.max(1, Math.ceil(lista.length / PAGE_SIZE));
    const current = Math.min(page, totalPages);
    const start = (current - 1) * PAGE_SIZE;
    return { items: lista.slice(start, start + PAGE_SIZE), totalPages };
  };

  const downloadReportCsv = () => {
    if (!reporte) return;
    const t = reporte.totales;
    const lineas: string[] = [];
    lineas.push('Indicador,Valor');
    lineas.push(`Solicitudes,${t.solicitudes}`);
    lineas.push(`Usuarios,${t.usuarios}`);
    lineas.push(`Bytes almacenados,${t.bytes}`);
    lineas.push('');
    lineas.push('Tipo,Cantidad');
    Object.entries(reporte.por_tipo).forEach(([k, v]) => lineas.push(`${k},${v}`));
    lineas.push('');
    lineas.push('Mes,Solicitudes');
    Object.entries(reporte.por_mes).forEach(([k, v]) => lineas.push(`${k},${v}`));
    lineas.push('');
    lineas.push('Usuario,Email,Solicitudes');
    reporte.top_usuarios.forEach((u) => lineas.push(`"${u.nombre}",${u.email},${u.total}`));
    const csv = lineas.join('\n');
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const url = window.URL.createObjectURL(blob);
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = `reporte_${new Date().toISOString().slice(0, 10)}.csv`;
    document.body.appendChild(anchor);
    anchor.click();
    anchor.remove();
    window.URL.revokeObjectURL(url);
  };

  const formatDateTime = (iso: string) =>
    new Date(iso).toLocaleString('es-CO', { dateStyle: 'short', timeStyle: 'short' });

  const getStatusLabel = (status: Request['status']) => {
    const labels: Record<Request['status'], string> = {
      pendiente: 'Pendiente',
      en_revision: 'En revisión',
      aprobado: 'Aprobado',
      rechazado: 'Rechazado',
    };
    return labels[status];
  };

  const getStatusClass = (status: Request['status']) => {
    const classes: Record<Request['status'], string> = {
      pendiente: 'status-pending',
      en_revision: 'status-review',
      aprobado: 'status-approved',
      rechazado: 'status-rejected',
    };
    return classes[status];
  };

  const badgeIA = (v?: ValidacionIA) => {
    if (!v) return <span className="ia-badge ia-neutro" title="Sin revisión automática">—</span>;
    if (v.apto === null) {
      return <span className="ia-badge ia-neutro" title={v.resumen}>Manual</span>;
    }
    if (v.apto) {
      return (
        <span className="ia-badge ia-ok" title={`${v.resumen} (puntaje ${v.puntaje}/100)`}>
          Correcto ({v.puntaje})
        </span>
      );
    }
    return (
      <span
        className="ia-badge ia-alerta"
        title={`${v.resumen}\n${v.faltantes.map((f) => `• ${f.campo}${f.detalle ? `: ${f.detalle}` : ''}`).join('\n')}`}
      >
        {v.faltantes.length} por corregir ({v.puntaje})
      </span>
    );
  };

  const roleLabel: Record<UserRole, string> = {
    admin: 'Admin',
    consultor: 'Consultor',
    cliente: 'Usuario',
  };

  if (!isAdmin) {
    return (
      <div className="app-shell">
        <Navbar />
        <main className="admin-page">
          <div className="shell">
            <div className="admin-denied">
              <Shield size={64} className="denied-icon" />
              <h2>Acceso denegado</h2>
              <p>No tienes permisos de administrador para acceder a esta página.</p>
            </div>
          </div>
        </main>
        <Footer />
      </div>
    );
  }

  const usuariosPaginados = paginar(filteredUsers);
  const solicitudesPaginadas = paginar(filteredRequests);
  const docsPaginados = paginar(filteredDocs);
  const detallePaginado = paginar(detalle);

  return (
    <div className="app-shell">
      <Navbar />
      <main className="admin-page">
        <div className="shell">
          <header className="admin-header">
            <div>
              <h1>Panel de Administración</h1>
              <p>Gestiona usuarios y solicitudes del sistema</p>
            </div>
            <div className="admin-stats">
              <div className="stat-card">
                <span className="stat-value">{users.length}</span>
                <span className="stat-label">Usuarios totales</span>
              </div>
              <div className="stat-card">
                <span className="stat-value">{docs.filter(r => r.estado === 'pendiente').length}</span>
                <span className="stat-label">Solicitudes pendientes</span>
              </div>
              <div className="stat-card">
                <span className="stat-value">{docs.filter(r => r.estado === 'aprobado').length}</span>
                <span className="stat-label">Solicitudes aprobadas</span>
              </div>
              <div className="stat-card">
                <span className="stat-value">{docs.filter(r => r.resumen?.validacion_ia?.apto === false).length}</span>
                <span className="stat-label">Con observaciones IA</span>
              </div>
            </div>
          </header>

          {error && <div className="auth-error" role="alert">{error}</div>}
          {loading && <div className="loading">Cargando datos del servidor…</div>}

          <div className="admin-tabs">
            <button
              className={activeTab === 'users' ? 'active' : ''}
              onClick={() => setActiveTab('users')}
            >
              <User size={18} /> Usuarios ({users.length})
            </button>
            <button
              className={activeTab === 'requests' ? 'active' : ''}
              onClick={() => setActiveTab('requests')}
            >
              <Mail size={18} /> Solicitudes ({docs.length})
            </button>
            <button
              className={activeTab === 'docs' ? 'active' : ''}
              onClick={() => setActiveTab('docs')}
            >
              <Eye size={18} /> Documentos ({docs.length})
            </button>
            <button
              className={activeTab === 'reports' ? 'active' : ''}
              onClick={() => setActiveTab('reports')}
            >
              <BarChart2 size={18} /> Reportes
            </button>
          </div>

          {activeTab === 'users' && (
            <section className="admin-section">
              <div className="section-toolbar">
                <div className="search-box">
                  <Search size={18} />
                  <input
                    type="text"
                    placeholder="Buscar usuario..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                  />
                </div>
                <div className="filter-group">
                  <Filter size={18} />
                  <select value={roleFilter} onChange={(e) => setRoleFilter(e.target.value as 'all' | UserRole)}>
                    <option value="all">Todos los roles</option>
                    <option value="admin">Administradores</option>
                    <option value="consultor">Consultores</option>
                    <option value="cliente">Clientes</option>
                  </select>
                </div>
                <button className="btn-secondary btn-limpiar" onClick={limpiarFiltros} title="Limpiar filtros">
                  <Eraser size={16} /> Limpiar filtros
                </button>
              </div>

              <div className="table-container">
                <table className="admin-table">
                  <thead>
                    <tr>
                      <th>Usuario</th>
                      <th>Email</th>
                      <th>Rol</th>
                      <th>Estado</th>
                      <th>Fecha registro</th>
                      <th>Acciones</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredUsers.length === 0 ? (
                      <tr>
                        <td colSpan={6} className="empty-state">No hay usuarios</td>
                      </tr>
                    ) : (
                      usuariosPaginados.items.map(u => (
                        <tr key={u.id}>
                          <td>
                            <div className="user-info">
                              <div className="user-avatar">{u.name.charAt(0).toUpperCase()}</div>
                              <span>{u.name}</span>
                            </div>
                          </td>
                          <td>{u.email}</td>
                          <td>
                            <span className={`role-badge ${u.role === 'admin' ? 'admin' : 'user'}`}>
                              {u.role === 'admin' ? <Shield size={14} /> : <User size={14} />}
                              {roleLabel[u.role]}
                            </span>
                          </td>
                          <td>
                            <span className={`status-badge ${u.activo ? 'status-approved' : 'status-rejected'}`}>
                              {u.activo ? 'Activo' : 'Inactivo'}
                            </span>
                          </td>
                          <td>{new Date(u.createdAt).toLocaleDateString('es-ES')}</td>
                          <td>
                            <div className="action-menu">
                              <button className="action-btn" onClick={() => void cycleUserRole(u)} title="Cambiar rol">
                                {u.role === 'admin' ? <User size={16} /> : <Shield size={16} />}
                              </button>
                              <button
                                className="action-btn"
                                onClick={() => void toggleUserActive(u)}
                                title={u.activo ? 'Desactivar' : 'Activar'}
                                disabled={u.id === user?.id && u.activo}
                              >
                                <Eye size={16} />
                              </button>
                              <button className="action-btn danger" onClick={() => handleDeleteUser(u.id)} title="Eliminar">
                                <Trash2 size={16} />
                              </button>
                            </div>
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
              <Paginador page={page} totalPages={usuariosPaginados.totalPages} onChange={setPage} />
            </section>
          )}

          {activeTab === 'requests' && (
            <section className="admin-section">
              <div className="section-toolbar">
                <div className="search-box">
                  <Search size={18} />
                  <input
                    type="text"
                    placeholder="Buscar solicitud..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                  />
                </div>
                <div className="filter-group">
                  <Filter size={18} />
                  <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value as 'all' | Request['status'])}>
                    <option value="all">Todos los estados</option>
                    <option value="pendiente">Pendiente</option>
                    <option value="en_revision">En revisión</option>
                    <option value="aprobado">Aprobado</option>
                    <option value="rechazado">Rechazado</option>
                  </select>
                </div>
                <button className="btn-secondary btn-limpiar" onClick={limpiarFiltros} title="Limpiar filtros">
                  <Eraser size={16} /> Limpiar filtros
                </button>
              </div>

              <div className="table-container">
                <table className="admin-table">
                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>Usuario</th>
                      <th>Tipo</th>
                      <th>Revisión IA</th>
                      <th>Estado</th>
                      <th>Fecha creación</th>
                      <th>Acciones</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredRequests.length === 0 ? (
                      <tr>
                        <td colSpan={7} className="empty-state">No hay solicitudes</td>
                      </tr>
                    ) : (
                      solicitudesPaginadas.items.map((r) => (
                        <tr key={r.id}>
                          <td className="request-id">#{r.id}</td>
                          <td>
                            <div className="user-info">
                              <div className="user-avatar">{r.usuario_nombre.charAt(0).toUpperCase()}</div>
                              <span>{r.usuario_nombre}<br /><small>{r.usuario_email}</small></span>
                            </div>
                          </td>
                          <td><span className="type-badge">{r.tipo.toUpperCase()}</span></td>
                          <td>{badgeIA(r.resumen?.validacion_ia)}</td>
                          <td>
                            <span className={`status-badge ${getStatusClass(r.estado as Request['status'])}`}>
                              {getStatusLabel(r.estado as Request['status'])}
                            </span>
                          </td>
                          <td>{new Date(r.creado_en).toLocaleDateString('es-ES')}</td>
                          <td>
                            <div className="action-menu">
                              <select
                                value={r.estado}
                                onChange={(e) => void actualizarEstadoSolicitud(r.id, e.target.value)}
                                className="status-select"
                              >
                                <option value="pendiente">Pendiente</option>
                                <option value="en_revision">En revisión</option>
                                <option value="aprobado">Aprobado</option>
                                <option value="rechazado">Rechazado</option>
                              </select>
                            </div>
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
              <Paginador page={page} totalPages={solicitudesPaginadas.totalPages} onChange={setPage} />
            </section>
          )}

          {activeTab === 'docs' && (
            <section className="admin-section">
              <div className="section-toolbar report-toolbar">
                <div className="search-box">
                  <Search size={18} />
                  <input
                    type="text"
                    placeholder="Buscar por usuario o archivo..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                  />
                </div>
                <div className="report-filters">
                  <label className="field">
                    <span>Usuario</span>
                    <select
                      value={userFilter === 'all' ? 'all' : String(userFilter)}
                      onChange={(e) => setUserFilter(e.target.value === 'all' ? 'all' : Number(e.target.value))}
                    >
                      <option value="all">Todos los usuarios</option>
                      {users.map((u) => (
                        <option key={u.id} value={u.id}>{u.name} ({u.email})</option>
                      ))}
                    </select>
                  </label>
                  <label className="field">
                    <span>Tipo</span>
                    <select value={docTipoFilter} onChange={(e) => setDocTipoFilter(e.target.value)}>
                      <option value="all">Todos los tipos</option>
                      {(reporte?.tipos_disponibles || TIPOS_DOCUMENTO).map((t) => (
                        <option key={t.tipo} value={t.tipo}>{t.label}</option>
                      ))}
                    </select>
                  </label>
                  <label className="field">
                    <span>Desde</span>
                    <input type="date" value={docDesde} onChange={(e) => setDocDesde(e.target.value)} />
                  </label>
                  <label className="field">
                    <span>Hasta</span>
                    <input type="date" value={docHasta} onChange={(e) => setDocHasta(e.target.value)} />
                  </label>
                </div>
                <button
                  className="btn-primary btn-zip"
                  onClick={() => void downloadZip()}
                  disabled={selectedDocs.length === 0 || downloadingZip}
                >
                  {downloadingZip ? 'Generando ZIP…' : `Descargar ZIP (${selectedDocs.length})`}
                </button>
                <button className="btn-secondary btn-limpiar" onClick={limpiarFiltros} title="Limpiar filtros">
                  <Eraser size={16} /> Limpiar filtros
                </button>
              </div>

              <div className="table-container">
                <table className="admin-table">
                  <thead>
                    <tr>
                      <th>
                        <input
                          type="checkbox"
                          checked={filteredDocs.length > 0 && selectedDocs.length === filteredDocs.length}
                          onChange={toggleAllDocs}
                          aria-label="Seleccionar todos"
                        />
                      </th>
                      <th>Usuario</th>
                      <th>Archivo</th>
                      <th>Tipo</th>
                      <th>Tamaño</th>
                      <th>Fecha y hora</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredDocs.length === 0 ? (
                      <tr>
                        <td colSpan={6} className="empty-state">No hay documentos exportados</td>
                      </tr>
                    ) : (
                      docsPaginados.items.map((d) => (
                        <tr key={d.id}>
                          <td>
                            <input
                              type="checkbox"
                              checked={selectedDocs.includes(d.id)}
                              onChange={() => toggleDoc(d.id)}
                              aria-label={`Seleccionar ${d.nombre_archivo}`}
                            />
                          </td>
                          <td>
                            <div className="user-info">
                              <div className="user-avatar">{d.usuario_nombre.charAt(0).toUpperCase()}</div>
                              <span>{d.usuario_nombre}<br /><small>{d.usuario_email}</small></span>
                            </div>
                          </td>
                          <td className="request-id">{d.nombre_archivo}</td>
                          <td><span className="type-badge">{d.tipo.toUpperCase()}</span></td>
                          <td>{formatSize(d.tamano_bytes)}</td>
                          <td>{formatDateTime(d.creado_en)}</td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
              <Paginador page={page} totalPages={docsPaginados.totalPages} onChange={setPage} />
            </section>
          )}

          {activeTab === 'reports' && (
            <section className="admin-section admin-section--wide">
              <div className="section-toolbar">
                <h2 className="section-title">Reportes y métricas</h2>
                <button className="btn-secondary btn-limpiar" onClick={limpiarFiltros} title="Limpiar filtros">
                  <Eraser size={16} /> Limpiar filtros
                </button>
                <button className="btn-primary" onClick={downloadReportCsv} disabled={!reporte && detalle.length === 0}>
                  <Download size={16} /> Exportar CSV
                </button>
              </div>

              {reportLoading && <div className="loading">Generando reporte…</div>}

              {reporte && !reportLoading && (
                <>
                  <div className="report-cards">
                    <div className="stat-card">
                      <span className="stat-value">{reporte.totales.solicitudes}</span>
                      <span className="stat-label">Solicitudes</span>
                    </div>
                    <div className="stat-card">
                      <span className="stat-value">{reporte.totales.usuarios}</span>
                      <span className="stat-label">Usuarios</span>
                    </div>
                    <div className="stat-card">
                      <span className="stat-value">{formatSize(reporte.totales.bytes)}</span>
                      <span className="stat-label">Almacenamiento</span>
                    </div>
                  </div>

                  <div className="report-grid">
                    <div className="report-panel">
                      <h3>Solicitudes por tipo</h3>
                      {Object.keys(reporte.por_tipo).length === 0 ? (
                        <p className="report-empty">Sin datos</p>
                      ) : (
                        <table className="admin-table">
                          <thead><tr><th>Tipo</th><th>Cantidad</th></tr></thead>
                          <tbody>
                            {Object.entries(reporte.por_tipo).map(([k, v]) => (
                              <tr key={k}><td><span className="type-badge">{k.toUpperCase()}</span></td><td>{v}</td></tr>
                            ))}
                          </tbody>
                        </table>
                      )}
                    </div>

                    <div className="report-panel">
                      <h3>Solicitudes por mes</h3>
                      {Object.keys(reporte.por_mes).length === 0 ? (
                        <p className="report-empty">Sin datos</p>
                      ) : (
                        <table className="admin-table">
                          <thead><tr><th>Mes</th><th>Solicitudes</th></tr></thead>
                          <tbody>
                            {Object.entries(reporte.por_mes).map(([k, v]) => (
                              <tr key={k}><td>{k}</td><td>{v}</td></tr>
                            ))}
                          </tbody>
                        </table>
                      )}
                    </div>
                  </div>
                </>
              )}

              <div className="report-panel report-panel--wide" style={{ marginTop: 16 }}>
                <h3>Detalle de documentos (filtros)</h3>
                <div className="report-filters">
                  <label className="field">
                    <span>Usuario</span>
                    <select value={filtroUsuario === 'all' ? 'all' : String(filtroUsuario)} onChange={(e) => setFiltroUsuario(e.target.value === 'all' ? 'all' : Number(e.target.value))}>
                      <option value="all">Todos</option>
                      {users.map((u) => (
                        <option key={u.id} value={u.id}>{u.name} ({u.email})</option>
                      ))}
                    </select>
                  </label>
                  <label className="field">
                    <span>Trámite (tipo)</span>
                    <select value={filtroTipo} onChange={(e) => setFiltroTipo(e.target.value)}>
                      <option value="all">Todos</option>
                      {(reporte?.tipos_disponibles || []).map((t) => (
                        <option key={t.tipo} value={t.tipo}>{t.label}</option>
                      ))}
                    </select>
                  </label>
                  <label className="field">
                    <span>Desde</span>
                    <input type="date" value={filtroDesde} onChange={(e) => setFiltroDesde(e.target.value)} />
                  </label>
                  <label className="field">
                    <span>Hasta</span>
                    <input type="date" value={filtroHasta} onChange={(e) => setFiltroHasta(e.target.value)} />
                  </label>
                </div>

                <div className="table-container">
                  <table className="admin-table">
                    <thead>
                      <tr>
                        <th>Usuario</th>
                        <th>Trámite</th>
                        <th>Detalle</th>
                        <th>Archivo</th>
                        <th>Tamaño</th>
                        <th>Fecha</th>
                      </tr>
                    </thead>
                    <tbody>
                      {detalle.length === 0 ? (
                        <tr><td colSpan={6} className="empty-state">Sin documentos para los filtros seleccionados</td></tr>
                      ) : (
                        detallePaginado.items.map((r) => (
                          <tr key={r.id}>
                            <td>
                              <div className="user-info">
                                <div className="user-avatar">{r.usuario_nombre.charAt(0).toUpperCase()}</div>
                                <span>{r.usuario_nombre}<br /><small>{r.usuario_email}</small></span>
                              </div>
                            </td>
                            <td><span className="type-badge">{r.tipo_label}</span></td>
                            <td className="report-detalle">{formatearDetalle(r.detalle)}</td>
                            <td className="request-id">{r.nombre_archivo}</td>
                            <td>{formatSize(r.tamano_bytes)}</td>
                            <td>{r.creado_en ? formatDateTime(r.creado_en) : '—'}</td>
                          </tr>
                        ))
                      )}
                    </tbody>
                  </table>
                </div>
                <p className="report-empty" style={{ marginTop: 8 }}>{detalle.length} documento(s)</p>
                <Paginador page={page} totalPages={detallePaginado.totalPages} onChange={setPage} />
              </div>
            </section>
          )}

          {showDeleteConfirm !== null && (
            <div className="modal-overlay" onClick={() => setShowDeleteConfirm(null)}>
              <div className="modal" onClick={(e) => e.stopPropagation()}>
                <h3>Eliminar usuario</h3>
                <p>¿Estás seguro de que quieres eliminar este usuario? Esta acción no se puede deshacer.</p>
                <div className="modal-actions">
                  <button className="btn-secondary" onClick={() => setShowDeleteConfirm(null)}>Cancelar</button>
                  <button className="btn-primary danger" onClick={() => showDeleteConfirm !== null && void confirmDeleteUser(showDeleteConfirm)}>Eliminar</button>
                </div>
              </div>
            </div>
          )}
        </div>
      </main>
      <Footer />
    </div>
  );
};

function Paginador({ page, totalPages, onChange }: { page: number; totalPages: number; onChange: (p: number) => void }) {
  if (totalPages <= 1) return null;
  return (
    <div className="paginador">
      <button className="paginador-btn" onClick={() => onChange(Math.max(1, page - 1))} disabled={page <= 1} aria-label="Página anterior">
        <ChevronLeft size={16} />
      </button>
      <span className="paginador-info">Página {page} de {totalPages}</span>
      <button className="paginador-btn" onClick={() => onChange(Math.min(totalPages, page + 1))} disabled={page >= totalPages} aria-label="Página siguiente">
        <ChevronRight size={16} />
      </button>
    </div>
  );
}

export default AdminPage;
