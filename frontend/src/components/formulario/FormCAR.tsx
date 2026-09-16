import React, { useState, useCallback } from 'react';
import { Upload, FileText, AlertCircle, CheckCircle, X } from 'lucide-react';
import JSZip from 'jszip';
import { saveAs } from 'file-saver';
import { Navbar } from '../comunes/Navbar';
import { Footer } from '../comunes/Footer';
import '../formatos/formcar.css';

interface DocumentoRequerido {
  id: string;
  nombre: string;
  descripcion: string;
  obligatorio: boolean;
  archivo?: File;
  preview?: string;
}

const documentosIniciales: DocumentoRequerido[] = [
  {
    id: 'formato_unico',
    nombre: 'Formato Único Nacional de Solicitud',
    descripcion: 'Formato Único Nacional de Solicitud de Aprovechamiento Forestal y Manejo Sostenible de Flora Silvestre y los Productos Forestales No Maderables Nuevo/Prórroga. Debidamente diligenciado.',
    obligatorio: true
  },
  {
    id: 'certificado_libertad',
    nombre: 'Certificado de Libertad y Tradición',
    descripcion: 'Certificado de libertad y tradición expedido dentro de los dos (2) meses inmediatamente anteriores a la presentación de la solicitud. Si se trata de predio ajeno se anexará la prueba de la posesión o tenencia.',
    obligatorio: true
  },
  {
    id: 'autorizacion_propietario',
    nombre: 'Autorización del Propietario',
    descripcion: 'Autorización escrita del propietario cuando el solicitante no sea el mismo propietario del predio.',
    obligatorio: false
  },
  {
    id: 'croquis_acceso',
    nombre: 'Croquis de Acceso al Predio',
    descripcion: 'Croquis a mano alzada para acceso al predio.',
    obligatorio: true
  },
  {
    id: 'poder_apoderado',
    nombre: 'Poder para Apoderado',
    descripcion: 'Poder debidamente otorgado, cuando se actúa mediante abogado.',
    obligatorio: false
  },
  {
    id: 'certificado_existencia',
    nombre: 'Certificado de Existencia y Representación Legal',
    descripcion: 'Certificado de existencia y representación legal vigente, para el caso de personas jurídicas.',
    obligatorio: false
  }
];

export const FormCAR: React.FC = () => {
  const [documentos, setDocumentos] = useState<DocumentoRequerido[]>(documentosIniciales);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleFileChange = useCallback((documentoId: string, file: File) => {
    setDocumentos(prev => prev.map(doc => {
      if (doc.id === documentoId) {
        return { ...doc, archivo: file, preview: URL.createObjectURL(file) };
      }
      return doc;
    }));
    setMessage(null);
  }, []);

  const removeFile = useCallback((documentoId: string) => {
    setDocumentos(prev => prev.map(doc => {
      if (doc.id === documentoId) {
        if (doc.preview) URL.revokeObjectURL(doc.preview);
        return { ...doc, archivo: undefined, preview: undefined };
      }
      return doc;
    }));
    setMessage(null);
  }, []);

  const handleSubmit = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();

    // Validar documentos obligatorios
    const faltantes = documentos.filter(doc => doc.obligatorio && !doc.archivo);
    if (faltantes.length > 0) {
      setMessage({
        type: 'error',
        text: `Faltan documentos obligatorios: ${faltantes.map(d => d.nombre).join(', ')}`
      });
      return;
    }

    const adjuntos = documentos.filter(doc => doc.archivo);
    if (adjuntos.length === 0) {
      setMessage({ type: 'error', text: 'No hay documentos para generar el archivo comprimido.' });
      return;
    }

    setIsSubmitting(true);
    setMessage(null);

    try {
      const zip = new JSZip();
      adjuntos.forEach(doc => {
        if (doc.archivo) {
          zip.file(formatFileName(doc), doc.archivo);
        }
      });

      const blob = await zip.generateAsync({ type: 'blob', compression: 'DEFLATE' });
      const stamp = new Date().toISOString().slice(0, 10).replace(/-/g, '');
      saveAs(blob, `documentos_car_${stamp}.zip`);
      setMessage({ type: 'success', text: `Se generó el archivo comprimido con ${adjuntos.length} documento(s).` });
    } catch (error) {
      setMessage({ type: 'error', text: 'Error al generar el archivo comprimido.' });
    } finally {
      setIsSubmitting(false);
    }
  }, [documentos]);

  const handleClear = useCallback(() => {
    setDocumentos(prev => prev.map(doc => {
      if (doc.preview) URL.revokeObjectURL(doc.preview);
      return { ...doc, archivo: undefined, preview: undefined };
    }));
    setMessage(null);
  }, []);

  const getFileExtension = (filename: string) => {
    return filename.slice(filename.lastIndexOf('.') + 1).toUpperCase();
  };

  const formatFileName = (doc: DocumentoRequerido): string => {
    const extension = doc.archivo ? getFileExtension(doc.archivo.name).toLowerCase() : '';
    const prefijo = doc.id.replace(/_/g, '-');
    return `${prefijo}.${extension}`;
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const allRequiredComplete = documentos.filter(d => d.obligatorio).every(d => d.archivo);
  const totalFiles = documentos.filter(d => d.archivo).length;

  return (
    <div className="app-shell formcar-page">
      <Navbar />
      <main className="formato-page">
        <div className="formato-container">
          <header className="formato-header">
            <h1>Formulario CAR - Carga de Documentos</h1>
            <p>Adjunte los documentos requeridos para la solicitud ante la Corporación Autónoma Regional</p>
            <div className="formato-progress">
              <div className="progress-bar">
                <div className="progress-fill" style={{ width: `${documentos.filter(d => d.archivo).length / documentos.length * 100}%` }} />
              </div>
              <span>{documentos.filter(d => d.archivo).length} de {documentos.length} documentos cargados</span>
            </div>
          </header>

          <div className="formato-toolbar">
            <button className="btn-primary" onClick={handleSubmit} disabled={!allRequiredComplete || isSubmitting}>
              {isSubmitting ? 'Generando ZIP...' : 'Generar ZIP de documentos'}
            </button>
            {totalFiles > 0 && (
              <button className="btn-secondary" onClick={handleClear} title="Quitar todos los archivos cargados">
                Limpiar
              </button>
            )}
          </div>

          {message && (
            <div className={`formato-message ${message.type}`}>
              {message.type === 'success' ? <CheckCircle size={20} /> : <AlertCircle size={20} />}
              {message.text}
            </div>
          )}

          <div className="formato-form">
            <div className="form-section">
              <h2>Documentos Requeridos para CAR</h2>
              <p className="section-description">
                Cargue cada documento en su respectivo campo. Los marcados con * son obligatorios.
                Formatos aceptados: PDF, JPG, PNG (máx. 10MB c/u)
              </p>

              {/*
                Estilo inline forzado como blindaje: garantiza el grid de 3 columnas
                sin depender de la cascada CSS externa (que hasta ahora estaba
                ganándole a nuestras reglas, incluso con !important). Los breakpoints
                de 1100px y 760px siguen resolviéndose vía CSS con !important en
                formatos.css, que sí puede sobreescribir un inline style sin !important.
              */}
              <div
                className="documentos-grid"
                style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(3, 1fr)',
                  gap: '16px',
                  width: '100%',
                  alignItems: 'stretch',
                }}
              >
                {documentos.map((doc) => (
                  <article key={doc.id} className={`documento-card ${doc.archivo ? 'completo' : ''} ${doc.obligatorio ? 'obligatorio' : ''}`}>
                    <div className="documento-header">
                      <div className="documento-info">
                        <h3>{doc.nombre} {doc.obligatorio && <span className="badge-obligatorio">*</span>}</h3>
                        <p className="documento-descripcion">{doc.descripcion}</p>
                      </div>
                      {doc.archivo && (
                        <span className="documento-status">
                          <CheckCircle size={16} /> Cargado
                        </span>
                      )}
                    </div>

                    <div className="documento-content">
                      {doc.archivo ? (
                        <div className="archivo-cargado">
                          <div className="archivo-preview">
                            <FileText size={32} />
                          </div>
                          <div className="archivo-detalles">
                            <span className="archivo-nombre">{doc.archivo.name}</span>
                            <span className="archivo-meta">
                              {getFileExtension(doc.archivo.name)} · {formatFileSize(doc.archivo.size)}
                            </span>
                          </div>
                          <button
                            className="btn-eliminar"
                            onClick={() => removeFile(doc.id)}
                            aria-label={`Eliminar ${doc.nombre}`}
                          >
                            <X size={16} />
                          </button>
                        </div>
                      ) : (
                        <div className="archivo-vacio">
                          <input
                            type="file"
                            accept=".pdf,.jpg,.jpeg,.png"
                            onChange={(e) => e.target.files?.[0] && handleFileChange(doc.id, e.target.files[0])}
                            className="file-input"
                            id={`file-${doc.id}`}
                          />
                          <label htmlFor={`file-${doc.id}`} className="file-label">
                            <Upload size={32} />
                            <span>Haga clic o arrastre el archivo</span>
                            <small>PDF, JPG, PNG · Máx. 10MB</small>
                          </label>
                        </div>
                      )}
                    </div>

                    {doc.obligatorio && !doc.archivo && (
                      <div className="documento-alerta">
                        <AlertCircle size={14} /> Documento obligatorio
                      </div>
                    )}
                  </article>
                ))}
              </div>
            </div>
          </div>

          <div className="formato-actions">
            <button className="btn-primary" onClick={handleSubmit} disabled={!allRequiredComplete || isSubmitting} style={{ width: '100%', maxWidth: 'none' }}>
              {isSubmitting ? 'Generando ZIP...' : 'Generar ZIP de documentos'}
            </button>
          </div>
        </div>
      </main>
      <Footer />
    </div>
  );
};

export default FormCAR;