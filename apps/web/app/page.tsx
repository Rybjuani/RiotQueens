"use client";

import { useEffect, useState } from "react";

import { ChatPanel } from "@/components/ChatPanel";
import { Experience } from "@/components/Experience";
import { Footer } from "@/components/Footer";
import { Hero } from "@/components/Hero";
import { Navbar } from "@/components/Navbar";
import { TierGrid } from "@/components/TierGrid";

type ModalKind = "how" | "locked" | null;

function InfoModal({ kind, onClose, onStart }: { kind: ModalKind; onClose: () => void; onStart: () => void }) {
  useEffect(() => {
    if (!kind) return;
    const onKeyDown = (event: KeyboardEvent) => event.key === "Escape" && onClose();
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [kind, onClose]);

  if (!kind) return null;

  const locked = kind === "locked";
  return (
    <div className="modal-backdrop" role="presentation" onMouseDown={onClose}>
      <section
        className="modal-card"
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-title"
        onMouseDown={(event) => event.stopPropagation()}
      >
        <span className="eyebrow">{locked ? "EN CURACIÓN" : "CÓMO FUNCIONA"}</span>
        <h2 id="modal-title">{locked ? "Todavía no sale al escenario." : "Entrás. Hablás. Ella continúa."}</h2>
        <p>
          {locked
            ? "T2 y T3 se abren cuando la experiencia, la biblioteca y la economía estén listas. Sin promesas de utilería."
            : "La beta conecta el landing con el chat real del backend. La conversación se conserva durante la sesión del servidor; la memoria durable todavía está en construcción."}
        </p>
        <div className="modal-actions">
          <button className="button-primary" onClick={onStart}>PROBAR T1</button>
          <button className="button-ghost" onClick={onClose}>CERRAR</button>
        </div>
      </section>
    </div>
  );
}

export default function Home() {
  const [chatOpen, setChatOpen] = useState(false);
  const [modal, setModal] = useState<ModalKind>(null);

  const startChat = () => {
    setModal(null);
    setChatOpen(true);
    window.setTimeout(() => document.getElementById("chat")?.scrollIntoView({ behavior: "smooth" }), 60);
  };

  return (
    <div className="site-shell">
      <Navbar onCta={startChat} />
      <main>
        <Hero onStart={startChat} onHow={() => setModal("how")} />
        <div className="signal-strip" aria-label="Principios de RiotQueens">
          <div>✦ HABLA ✦ RECUERDA ✦ REACCIONA ✦ APARECE ✦ PRODUCE ✦ ENTREGA ✦</div>
        </div>
        <Experience onStart={startChat} />
        <TierGrid onStart={startChat} onLocked={() => setModal("locked")} />
        {chatOpen && <ChatPanel />}
        <section className="final-cta" id="join">
          <span className="eyebrow">BETA / T1</span>
          <h2>NO ES UNA GALERÍA.<br /><span>HABLÁ CON ELLA.</span></h2>
          <button className="button-primary" onClick={startChat}>ENTRAR AL CHAT →</button>
        </section>
      </main>
      <Footer />
      <InfoModal kind={modal} onClose={() => setModal(null)} onStart={startChat} />
    </div>
  );
}
