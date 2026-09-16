import { useEffect, useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import { AlertCircle, CheckCircle, CloudUpload, FileText, Loader2, Sparkles } from 'lucide-react';
import { api, ValidacionIA } from '../../services/api';

interface FormatUploadProps {
  /** Clave del tipo de solicitud aceptada por el backend (fun, f1, f2, f3, fg1, fg2). */
  tipo: string;
  /** Extensiones aceptadas, p. ej. ".xlsx,.xls". */
  accept: string;
  /** Texto de ayuda bajo el campo. */
  ayuda?: string;
  /** URL pública de la plantilla descargable (opcional). */
  plantillaUrl?: string;
  /** Nombre con el que se mostrará/descarga la plantilla. */
  plantillaNombre?: string;
  /** Varias plantillas descargables (entidades con más de un formato). */
  plantillas?: Array<{ url: string; nombre: string }>;
}

type EstadoRevision =
  | { fase: 'idle' }
  | { fase: 'revisando' }
  | { fase: 'lista'; validacion: ValidacionIA };

const POLL_INTERVALO_MS = 5_000;
const POLL_MAX_INTENTOS = 30; // ~2.5 min
const MAX_BYTES = 4 * 1024 * 1024; // alineado con el límite del backend (Vercel)

export const FormatUpload: React.FC<FormatUploadProps> = ({
  tipo,
  accept,
  ayuda,
  plantillaUrl,
  plantillaNombre,
  plantillas,
}) => {
  const inputRef = useRef<HTMLInputElement>(null);
  const [archivo, setArchivo] = useState<File | null>(null);
  const [subiendo, setSubiendo] = useState(false);
  const [mensaje, setMensaje] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const [revision, setRevision] = useState<EstadoRevision>({ fase: 'idle' });
  const [solicitudId, setSolicitudId] = useState<number | null>(null);

  // Consulta el dictamen IA hasta que esté listo (la validación corre en background).
  useEffect(() => {
    if (revision.fase !== 'revisando' || solicitudId === null) return;
    let intentos = 0;
    const intervalo = setInterval(() => {
      intentos += 1;
      void (async () => {
        try {
          const resp = await api.getValidacionSolicitud(solicitudId);
          if (resp.estado_validacion === 'lista' && resp.validacion) {
            clearInterval(intervalo);
            setRevision({ fase: 'lista', validacion: resp.validacion });
          } else if (intentos >= POLL_MAX_INTENTOS) {
            clearInterval(intervalo);
            setRevision({
              fase: 'lista',
              validacion: {
                apto: null, puntaje: null, faltantes: [],
                observaciones: ['La revisión IA tardó más de lo esperado. Consulta el resultado en «Mis solicitudes».'],
                resumen: 'Revisión en curso: verás el resultado en «Mis solicitudes» en unos segundos.',
              },
            });
          }
        } catch {
          // reintenta en el siguiente tick
        }
      })();
    }, POLL_INTERVALO_MS);
    return () => clearInterval(intervalo);
  }, [revision.fase, solicitudId]);

  const handleSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0] ?? null;
    if (file && file.size > MAX_BYTES) {
      setArchivo(null);
      if (inputRef.current) inputRef.current.value = '';
      setMensaje({
        type: 'error',
        text: `El archivo pesa ${(file.size / 1048576).toFixed(1)} MB; el máximo permitido es 4 MB. Comprímelo o divídelo e inténtalo de nuevo.`,
      });
      return;
    }
    setArchivo(file);
    setMensaje(null);
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!archivo || subiendo) return;
    setSubiendo(true);
    setMensaje(null);
    setRevision({ fase: 'idle' });
    try {
      const respuesta = await api.subirDocumento(tipo, archivo, archivo.name) as { id?: number };
      setMensaje({
        type: 'success',
        text: 'Documento enviado correctamente.',
      });
      setArchivo(null);
      if (inputRef.current) inputRef.current.value = '';
      if (respuesta?.id != null) {
        setSolicitudId(respuesta.id);
        setRevision({ fase: 'revisando' });
      }
    } catch (err) {
      const detalle = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      setMensaje({ type: 'error', text: detalle ?? 'No se pudo subir el documento. Inténtalo de nuevo.' });
    } finally {
      setSubiendo(false);
    }
  };

  const v = revision.fase === 'lista' ? revision.validacion : null;

  return (
    <form className="format-upload" onSubmit={handleSubmit}>
      {plantillaUrl && (
        <p className="format-upload-plantilla">
          ¿No tienes la plantilla? <a href={plantillaUrl} download={plantillaNombre}>Descárgala aquí</a>, dilienciala en tu equipo y súbela.
        </p>
      )}
      {plantillas && plantillas.length > 0 && (
        <div className="format-upload-plantillas">
          <p>Descarga la plantilla que necesites, diliénciala en tu equipo y súbela:</p>
          <ul>
            {plantillas.map((p) => (
              <li key={p.url}>
                <a href={p.url} download>{p.nombre}</a>
              </li>
            ))}
          </ul>
        </div>
      )}

      <label className="format-upload-dropzone" htmlFor={`format-upload-${tipo}`}>
        <CloudUpload size={32} aria-hidden />
        <span>{archivo ? 'Cambiar archivo' : 'Seleccionar archivo'}</span>
        <input
          id={`format-upload-${tipo}`}
          ref={inputRef}
          type="file"
          accept={accept}
          onChange={handleSelect}
          hidden
        />
      </label>

      {archivo && (
        <p className="format-upload-file">
          <FileText size={16} aria-hidden />
          {archivo.name} — {(archivo.size / 1024).toFixed(0)} KB
        </p>
      )}

      {ayuda && <p className="format-upload-ayuda">{ayuda}</p>}
      <p className="format-upload-ayuda">Tamaño máximo: 4 MB.</p>

      <button className="btn-primary" type="submit" disabled={!archivo || subiendo}>
        {subiendo ? (
          <>
            <Loader2 className="spin" size={18} /> Subiendo…
          </>
        ) : (
          'Analizar documento'
        )}
      </button>

      {mensaje && (
        <div className={`formato-message ${mensaje.type}`} role="alert">
          {mensaje.type === 'success' ? <CheckCircle size={20} /> : <AlertCircle size={20} />}
          {mensaje.text}
        </div>
      )}

      {revision.fase === 'revisando' && (
        <div className="ia-panel ia-panel-revisando" role="status">
          <Loader2 className="spin" size={22} />
          <p>La IA está revisando tu documento… suele tardar unos segundos.</p>
        </div>
      )}

      {v && (
        <section
          className={`ia-panel ${v.apto === true ? 'ia-panel-ok' : v.apto === false ? 'ia-panel-alerta' : 'ia-panel-neutro'}`}
          aria-live="polite"
        >
          <header className="ia-panel-header">
            {v.apto === true ? (
              <span className="ia-badge ia-ok"><CheckCircle size={16} /> Documento completo</span>
            ) : v.apto === false ? (
              <span className="ia-badge ia-alerta"><AlertCircle size={16} /> {v.faltantes.length} punto(s) por corregir</span>
            ) : (
              <span className="ia-badge ia-neutro">Revisión manual</span>
            )}
            {v.puntaje != null && <span className="ia-panel-puntaje">Puntaje: {v.puntaje}/100</span>}
          </header>

          <p className="ia-panel-resumen">
            <Sparkles size={15} aria-hidden /> {v.resumen}
          </p>

          {v.faltantes.length > 0 && (
            <div className="ia-panel-bloque">
              <strong>Campos por corregir:</strong>
              <ul>
                {v.faltantes.map((f, i) => (
                  <li key={i}>
                    <span className="ia-faltante-campo">{f.campo}</span>
                    {f.detalle ? ` — ${f.detalle}` : ''}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {v.observaciones.length > 0 && (
            <div className="ia-panel-bloque">
              <strong>Observaciones:</strong>
              <ul>
                {v.observaciones.map((o, i) => <li key={i}>{o}</li>)}
              </ul>
            </div>
          )}

          {v.apto === false && (
            <p className="ia-panel-cta">
              Corrige el documento en tu equipo y súbelo de nuevo aquí mismo.
            </p>
          )}

          <p className="ia-panel-final">
            También puedes verlo luego en <Link to="/mis-solicitudes">Mis solicitudes</Link>.
          </p>
        </section>
      )}
    </form>
  );
};

export default FormatUpload;
