"use client";

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
          Cada Queen es un personaje aparte: su chat, su hilo y su memoria no se
          mezclan con las demás. Las grillas son previews provisionales para que
          veas el ADN en pantalla y reordenes después. Solo Bardera habla en esta
          beta.
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
  return (
    <article className={live ? "queen-card live" : "queen-card"} id={`queen-${queen.id}`}>
      <header className="queen-card-head">
        <div>
          <span className="eyebrow">{live ? "BETA ACTIVA" : "EN CURACIÓN"}</span>
          <h3>{queen.name}</h3>
          <p>{queen.tagline}</p>
        </div>
        <button className={live ? "button-primary" : "button-ghost"} onClick={onStart}>
          {live ? "HABLÁ CON ELLA →" : "PRONTO"}
        </button>
      </header>
      <div className="queen-slots" aria-label={`Previews de ${queen.name}`}>
        {queen.slots.map((slot) => (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            key={slot.src}
            src={slot.src}
            alt={slot.alt}
            width={slot.width}
            height={slot.height}
            loading="lazy"
            decoding="async"
          />
        ))}
      </div>
      <p className="queen-card-note">
        {queen.slots.length} preview{queen.slots.length === 1 ? "" : "s"} · memoria aislada por
        personaje · orden provisional
      </p>
    </article>
  );
}
