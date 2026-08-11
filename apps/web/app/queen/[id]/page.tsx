import Link from "next/link";
import { notFound } from "next/navigation";

import { getQueen, type QueenId } from "@/lib/queen";

const VALID: QueenId[] = ["bardera", "toxica", "gede", "rocha", "chela"];

export function generateStaticParams() {
  return VALID.map((id) => ({ id }));
}

export default function QueenProfilePage({ params }: { params: { id: string } }) {
  const queen = getQueen(params.id);
  if (!queen) notFound();

  const ready = queen.profile.status === "ready";
  const readyCount = queen.profile.slides.filter((s) => s.state === "ready").length;
  const slotCount = queen.profile.slides.filter((s) => s.state === "slot").length;

  return (
    <div className="site-shell profile-shell">
      <header className="profile-top">
        <Link href="/#queens" className="profile-back">
          ← ROSTER
        </Link>
        <span className="eyebrow cyan">
          {ready ? "IDENTITY DECK" : "PROFILE SLOT · RESERVADO"}
        </span>
      </header>

      <main className="profile-main">
        <section className="profile-hero">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src={queen.portrait}
            alt={queen.name}
            width={900}
            height={1200}
            className="profile-portrait"
          />
          <div className="profile-hero-copy">
            <span className="eyebrow">{queen.status === "live" ? "BETA ACTIVA" : "EN CURACIÓN"}</span>
            <h1>{queen.name}</h1>
            <p className="profile-tagline">{queen.tagline}</p>
            <p className="profile-sub">{queen.profile.subtitle}</p>
            <div className="profile-actions">
              {queen.chatEnabled ? (
                <Link className="button-primary" href="/#chat">
                  HABLÁ CON ELLA →
                </Link>
              ) : (
                <span className="button-ghost profile-disabled">CHAT PRONTO</span>
              )}
              <Link className="button-ghost" href="/#queens">
                VER ROSTER
              </Link>
            </div>
            <p className="queen-card-note">
              {readyCount} slides listos · {slotCount} slots vacíos · memoria no compartida con
              otras Queens · deck ≠ system prompt
            </p>
          </div>
        </section>

        <section className="profile-deck" aria-label={`Deck de ${queen.name}`}>
          <div className="section-heading compact">
            <span className="eyebrow cyan">{queen.profile.label}</span>
            <h2>
              {ready ? "MANUAL DE IDENTIDAD." : "SLOT LISTO."}
              <br />
              <span>{ready ? "ONCE CAPAS." : "ESPERANDO NOTEBOOKLM / FLOW."}</span>
            </h2>
          </div>

          <div className="deck-grid">
            {queen.profile.slides.map((slide) => (
              <article
                key={`${queen.id}-${slide.n}`}
                className={slide.state === "ready" ? "deck-card ready" : "deck-card slot"}
              >
                <div className="deck-card-top">
                  <strong>{String(slide.n).padStart(2, "0")}</strong>
                  <span>{slide.state === "ready" ? "READY" : "SLOT"}</span>
                </div>
                <h3>{slide.title}</h3>
                {slide.body ? (
                  <p>{slide.body}</p>
                ) : (
                  <p className="deck-empty">
                    Reservado. Exportá el deck desde NotebookLM / Flow y lo enchufamos acá sin
                    tocar el chat ni la memoria de otra Queen.
                  </p>
                )}
              </article>
            ))}
          </div>
        </section>
      </main>
    </div>
  );
}
