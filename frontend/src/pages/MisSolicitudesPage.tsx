import { Fragment, useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { AlertCircle, CheckCircle, ChevronDown, ChevronUp, Download, FileText, Loader2 } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { api, ValidacionIA } from '../services/api';
import { Navbar } from '../components/comunes/Navbar';
import { Footer } from '../components/comunes/Footer';

interface SolicitDoc {
  id: number;
  tipo: string;
  nombre_archivo: string;
  tamano_bytes: number;
  creado_en: string;
  resumen?: { validacion_ia?: ValidacionIA } & Record<string, unknown>;
}

const TIPOS_CON_VALIDACION = /\.(pdf|docx|xlsx?|txt|csv)$/i;

const MisSolicitudesPage: React.FC = () => {
  const { isAuthenticated } = useAuth();
  const [docs, setDocs] = useState<SolicitDoc[]>([]);
  const [selected, setSelected] = useState<number[]>([]);
  const [expandido, setExpandido] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  const load = useCallback(async (mostrarCargando = true) => {
    if (!isAuthenticated) return;
    if (mostrarCargando) setLoading(true);
    setError('');
    try {
      setDocs(await api.listMisSolicitudes());
    } catch {
      setError('No se pudieron cargar tus solicitudes.');
    } finally {
      if (mostrarCargando) setLoading(false);
    }
  }, [isAuthenticated]);

  useEffect(() => {
    void load();
  }, [load]);

  // Mientras haya documentos sin dictamen IA, refrescar cada 10 s (máx. 2 min).
  useEffect(() => {
    const hayPendientes = docs.some(
      (d) => TIPOS_CON_VALIDACION.test(d.nombre_archivo) && !d.resumen?.validacion_ia
    );
    if (!hayPendientes) return;
    let intentos = 0;
    const intervalo = setInterval(() => {
      intentos += 1;
      if (intentos > 12) {
        clearInterval(intervalo);
        return;
      }
      void load(false);
    }, 10_000);
    return () => clearInterval(intervalo);
  }, [docs, load]);

  const saveBlob = (blob: unknown, filename: string, type: string) => {
    const url = window.URL.createObjectURL(new Blob([blob as BlobPart], { type }));
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = filename;
    document.body.appendChild(anchor);
    anchor.click();
    anchor.remove();
    window.URL.revokeObjectURL(url);
  };

  const downloadOne = async (d: SolicitDoc) => {
    setBusy(true);
    try {
      saveBlob(await api.downloadSolicitud(d.id), d.nombre_archivo, 'application/octet-stream');
    } catch {
      setError('No se pudo descargar el documento.');
    } finally {
      setBusy(false);
    }
  };

  const downloadZip = async () => {
    if (selected.length === 0) return;
    setBusy(true);
    try {
      const stamp = new Date().toISOString().slice(0, 16).replace(/[-:T]/g, '');
      saveBlob(await api.downloadSolicitudesZip(selected), `mis_solicitudes_${stamp}.zip`, 'application/zip');
    } catch {
      setError('No se pudo descargar el ZIP.');
    } finally {
      setBusy(false);
    }
  };

  const formatSize = (bytes: number) =>
    bytes < 1024 ? `${bytes} B` : bytes < 1024 * 1024 ? `${(bytes / 1024).toFixed(1)} KB` : `${(bytes / 1048576).toFixed(1)} MB`;

  const badgeIA = (d: SolicitDoc) => {
    if (!TIPOS_CON_VALIDACION.test(d.nombre_archivo)) {
      return <span className="ia-badge ia-neutro" title="Este tipo de archivo no admite revisión automática">—</span>;
    }
    const v = d.resumen?.validacion_ia;
    if (!v) {
      return (
        <span className="ia-badge ia-pendiente" title="Revisión IA en curso">
          <Loader2 className="spin" size={14} /> Revisando…
        </span>
      );
    }
    if (v.apto === null) {
      return <span className="ia-badge ia-neutro" title={v.resumen}>Revisión manual</span>;
    }
    return v.apto ? (
      <span className="ia-badge ia-ok" title={`Puntaje ${v.puntaje}/100`}>
        <CheckCircle size={14} /> Diligenciado
      </span>
    ) : (
      <span className="ia-badge ia-alerta" title={`Puntaje ${v.puntaje}/100`}>
        <AlertCircle size={14} /> {v.faltantes.length} por corregir
      </span>
    );
  };

  return (
    <div className="app-shell">
      <Navbar />
      <main className="admin-page">
        <div className="shell">
          <header className="admin-header">
            <div>
              <h1>Mis solicitudes</h1>
              <p>Historial de los documentos que has generado, de más reciente a más antiguo</p>
            </div>
          </header>

          {error && <div className="auth-error" role="alert">{error}</div>}

          <section className="admin-section">
            <div className="section-toolbar">
              <span>{docs.length} documento(s)</span>
              <button className="btn-primary" onClick={() => void downloadZip()} disabled={selected.length === 0 || busy}>
                {busy ? 'Descargando…' : `Descargar ZIP (${selected.length})`}
              </button>
            </div>
            <div className="table-container">
              <table className="admin-table">
                <thead>
                  <tr>
                    <th>
                      <input
                        type="checkbox"
                        checked={docs.length > 0 && selected.length === docs.length}
                        onChange={() => setSelected((prev) => (prev.length === docs.length ? [] : docs.map((d) => d.id)))}
                        aria-label="Seleccionar todos"
                      />
                    </th>
                    <th>Archivo</th>
                    <th>Tipo</th>
                    <th>Tamaño</th>
                    <th>Fecha y hora</th>
                    <th>Revisión IA</th>
                    <th>Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  {loading ? (
                    <tr><td colSpan={7} className="empty-state">Cargando…</td></tr>
                  ) : docs.length === 0 ? (
                    <tr><td colSpan={7} className="empty-state">Aún no has generado documentos. Crea tu primera solicitud.</td></tr>
                  ) : (
                    docs.map((d) => {
                      const v = d.resumen?.validacion_ia;
                      const abierto = expandido === d.id;
                      return (
                        <Fragment key={d.id}>
                          <tr>
                            <td>
                              <input
                                type="checkbox"
                                checked={selected.includes(d.id)}
                                onChange={() => setSelected((prev) => (prev.includes(d.id) ? prev.filter((x) => x !== d.id) : [...prev, d.id]))}
                                aria-label={`Seleccionar ${d.nombre_archivo}`}
                              />
                            </td>
                            <td className="request-id"><FileText size={14} /> {d.nombre_archivo}</td>
                            <td><span className="type-badge">{d.tipo.toUpperCase()}</span></td>
                            <td>{formatSize(d.tamano_bytes)}</td>
                            <td>{new Date(d.creado_en).toLocaleString('es-CO', { dateStyle: 'short', timeStyle: 'short' })}</td>
                            <td>
                              {badgeIA(d)}
                              {v && (
                                <button
                                  className="action-btn"
                                  onClick={() => setExpandido(abierto ? null : d.id)}
                                  title={abierto ? 'Ocultar detalle' : 'Ver detalle de la revisión'}
                                >
                                  {abierto ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                                </button>
                              )}
                            </td>
                            <td>
                              <button className="action-btn" onClick={() => void downloadOne(d)} title="Descargar" disabled={busy}>
                                <Download size={16} />
                              </button>
                            </td>
                          </tr>
                          {abierto && v && (
                            <tr className="ia-detalle">
                              <td colSpan={7}>
                                <div className={`ia-detalle-panel ${v.apto === false ? 'ia-detalle-alerta' : ''}`}>
                                  <p className="ia-detalle-resumen"><strong>Dictamen IA:</strong> {v.resumen}</p>
                                  {v.faltantes.length > 0 && (
                                    <div className="ia-detalle-faltantes">
                                      <strong>Campos por corregir:</strong>
                                      <ul>
                                        {v.faltantes.map((f, i) => (
                                          <li key={i}>
                                            <span className="ia-faltante-campo">{f.campo}</span>
                                            {f.detalle ? ` — ${f.detalle}` : ''}
                                          </li>
                                        ))}
                                      </ul>
                                      <p>
                                        Corrige el documento en tu equipo y{' '}
                                        <Link to="/formatos">súbelo de nuevo desde Formatos</Link>.
                                      </p>
                                    </div>
                                  )}
                                  {v.observaciones.length > 0 && (
                                    <div className="ia-detalle-obs">
                                      <strong>Observaciones:</strong>
                                      <ul>{v.observaciones.map((o, i) => <li key={i}>{o}</li>)}</ul>
                                    </div>
                                  )}
                                </div>
                              </td>
                            </tr>
                          )}
                        </Fragment>
                      );
                    })
                  )}
                </tbody>
              </table>
            </div>
          </section>
        </div>
      </main>
      <Footer />
    </div>
  );
};

export default MisSolicitudesPage;
