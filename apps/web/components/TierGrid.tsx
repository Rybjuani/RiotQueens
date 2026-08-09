"use client";

const TIERS = [
  { id: "T0", title: "PRESENCIA", status: "PREVIEW", copy: "Una primera señal. Suficiente para saber si querés entrar." },
  { id: "T1", title: "PROXIMIDAD", status: "BETA ABIERTA", copy: "Chat, continuidad de sesión y biblioteca contextual.", active: true },
  { id: "T2", title: "PREMIUM", status: "EN CURACIÓN", copy: "Piezas raras, mayor producción y continuidad visual exigente." },
  { id: "T3", title: "A MEDIDA", status: "PRÓXIMAMENTE", copy: "Pedidos específicos, prioridad y generación cuando corresponda." },
];

export function TierGrid({ onStart, onLocked }: { onStart: () => void; onLocked: () => void }) {
  return (
    <section className="tiers" id="tiers">
      <div className="section-heading compact">
        <span className="eyebrow cyan">ACCESO / VALOR / COSTO</span>
        <h2>NO ES MÁS TEMPERATURA.<br /><span>ES MÁS POSIBILIDAD.</span></h2>
      </div>
      <div className="tier-grid">
        {TIERS.map((tier) => (
          <article className={tier.active ? "tier-card active" : "tier-card"} key={tier.id}>
            <div className="tier-top"><strong>{tier.id}</strong><span>{tier.status}</span></div>
            <h3>{tier.title}</h3>
            <p>{tier.copy}</p>
            <button onClick={tier.active ? onStart : onLocked}>{tier.active ? "PROBAR AHORA →" : "VER ESTADO"}</button>
          </article>
        ))}
      </div>
      <p className="credits-note"><b>TIER</b> = capacidad base. <b>CRÉDITOS</b> = costo variable visible antes de confirmar.</p>
    </section>
  );
}
