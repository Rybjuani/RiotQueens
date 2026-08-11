"use client";

import Link from "next/link";

import { queens, type Queen } from "@/lib/queen";

export function QueenRoster({
  onStartBardera,
  onLocked,
}: {
  onStartBardera: () => void;
  onLocked: () => void;
}) {
  return (
    <section className="roster" id="queens">
      <div className="section-heading">
        <span className="eyebrow cyan">ROSTER / PRESENCIA</span>
        <h2>
          CINCO VOCES.
          <br />
          <span>CERO MEMORIA COMPARTIDA.</span>
        </h2>
        <p>
          Cada Queen es un personaje aparte: chat, hilo y memoria no se mezclan.
          DETAILS abre el manual de identidad (deck NotebookLM/Flow). Solo Bardera
          tiene el primero listo; las otras cuatro ya tienen el slot reservado.
        </p>
      </div>

      <div className="roster-list">
        {queens.map((queen) => (
          <QueenCard
            key={queen.id}
            queen={queen}
            onStart={queen.chatEnabled ? onStartBardera : onLocked}
          />
        ))}
      </div>
    </section>
  );
}

function QueenCard({ queen, onStart }: { queen: Queen; onStart: () => void }) {
  const live = queen.status === "live";
  const profileReady = queen.profile.status === "ready";
  return (
    <article className={live ? "queen-card live" : "queen-card"} id={`queen-${queen.id}`}>
      <header className="queen-card-head">
        <div>
          <span className="eyebrow">{live ? "BETA ACTIVA" : "EN CURACIÓN"}</span>
          <h3>{queen.name}</h3>
          <p>{queen.tagline}</p>
        </div>
        <div className="queen-card-actions">
          <Link className="button-ghost queen-link" href={`/queen/${queen.id}`}>
            {profileReady ? "DETAILS →" : "PROFILE SLOT"}
          </Link>
          <button className={live ? "button-primary" : "button-ghost"} onClick={onStart}>
            {live ? "HABLÁ CON ELLA →" : "PRONTO"}
          </button>
        </div>
      </header>
      <div className="queen-slots" aria-label={`Previews de ${queen.name}`}>
        {queen.slots.map((imageSlot) => (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            key={imageSlot.src}
            src={imageSlot.src}
            alt={imageSlot.alt}
            width={imageSlot.width}
            height={imageSlot.height}
            loading="lazy"
            decoding="async"
          />
        ))}
      </div>
      <p className="queen-card-note">
        {queen.slots.length} preview{queen.slots.length === 1 ? "" : "s"} · perfil{" "}
        {profileReady ? "listo" : "slot vacío"} · memoria aislada · orden provisional
      </p>
    </article>
  );
}
