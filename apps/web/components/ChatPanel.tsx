"use client";

import { useCallback, useEffect, useRef, useState } from "react";

import {
  clearConversation,
  getConversation,
  sendChat,
  type ChatMessage,
  type ConversationSummary,
} from "@/lib/api";
import { bardera } from "@/lib/queen";

const CHAT_MESSAGE_MAX_LENGTH = 4_000;

export function ChatPanel() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [hydrating, setHydrating] = useState(true);
  const [conversationReady, setConversationReady] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);
  const requestInFlightRef = useRef(false);

  const hydrateConversation = useCallback(async (signal?: AbortSignal) => {
    setHydrating(true);
    setError(null);
    try {
      const summary: ConversationSummary = await getConversation({ character_id: bardera.id, signal });
      if (signal?.aborted) return;
      setMessages(summary.messages.map(({ role, content }) => ({ role, content })));
      setConversationReady(true);
    } catch {
      if (!signal?.aborted) {
        setConversationReady(false);
        setError("No se pudo recuperar esta sesión. Reintentá antes de seguir.");
      }
    } finally {
      if (!signal?.aborted) setHydrating(false);
    }
  }, []);

  useEffect(() => {
    const controller = new AbortController();
    void hydrateConversation(controller.signal);
    return () => controller.abort();
  }, [hydrateConversation]);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, loading]);

  const send = async (text?: string) => {
    const content = (text ?? input).trim();
    if (!content || loading || hydrating || !conversationReady || requestInFlightRef.current) return;
    if (content.length > CHAT_MESSAGE_MAX_LENGTH) {
      setError(`El mensaje puede tener hasta ${CHAT_MESSAGE_MAX_LENGTH} caracteres.`);
      return;
    }
    requestInFlightRef.current = true;
    const previousMessages = messages;
    const optimisticMessages: ChatMessage[] = [...previousMessages, { role: "user", content }];
    setInput("");
    setError(null);
    setMessages(optimisticMessages);
    setLoading(true);
    try {
      const data = await sendChat(content, { character_id: bardera.id });
      const completedMessages: ChatMessage[] = [
        ...optimisticMessages,
        { role: "assistant", content: data.response.content },
      ];
      setMessages(completedMessages);
      try {
        const summary = await getConversation({ character_id: bardera.id });
        setMessages(summary.messages.map(({ role, content: storedContent }) => ({ role, content: storedContent })));
      } catch {
        setConversationReady(false);
        setError("La respuesta llegó, pero no se pudo confirmar el hilo completo. Reintentá la sesión antes de seguir.");
      }
    } catch {
      try {
        const summary = await getConversation({ character_id: bardera.id });
        setMessages(summary.messages.map(({ role, content: storedContent }) => ({ role, content: storedContent })));
        setConversationReady(true);
        setError("No se pudo confirmar el envío. El hilo visible se sincronizó con el servidor.");
      } catch {
        setMessages(previousMessages);
        setConversationReady(false);
        setError("No se pudo confirmar el envío ni recuperar el hilo. Reintentá la sesión antes de seguir.");
      }
    } finally {
      requestInFlightRef.current = false;
      setLoading(false);
    }
  };

  const clear = async () => {
    if (loading || hydrating || !conversationReady || requestInFlightRef.current) return;
    requestInFlightRef.current = true;
    const previousMessages = messages;
    setError(null);
    try {
      await clearConversation({ character_id: bardera.id });
      setMessages([]);
    } catch {
      try {
        const summary = await getConversation({ character_id: bardera.id });
        setMessages(summary.messages.map(({ role, content }) => ({ role, content })));
        setConversationReady(true);
        setError("No se pudo confirmar el reinicio. El hilo visible se sincronizó con el servidor.");
      } catch {
        setMessages(previousMessages);
        setConversationReady(false);
        setError("No se pudo confirmar el reinicio ni recuperar el hilo. Reintentá la sesión antes de seguir.");
      }
    } finally {
      requestInFlightRef.current = false;
    }
  };

  return (
    <section className="chat-section" id="chat">
      <div className="chat-heading">
        <span className="eyebrow cyan">BETA ABIERTA</span>
        <h2>HABLÁ CON<br /><span>LA BARDERA.</span></h2>
        <p>Entrá directo. La configuración fina puede esperar.</p>
      </div>
      <div className="chat-layout">
        <aside className="chat-presence">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src={bardera.portrait} alt="La Bardera" width={1600} height={893} loading="lazy" decoding="async" />
          <div className="presence-label"><i /><b>BETA ABIERTA</b><span>PREVIEW PÚBLICO</span></div>
          <p>{bardera.tagline}</p>
        </aside>
        <div className="chat-window">
          <header><div><b>{bardera.name}</b><span>{hydrating ? "RECUPERANDO" : conversationReady ? "SEÑAL LISTA" : "SIN CONEXIÓN"}</span></div><button onClick={clear} disabled={loading || hydrating || !conversationReady}>REINICIAR</button></header>
          <div className="chat-messages" ref={scrollRef} aria-live="polite" aria-busy={hydrating || loading}>
            {hydrating && <p className="chat-empty">SISTEMA · Recuperando esta sesión…</p>}
            {!hydrating && conversationReady && messages.length === 0 && <p className="chat-empty">SISTEMA · La conversación empieza cuando enviás el primer mensaje.</p>}
            {messages.map((message, index) => <div className={`bubble ${message.role}`} key={`${message.role}-${index}`}>{message.content}</div>)}
            {loading && <div className="typing" aria-label="Escribiendo"><span /><span /><span /></div>}
          </div>
          {messages.length === 0 && !loading && !hydrating && conversationReady && <div className="quick-prompts">{bardera.quickPrompts.map((prompt) => <button key={prompt} onClick={() => send(prompt)}>{prompt}</button>)}</div>}
          <div className="composer">
            <input
              aria-label="Mensaje"
              value={input}
              onChange={(event) => setInput(event.target.value)}
              onKeyDown={(event) => event.key === "Enter" && send()}
              placeholder="Escribile algo..."
              maxLength={CHAT_MESSAGE_MAX_LENGTH}
              disabled={loading || hydrating || !conversationReady}
            />
            <button onClick={() => send()} disabled={loading || hydrating || !conversationReady || !input.trim()}>ENVIAR →</button>
          </div>
          {error && <p className="chat-error" role="status">SISTEMA · {error}</p>}
          {!hydrating && !conversationReady && <button className="chat-retry" onClick={() => void hydrateConversation()}>REINTENTAR SESIÓN</button>}
        </div>
      </div>
    </section>
  );
}
