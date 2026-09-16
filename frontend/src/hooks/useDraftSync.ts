import { useCallback, useEffect, useRef, useState } from 'react';
import axios from 'axios';
import { api } from '../services/api';

interface DraftEnvelope<T> {
  version: number;
  data: T;
}

interface DraftSyncState {
  version: number;
  status: 'loading' | 'saved' | 'saving' | 'offline';
  conflict: string | null;
}

function makeDraftId(namespace?: string) {
  const key = namespace ? `ecoregion:draft-id:${namespace}` : 'ecoregion:draft-id';
  const existing = localStorage.getItem(key);
  if (existing) return existing;
  const created = typeof crypto.randomUUID === 'function'
    ? crypto.randomUUID()
    : `draft-${Date.now()}-${Math.random().toString(36).slice(2)}`;
  localStorage.setItem(key, created);
  return created;
}

function scopedKey(prefix: string, namespace: string | undefined, id: string) {
  return namespace ? `${prefix}:${namespace}:${id}` : `${prefix}:${id}`;
}

export interface DraftSyncOptions {
  /** Aísla el borrador por formulario (wizard, fun…). Sin namespace = comportamiento actual. */
  namespace?: string;
  /** Clave vieja de localStorage para migrar una sola vez al borrador sincronizado. */
  legacyLocalKey?: string;
}

export function useDraftSync<T>(
  value: T,
  onRemoteValue: (value: T) => void,
  options?: DraftSyncOptions,
): DraftSyncState & { resolveConflict: () => void } {
  const namespace = options?.namespace;
  const legacyLocalKey = options?.legacyLocalKey;
  const [state, setState] = useState<DraftSyncState>({
    version: 0,
    status: 'loading',
    conflict: null,
  });
  const draftId = useRef(makeDraftId(namespace));
  const valueRef = useRef(value);
  const dirtyRef = useRef(false);
  const channelRef = useRef<BroadcastChannel | null>(null);
  const initialLoadRef = useRef(true);
  const suppressDirtyRef = useRef(false);

  useEffect(() => {
    valueRef.current = value;
    if (suppressDirtyRef.current) {
      suppressDirtyRef.current = false;
    } else if (!initialLoadRef.current) {
      dirtyRef.current = true;
    }
  }, [value]);

  useEffect(() => {
    let active = true;
    const localKey = scopedKey('ecoregion:draft', namespace, draftId.current);
    const adoptLocal = (raw: string | null) => {
      if (!raw) return false;
      try {
        const parsed = JSON.parse(raw) as DraftEnvelope<T>;
        setState({ version: parsed.version, status: 'offline', conflict: null });
        suppressDirtyRef.current = true;
        onRemoteValue(parsed.data);
        return true;
      } catch {
        return false;
      }
    };
    const load = async () => {
      try {
        const remote = await api.getDraft(draftId.current);
        if (!active) return;
        setState({ version: remote.version, status: 'saved', conflict: null });
        suppressDirtyRef.current = true;
        onRemoteValue(remote.data);
      } catch (error) {
        if (!active) return;
        if (!axios.isAxiosError(error) || error.response?.status !== 404) {
          setState((current) => ({ ...current, status: 'offline' }));
        } else if (adoptLocal(localStorage.getItem(localKey))) {
          // Borrador local del mismo namespace.
        } else if (legacyLocalKey && adoptLocal(localStorage.getItem(legacyLocalKey))) {
          // Migración única desde la clave vieja (ej. formularioFUN-draft).
          localStorage.removeItem(legacyLocalKey);
        } else {
          setState({ version: 0, status: 'offline', conflict: null });
        }
      } finally {
        initialLoadRef.current = false;
      }
    };
    void load();
    return () => { active = false; };
  }, [onRemoteValue, namespace, legacyLocalKey]);

  useEffect(() => {
    const localKey = scopedKey('ecoregion:draft', namespace, draftId.current);
    const timer = window.setTimeout(async () => {
      if (initialLoadRef.current || !dirtyRef.current) return;
      setState((current) => ({ ...current, status: 'saving' }));
      try {
        const saved = await api.putDraft(draftId.current, state.version, valueRef.current);
        localStorage.setItem(localKey, JSON.stringify({ version: saved.version, data: saved.data }));
        dirtyRef.current = false;
        setState({ version: saved.version, status: 'saved', conflict: null });
        channelRef.current?.postMessage(saved);
      } catch (error) {
        if (axios.isAxiosError(error) && error.response?.status === 409) {
          setState((current) => ({
            ...current,
            status: 'saved',
            conflict: 'Este borrador cambió en otra sesión. Tus datos locales se conservaron.',
          }));
        } else {
          localStorage.setItem(localKey, JSON.stringify({ version: state.version, data: valueRef.current }));
          setState((current) => ({ ...current, status: 'offline' }));
        }
      }
    }, 700);
    return () => window.clearTimeout(timer);
  }, [value, state.version]);

  useEffect(() => {
    if (typeof BroadcastChannel !== 'undefined') {
      const channel = new BroadcastChannel(scopedKey('ecoregion:draft', namespace, draftId.current));
      channelRef.current = channel;
      channel.onmessage = (event: MessageEvent<DraftEnvelope<T>>) => {
        if (event.data.version > state.version) {
          if (dirtyRef.current) {
            setState((current) => ({ ...current, conflict: 'Hay cambios remotos sin aplicar; tus datos locales se conservaron.' }));
          } else {
            setState({ version: event.data.version, status: 'saved', conflict: null });
            suppressDirtyRef.current = true;
            onRemoteValue(event.data.data);
          }
        }
      };
      return () => channel.close();
    }
    return undefined;
  }, [onRemoteValue, state.version]);

  useEffect(() => {
    const interval = window.setInterval(async () => {
      try {
        const remote = await api.getDraft(draftId.current);
        if (remote.version <= state.version) return;
        if (dirtyRef.current) {
          setState((current) => ({ ...current, conflict: 'Hay cambios remotos sin aplicar; tus datos locales se conservaron.' }));
        } else {
          setState({ version: remote.version, status: 'saved', conflict: null });
          suppressDirtyRef.current = true;
          onRemoteValue(remote.data);
        }
      } catch {
        // Local storage remains the offline fallback.
      }
    }, 5000);
    return () => window.clearInterval(interval);
  }, [onRemoteValue, state.version]);

  const resolveConflict = useCallback(() => {
    setState((current) => ({ ...current, conflict: null }));
  }, []);

  return { ...state, resolveConflict };
}
