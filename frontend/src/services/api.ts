import axios from 'axios';

// En producción conviene definir VITE_API_BASE_URL (dashboard de Vercel);
// el fallback '/api' sirve si el backend vive en el mismo dominio.
const API_BASE_URL =
  (import.meta as any).env.VITE_API_BASE_URL ||
  ((import.meta as any).env.PROD ? '/api' : 'http://localhost:8000/api');

const TOKEN_KEY = 'ecoregion_token';

// Instancia compartida: inyecta el JWT en cada petición autenticada.
export const http = axios.create({ baseURL: API_BASE_URL });

http.interceptors.request.use((config) => {
  const token = localStorage.getItem(TOKEN_KEY);
  if (token) {
    config.headers = config.headers ?? {};
    (config.headers as Record<string, string>).Authorization = `Bearer ${token}`;
  }
  return config;
});

export interface ValidacionIA {
  apto: boolean | null;
  puntaje: number | null;
  faltantes: Array<{ campo: string; detalle: string }>;
  observaciones: string[];
  resumen: string;
  modelo?: string;
  generado_en?: string;
}

export interface BackendUser {
  id: number;
  email: string;
  nombre: string;
  rol: string;
  activo: boolean;
  creado_en: string;
}

export const api = {
  normalizar: async (formData: any) => {
    const response = await http.post(`/formulario/normalizar`, formData);
    return response.data;
  },
  generarDocumento: async (formData: any) => {
    const response = await http.post(`/formulario/generar-documento`, formData, {
      responseType: 'blob'
    });
    return response.data;
  },
  getDraft: async (draftId: string) => {
    const response = await http.get(`/formulario/drafts/${draftId}`);
    return response.data;
  },
  putDraft: async (draftId: string, version: number, data: unknown) => {
    const response = await http.put(`/formulario/drafts/${draftId}`, { version, data });
    return response.data;
  },
  agente: async (pregunta: string, historial: Array<{ role: 'user' | 'assistant'; content: string }>) => {
    const response = await http.post(`/ia/agente`, { pregunta, historial });
    return response.data as { reply: string; fallback: boolean; model?: string };
  },
  exportarFunPdf: async (formData: any) => {
    const response = await http.post(`/formulario/fun/exportar-pdf`, formData, {
      responseType: 'blob',
    });
    return response.data;
  },
  register: async (payload: { email: string; nombre: string; password: string }) => {
    const response = await http.post(`/auth/register`, payload);
    return response.data as BackendUser;
  },
  login: async (email: string, password: string) => {
    const body = new URLSearchParams({ username: email, password });
    const response = await http.post(`/auth/login`, body, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
    return response.data as { access_token: string; token_type: string };
  },
  me: async () => {
    const response = await http.get(`/auth/me`);
    return response.data as BackendUser;
  },
  listUsers: async () => {
    const response = await http.get(`/auth/usuarios`);
    return response.data as BackendUser[];
  },
  updateUser: async (id: number, payload: { rol?: string; activo?: boolean }) => {
    const response = await http.patch(`/auth/usuarios/${id}`, payload);
    return response.data as BackendUser;
  },
  deleteUser: async (id: number) => {
    await http.delete(`/auth/usuarios/${id}`);
  },
  listTramites: async () => {
    const response = await http.get(`/tramites`);
    return response.data as Array<{
      id: number;
      cliente_id: number | null;
      tipo_tramite: string | null;
      estado: string | null;
      datos_formulario: { titular?: { nombre?: string; nit?: string } } | null;
      autoridad_sigla: string | null;
      creado_en: string | null;
      actualizado_en: string | null;
    }>;
  },
  updateTramiteEstado: async (id: number, estado: string) => {
    const response = await http.patch(`/tramites/${id}/estado`, { estado });
    return response.data;
  },
  listMisSolicitudes: async () => {
    const response = await http.get(`/solicitudes/mias`);
    return response.data as Array<{
      id: number;
      usuario_id: number;
      usuario_email: string;
      usuario_nombre: string;
      tipo: string;
      nombre_archivo: string;
      tamano_bytes: number;
      creado_en: string;
      resumen?: { validacion_ia?: ValidacionIA } & Record<string, unknown>;
    }>;
  },
  getValidacionSolicitud: async (id: number) => {
    const response = await http.get(`/solicitudes/${id}/validacion`);
    return response.data as { estado_validacion: 'pendiente' | 'lista'; validacion?: ValidacionIA };
  },
  listSolicitudes: async (usuarioId?: number) => {
    const response = await http.get(`/solicitudes`, {
      params: usuarioId ? { usuario_id: usuarioId } : {},
    });
    return response.data as Array<{
      id: number;
      usuario_id: number;
      usuario_email: string;
      usuario_nombre: string;
      tipo: string;
      estado: string;
      nombre_archivo: string;
      tamano_bytes: number;
      creado_en: string;
      resumen?: Record<string, string>;
    }>;
  },
  updateSolicitudEstado: async (id: number, estado: string) => {
    const response = await http.patch(`/solicitudes/${id}/estado`, null, {
      params: { estado },
    });
    return response.data as { id: number; estado: string };
  },
  downloadSolicitud: async (id: number) => {
    const response = await http.get(`/solicitudes/${id}/descargar`, { responseType: 'blob' });
    return response.data;
  },
  downloadSolicitudesZip: async (ids: number[]) => {
    const response = await http.get(`/solicitudes/descargar-zip`, {
      params: { ids: ids.join(',') },
      responseType: 'blob',
    });
    return response.data;
  },
  subirDocumento: async (tipo: string, archivo: Blob, nombreArchivo: string) => {
    const form = new FormData();
    form.append('tipo', tipo);
    form.append('archivo', archivo, nombreArchivo);
    const response = await http.post(`/solicitudes/subir`, form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },
  getReporteResumen: async () => {
    const response = await http.get(`/reportes/resumen`);
    return response.data as {
      totales: { solicitudes: number; usuarios: number; bytes: number };
      por_tipo: Record<string, number>;
      por_mes: Record<string, number>;
      top_usuarios: Array<{ usuario_id: number; nombre: string; email: string; total: number }>;
      actividad_reciente: Array<{ fecha: string; total: number }>;
      tipos_disponibles: Array<{ tipo: string; label: string }>;
      generado_en: string;
    };
  },
  getReporteDetalle: async (params?: {
    usuario_id?: number;
    tipo?: string;
    fecha_desde?: string;
    fecha_hasta?: string;
  }) => {
    const response = await http.get(`/reportes/detalle`, { params });
    return response.data as {
      total: number;
      registros: Array<{
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
      }>;
      generado_en: string;
    };
  },
};

export { TOKEN_KEY };
