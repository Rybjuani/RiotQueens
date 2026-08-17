"use client";

import { useCallback, useEffect, useRef, useState } from "react";

import {
  clearConversation,
  getConversation,
  sendChat,
  type ChatMessage,
  type ConversationSummary,
} from "@/lib/api";
import { bardera } from "@/components/riotqueens/queen";

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
      const summary: ConversationSummary = await getConversation({
        character_id: bardera.id,
        signal,
      });
      if (signal?.aborted) return;
      setMessages(summary.messages.map(({ role, content }) => ({ role, content })));
      setConversationReady(true);
    } catch {
      if (!signal?.aborted) {
        setConversationReady(false);
        setError("No se pudo abrir el chat. Reintentá en un momento.");
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
    if (!content || loading || hydrating || !conversationReady || requestInFlightRef.current) {
      return;
    }
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
        setMessages(
          summary.messages.map(({ role, content: storedContent }) => ({
            role,
            content: storedContent,
          })),
        );
      } catch {
        setConversationReady(false);
        setError("La respuesta llegó, pero no se pudo confirmar el hilo. Reintentá.");
      }
    } catch {
      try {
        const summary = await getConversation({ character_id: bardera.id });
        setMessages(summary.messages.map(({ role, content: storedContent }) => ({ role, content: storedContent })));
        setConversationReady(true);
        setError("No se pudo confirmar el envío. El hilo se sincronizó.");
      } catch {
        setMessages(previousMessages);
        setConversationReady(false);
        setError("No se pudo enviar. Reintentá en un momento.");
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
        setError("No se pudo reiniciar. El hilo se sincronizó.");
      } catch {
        setMessages(previousMessages);
        setConversationReady(false);
        setError("No se pudo reiniciar. Reintentá en un momento.");
      }
    } finally {
      requestInFlightRef.current = false;
    }
  };

  return (
    <section className="chat-section" id="chat">
      <div className="wrap">
        <span className="label">CHAT · LA BARDERA · T1</span>
        <h2>
          HABLÁ CON
          <br />
          LA BARDERA
        </h2>
        <p className="chat-sub">
          Te bardea, te quiere, se queda. 100% virtual, +18. Hilo por pestaña,
          sin cuenta requerida en el preview.
        </p>

        <div className="chat-layout">
          <aside className="chat-presence">
            <div className="photo-wrap">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src={bardera.portrait}
                alt="La Bardera"
                width={1600}
                height={893}
                loading="lazy"
                decoding="async"
              />
              <span className="live-pill">
                <i className="dot" aria-hidden />
                ONLINE
              </span>
            </div>
            <div className="meta">
              <span className="label">{bardera.tagline}</span>
              <p>
                Punk del oeste, 24 años. Timing, sinceridad, ingenio, bardeo
                afectivo y aguante. No inventa recuerdos. Ante dolor real,
                acompaña antes de bardear.
              </p>
            </div>
          </aside>

          <div className="chat-window">
            <header>
              <div>
                <b>{bardera.name}</b>
                <span className={hydrating ? "" : conversationReady ? "live" : "dead"}>
                  {hydrating ? "ABRIENDO" : conversationReady ? "● LISTA" : "SIN SEÑAL"}
                </span>
              </div>
              <button
                type="button"
                className="btn mono"
                onClick={clear}
                disabled={loading || hydrating || !conversationReady}
              >
                REINICIAR
              </button>
            </header>

            <div
              className="chat-messages"
              ref={scrollRef}
              aria-live="polite"
              aria-busy={hydrating || loading}
            >
              {hydrating && <p className="chat-empty">Abriendo el chat…</p>}
              {!hydrating && conversationReady && messages.length === 0 && (
                <p className="chat-empty">Escribile algo. Ella arranca cuando vos mandás.</p>
              )}
              {messages.map((message, index) => (
                <div className={`bubble ${message.role}`} key={`${message.role}-${index}`}>
                  {message.content}
                </div>
              ))}
              {loading && (
                <div className="typing" aria-label="Escribiendo">
                  <span />
                  <span />
                  <span />
                </div>
              )}
            </div>

            {messages.length === 0 && !loading && !hydrating && conversationReady && (
              <div className="quick-prompts">
                {bardera.quickPrompts.map((prompt) => (
                  <button type="button" key={prompt} onClick={() => void send(prompt)}>
                    {prompt}
                  </button>
                ))}
              </div>
            )}

            <div className="composer">
              <input
                aria-label="Mensaje"
                value={input}
                onChange={(event) => setInput(event.target.value)}
                onKeyDown={(event) => {
                  if (event.key === "Enter" && !event.shiftKey) {
                    event.preventDefault();
                    void send();
                  }
                }}
                placeholder="Escribile algo..."
                maxLength={CHAT_MESSAGE_MAX_LENGTH}
                disabled={loading || hydrating || !conversationReady}
              />
              <button
                type="button"
                className="btn solid"
                onClick={() => void send()}
                disabled={loading || hydrating || !conversationReady || !input.trim()}
              >
                ENVIAR →
              </button>
            </div>

            {error && (
              <p className="chat-error" role="status">
                {error}
              </p>
            )}
            {!hydrating && !conversationReady && (
              <button
                type="button"
                className="chat-retry"
                onClick={() => void hydrateConversation()}
              >
                REINTENTAR
              </button>
            )}
          </div>
        </div>
      </div>
    </section>
  );
}
