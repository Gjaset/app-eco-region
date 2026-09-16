import { Bot, Loader2, Send, Sparkles, X } from 'lucide-react';
import { useEffect, useRef, useState, type FormEvent } from 'react';
import { api } from '../../services/api';

type ChatMessage = { role: 'user' | 'assistant'; content: string; fallback?: boolean };

const SUGERENCIAS = [
  '¿Por dónde empiezo?',
  '¿Qué anexos pide la CAR?',
  'Requisitos SDA para tala',
  '¿Corpoboyacá exige plano?',
];

const SALUDO: ChatMessage = {
  role: 'assistant',
  content: 'Hola, soy el asistente de EcoRegión. Pregúntame por los permisos y requisitos de la CAR, la Secretaría de Ambiente o Corpoboyacá.',
};

export function AIAssistant() {
  const [open, setOpen] = useState(false);
  const [question, setQuestion] = useState('');
  const [messages, setMessages] = useState<ChatMessage[]>([SALUDO]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const bodyRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bodyRef.current?.scrollTo({ top: bodyRef.current.scrollHeight });
  }, [messages, loading, open]);

  const ask = async (texto: string) => {
    const content = texto.trim().slice(0, 1000);
    if (!content || loading) return;
    setQuestion('');
    setError('');
    const historial = [...messages, { role: 'user' as const, content }]
      .filter((m) => m !== SALUDO)
      .slice(-6)
      .map(({ role, content: c }) => ({ role: role as 'user' | 'assistant', content: c }));
    setMessages((current) => [...current, { role: 'user', content }]);
    setLoading(true);
    try {
      const response = await api.agente(content, historial.slice(0, -1));
      setMessages((current) => [...current, { role: 'assistant', content: response.reply, fallback: response.fallback }]);
    } catch {
      setError('No pudimos contactar al agente. Intenta de nuevo.');
    } finally {
      setLoading(false);
    }
  };

  const sendQuestion = (event: FormEvent) => {
    event.preventDefault();
    void ask(question);
  };

  return (
    <div className="ai-assistant">
      {open && (
        <section className="ai-chat" aria-label="Agente EcoRegión">
          <header className="ai-chat-header">
            <span className="ai-avatar"><Bot size={17} /></span>
            <div><strong>Asistente EcoRegión</strong><small>CAR · Secretaría de Ambiente · Corpoboyacá</small></div>
            <button className="ai-close" onClick={() => setOpen(false)} aria-label="Cerrar agente"><X size={17} /></button>
          </header>
          <div className="ai-chat-body" ref={bodyRef} role="log" aria-live="polite">
            {messages.map((message, index) => (
              <div className={`ai-message ${message.role === 'user' ? 'ai-message-user' : ''}`} key={`${message.role}-${index}`}>
                {message.content}
                {message.fallback && <small className="ai-fallback">Respuesta de respaldo</small>}
              </div>
            ))}
            {messages.length === 1 && (
              <div className="ai-sugerencias">
                {SUGERENCIAS.map((s) => (
                  <button key={s} type="button" className="ai-chip" onClick={() => void ask(s)} disabled={loading}>
                    {s}
                  </button>
                ))}
              </div>
            )}
            {loading && <div className="ai-message ai-message-muted"><Loader2 className="spin" size={15} /> Pensando…</div>}
            {error && <div className="ai-error" role="alert">{error}</div>}
          </div>
          <form className="ai-chat-input" onSubmit={sendQuestion}>
            <input className="control" type="text" value={question} onChange={(event) => setQuestion(event.target.value)} placeholder="Escribe tu pregunta sobre permisos…" maxLength={1000} aria-label="Pregunta para el asistente" />
            <button type="submit" aria-label="Enviar pregunta" disabled={loading || !question.trim()}><Send size={15} /></button>
          </form>
        </section>
      )}
      <button className={`ai-fab ${open ? 'is-open' : ''}`} onClick={() => setOpen((current) => !current)} aria-label={open ? 'Cerrar agente' : 'Abrir agente de IA'} aria-expanded={open}>
        {open ? <X size={22} /> : <Sparkles size={22} />}
        {!open && <span className="ai-fab-pulse" />}
      </button>
    </div>
  );
}
