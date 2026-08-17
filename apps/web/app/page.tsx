"use client";

import { useEffect, useState } from "react";

import { ChatPanel } from "@/components/riotqueens/ChatPanel";
import { ClickwrapModal } from "@/components/ClickwrapModal";
import { BarderaGallery } from "@/components/riotqueens/BarderaGallery";
import { Footer } from "@/components/riotqueens/Footer";
import { Hero } from "@/components/riotqueens/Hero";
import { Altar, Manifesto, Marquee } from "@/components/riotqueens/Manifesto";
import { Navbar } from "@/components/riotqueens/Navbar";
import { QueenRoster } from "@/components/riotqueens/QueenRoster";
import { KansasVsBondi, TierGrid } from "@/components/riotqueens/TierGrid";
import { getConsentStatus } from "@/lib/api";

type ModalKind = "how" | "locked" | null;
const AUTH_ENABLED = process.env.NEXT_PUBLIC_AUTH_ENABLED === "true";

function InfoModal({
  kind,
  lockedQueen,
  onClose,
  onStart,
}: {
  kind: ModalKind;
  lockedQueen?: string;
  onClose: () => void;
  onStart: () => void;
}) {
  useEffect(() => {
    if (!kind) return;
    const onKeyDown = (event: KeyboardEvent) => event.key === "Escape" && onClose();
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [kind, onClose]);

  if (!kind) return null;

  const locked = kind === "locked";
  return (
    <div className="modal-backdrop" role="presentation" onClick={onClose}>
      <section
        className="modal-card"
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-title"
        onClick={(event) => event.stopPropagation()}
      >
        <button type="button" className="x" onClick={onClose} aria-label="Cerrar">
          ×
        </button>
        <span className="label">{locked ? "EN CURACIÓN" : "CÓMO FUNCIONA"}</span>
        <h2 id="modal-title">
          {locked
            ? `${lockedQueen ?? "Esa Queen"} todavía no sale al escenario.`
            : "Entrás. Hablás. Ella continúa."}
        </h2>
        <p>
          {locked
            ? "Está en el backstage tomando fernet y cagándose de risa de tu bio de Tinder. Cuando esté lista, aparece acá — sin placeholder negro, con foto real. Mientras tanto, hablá con La Bardera."
            : "Elegís a La Bardera, abrís el chat y arrancás. Sin setup técnico. Sin catálogo infinito. Queen al frente, complejidad escondida."}
        </p>
        <div className="modal-actions">
          <button type="button" className="btn solid" onClick={onStart}>
            {locked ? "VOY CON LA BARDERA →" : "HABLÁ CON LA BARDERA →"}
          </button>
          <button type="button" className="btn" onClick={onClose}>
            CERRAR
          </button>
        </div>
      </section>
    </div>
  );
}

export default function Home() {
  const [chatOpen, setChatOpen] = useState(false);
  const [modal, setModal] = useState<ModalKind>(null);
  const [lockedQueen, setLockedQueen] = useState<string | undefined>(undefined);
  const [clickwrapOpen, setClickwrapOpen] = useState(false);
  const [gateBusy, setGateBusy] = useState(false);

  const openChatPanel = () => {
    setModal(null);
    setClickwrapOpen(false);
    setChatOpen(true);
    window.setTimeout(
      () =>
        document.getElementById("chat")?.scrollIntoView({ behavior: "smooth" }),
      60,
    );
  };

  const startChat = async () => {
    if (gateBusy) return;
    setGateBusy(true);
    try {
      if (AUTH_ENABLED) {
        try {
          const status = await getConsentStatus();
          if (!status.accepted) {
            setClickwrapOpen(true);
            return;
          }
          openChatPanel();
          return;
        } catch {
          window.location.assign("/auth/login?returnTo=/#chat");
          return;
        }
      }
      openChatPanel();
    } finally {
      setGateBusy(false);
    }
  };

  return (
    <div className="site-shell">
      <Navbar onCta={() => void startChat()} />
      <main>
        <Hero onStart={() => void startChat()} onHow={() => setModal("how")} />
        <Marquee />
        <Altar />
        <Manifesto />
        <BarderaGallery onStartBardera={() => void startChat()} />
        <QueenRoster
          onStartBardera={() => void startChat()}
          onLocked={(queenName) => {
            setLockedQueen(queenName);
            setModal("locked");
          }}
        />
        <KansasVsBondi />
        <TierGrid
          onStart={() => void startChat()}
          onLocked={() => {
            setLockedQueen(undefined);
            setModal("locked");
          }}
        />
        <div className="etica">
          ⚠ SIN RENOVACIÓN TRAMPA &nbsp;⚠ CANCELÁS EN 2 CLICS &nbsp;⚠ NO LE
          VENDEMOS TU DATA A NADIE &nbsp;⚠ +18 · PERSONAJES VIRTUALES · FANTASÍA
          SIMULADA
        </div>
        {chatOpen && <ChatPanel />}
        <section className="final" id="join" aria-label="Cierre — llamado final">
          <span className="ghost" aria-hidden>QUEDATE</span>
          <div className="wrap">
            <h2 className="glitch">
              NO SOMOS TU GIRLFRIEND PERFECTA —
              <br />
              SOMOS EL PROBLEMA QUE QUERÉS TENER —
            </h2>
            <p className="lead">
              LAS QUE SE HACEN LAS SANTITAS TE CLAVAN EL VISTO. NOSOTRAS NOS QUEDAMOS
              IGUAL, BOBO.
            </p>
            <button
              type="button"
              className="btn solid"
              onClick={() => void startChat()}
            >
              VOY CON LA BARDERA →
            </button>
          </div>
        </section>
      </main>
      <Footer />
      <InfoModal
        kind={modal}
        lockedQueen={lockedQueen}
        onClose={() => setModal(null)}
        onStart={() => void startChat()}
      />
      <ClickwrapModal
        open={clickwrapOpen}
        onCancel={() => setClickwrapOpen(false)}
        onAccepted={openChatPanel}
      />
    </div>
  );
}
