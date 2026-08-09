"use client";

import { useEffect, useRef, useState } from "react";

import {
  clearConversation,
  getConversation,
  sendChat,
  type ChatMessage,
  type ConversationSummary,
  type OutputValidation,
} from "@/lib/api";
import { bardera } from "@/lib/queen";

interface RuntimeStatus {
  provider: string;
  model: string;
  configured: boolean;
  mode: string;
}

export function ChatPanel() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    { role: "assistant", content: bardera.greeting },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [validation, setValidation] = useState<OutputValidation | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [runtime, setRuntime] = useState<RuntimeStatus | null>(null);
  const [serverTurnCount, setServerTurnCount] = useState<number | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const api = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
    fetch(`${api}/v1/runtime/status`)
      .then((response) => (response.ok ? response.json() : null))
      .then((data) => data && setRuntime(data))
      .catch(() => undefined);
  }, []);

  useEffect(() => {
    let cancelled = false;
    getConversation({ character_id: bardera.id })
      .then((summary: ConversationSummary) => !cancelled && setServerTurnCount(summary.messages.length))
      .catch(() => undefined);
    return () => { cancelled = true; };
  }, [messages]);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, loading]);

  const send = async (text?: string) => {
    const content = (text ?? input).trim();
    if (!content || loading) return;
    setInput("");
    setError(null);
    setMessages((current) => [...current, { role: "user", content }]);
    setLoading(true);
    try {
      const data = await sendChat(content, { character_id: bardera.id });
      setMessages((current) => [...current, { role: "assistant", content: data.response.content }]);
      setValidation(data.response.validation);
      setRuntime((current) => current
        ? { ...current, provider: data.response.provider, model: data.response.model }
        : { provider: data.response.provider, model: data.response.model, configured: true, mode: "active" });
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "No se pudo conectar con el chat.");
      setMessages((current) => [...current, { role: "assistant", content: "Se cortó la señal. Probemos otra vez en un momento." }]);
    } finally {
      setLoading(false);
    }
  };

  const clear = async () => {
    if (loading) return;
    setError(null);
    try {
      await clearConversation({ character_id: bardera.id });
      setMessages([{ role: "assistant", content: bardera.greeting }]);
      setValidation(null);
      setServerTurnCount(0);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "No se pudo limpiar la conversación.");
    }
  };

  return (
    <section className="chat-section" id="chat">
      <div className="chat-heading">
        <span className="eyebrow cyan">T1 / BETA</span>
        <h2>LA BARDERA<br /><span>ESTÁ EN LÍNEA.</span></h2>
        <p>Entrá directo. La configuración fina puede esperar.</p>
      </div>
      <div className="chat-layout">
        <aside className="chat-presence">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src={bardera.portrait} alt="La Bardera" />
          <div className="presence-label"><i /><b>BETA ONLINE</b><span>Biblioteca visual curada</span></div>
          <p>{bardera.tagline}</p>
        </aside>
        <div className="chat-window">
          <header><div><b>{bardera.name}</b><span>{runtime ? "SEÑAL ACTIVA" : "CONECTANDO"}</span></div><button onClick={clear} disabled={loading}>REINICIAR</button></header>
          <div className="chat-messages" ref={scrollRef} aria-live="polite">
            {messages.map((message, index) => <div className={`bubble ${message.role}`} key={`${message.role}-${index}`}>{message.content}</div>)}
            {loading && <div className="typing" aria-label="Escribiendo"><span /><span /><span /></div>}
          </div>
          {messages.length <= 2 && !loading && <div className="quick-prompts">{bardera.quickPrompts.map((prompt) => <button key={prompt} onClick={() => send(prompt)}>{prompt}</button>)}</div>}
          <div className="composer">
            <input
              aria-label="Mensaje"
              value={input}
              onChange={(event) => setInput(event.target.value)}
              onKeyDown={(event) => event.key === "Enter" && send()}
              placeholder="Escribile algo..."
              disabled={loading}
            />
            <button onClick={() => send()} disabled={loading || !input.trim()}>ENVIAR →</button>
          </div>
          {error && <p className="chat-error">{error}</p>}
          {process.env.NODE_ENV !== "production" && <details className="chat-diagnostic"><summary>Diagnóstico</summary><p>turnos server: {serverTurnCount ?? "..."} · validación: {validation ? (validation.is_valid ? "OK" : "rechazada") : "..."}</p></details>}
        </div>
      </div>
    </section>
  );
}
