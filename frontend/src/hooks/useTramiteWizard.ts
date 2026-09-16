import { useCallback, useMemo, useState, type ChangeEvent } from 'react';
import axios from 'axios';
import type { AuthorityCode } from '../components/formulario/AuthoritySelector';
import { useDraftSync } from './useDraftSync';
import { api } from '../services/api';
import type { FormData, NormalizedData } from '../types/formulario';

export function authErrorMessage(err: unknown, fallback: string): string {
  if (axios.isAxiosError(err) && err.response?.status === 401) {
    return 'Inicia sesión para descargar documentos. Tus datos se conservan.';
  }
  return fallback;
}

export const initialWizardData: FormData = {
  titular: { nombre: '', nit: '', representante_legal: '', direccion: '' },
  predio: { nombre: '', municipio: '', vereda: '', latitud: '', longitud: '' },
  aprovechamiento: { tipo: '', justificacion: '', volumen_total: 0, unidad: 'm3' },
  especies: [{ nombre: '', cantidad: 0, diametro_cm: null }],
};

export type FormSection = 'titular' | 'predio' | 'aprovechamiento';
export const supportedAuthorities: AuthorityCode[] = ['CAR', 'SDA', 'CORPOBOYACA'];

/** Lógica compartida del wizard de normalización (antes duplicada en App). */
export function useTramiteWizard() {
  const [formData, setFormData] = useState<FormData>(initialWizardData);
  const [normalizedData, setNormalizedData] = useState<NormalizedData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [authority, setAuthority] = useState<AuthorityCode>('CAR');
  const [authorityDetails, setAuthorityDetails] = useState<Record<string, string | boolean>>({});

  const updateSection = (
    event: ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>,
    section: FormSection,
  ) => {
    const { name, value } = event.target;
    const nextValue = section === 'aprovechamiento' && name === 'volumen_total' ? Number(value) : value;
    setFormData((current) => ({ ...current, [section]: { ...current[section], [name]: nextValue } }));
    setNormalizedData(null);
  };

  const updateSpecies = (index: number, event: ChangeEvent<HTMLInputElement>) => {
    const { name, value } = event.target;
    const nextValue = name === 'nombre' ? value : value === '' ? null : Number(value);
    setFormData((current) => ({
      ...current,
      especies: current.especies.map((item, itemIndex) =>
        itemIndex === index ? { ...item, [name]: nextValue } : item,
      ),
    }));
    setNormalizedData(null);
  };

  const updateAuthorityDetail = (
    event: ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>,
  ) => {
    const { name, value, type } = event.target;
    setAuthorityDetails((current) => ({
      ...current,
      [name]: type === 'checkbox' ? (event.target as HTMLInputElement).checked : value,
    }));
    setNormalizedData(null);
  };

  const normalize = async (confirmar_revision = false) => {
    setLoading(true);
    setError('');
    try {
      setNormalizedData(
        await api.normalizar({
          ...formData,
          autoridad_seleccionada: authority,
          detalles_autoridad: authorityDetails,
          confirmar_revision,
        }),
      );
    } catch (err: unknown) {
      const detail =
        err instanceof Error
          ? err.message
          : 'No pudimos analizar estos datos. Intenta de nuevo.';
      setError(detail);
    } finally {
      setLoading(false);
    }
  };

  const downloadDocument = async () => {
    setLoading(true);
    setError('');
    try {
      const blob = await api.generarDocumento({
        ...formData,
        autoridad_seleccionada: authority,
        detalles_autoridad: authorityDetails,
        confirmar_revision: true,
      });
      const url = window.URL.createObjectURL(blob);
      const anchor = document.createElement('a');
      anchor.href = url;
      anchor.download = 'aprovechamiento_forestal.docx';
      anchor.click();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      setError(authErrorMessage(err, 'No pudimos generar el documento.'));
    } finally {
      setLoading(false);
    }
  };

  const addSpecies = () =>
    setFormData((current) => ({
      ...current,
      especies: [...current.especies, { nombre: '', cantidad: 0, diametro_cm: null }],
    }));
  const removeSpecies = (index: number) =>
    setFormData((current) => ({
      ...current,
      especies: current.especies.filter((_, itemIndex) => itemIndex !== index),
    }));

  const changeAuthority = (next: AuthorityCode) => {
    setAuthority(next);
    setAuthorityDetails({});
    setNormalizedData(null);
  };

  const draftValue = useMemo(
    () => ({ formData, authority, authorityDetails }),
    [formData, authority, authorityDetails],
  );
  const applyRemoteDraft = useCallback((draft: typeof draftValue) => {
    if (!draft?.formData) return;
    setFormData(draft.formData);
    if (supportedAuthorities.includes(draft.authority)) setAuthority(draft.authority);
    setAuthorityDetails(draft.authorityDetails || {});
  }, []);
  const draftSync = useDraftSync(draftValue, applyRemoteDraft);

  return {
    formData,
    normalizedData,
    loading,
    error,
    authority,
    authorityDetails,
    draftSync,
    updateSection,
    updateSpecies,
    updateAuthorityDetail,
    normalize,
    downloadDocument,
    addSpecies,
    removeSpecies,
    changeAuthority,
  };
}
