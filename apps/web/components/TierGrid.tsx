"use client";

const TIERS = [
  { id: "T0", title: "FREE / PREVIEW", status: "BETA ACTIVA", copy: "Experiencia gratuita y limitada para conocer el servicio.", active: true },
  { id: "T1", title: "PRIMER NIVEL PAGO", status: "EN DEFINICIÓN", copy: "Precio, límites y beneficios todavía no están definidos." },
  { id: "T2", title: "NIVEL PAGO AVANZADO", status: "EN DEFINICIÓN", copy: "Se habilitará sólo cuando sus capacidades estén implementadas y verificadas." },
  { id: "T3", title: "MÁXIMO NIVEL", status: "EN DEFINICIÓN", copy: "La personalización futura no cambia la identidad básica de la Queen." },
];

export function TierGrid({ onStart, onLocked }: { onStart: () => void; onLocked: () => void }) {
  return (
    <section className="tiers" id="tiers">
      <div className="section-heading compact">
        <span className="eyebrow cyan">ACCESO / SERVICIO</span>
        <h2>UNA QUEEN.<br /><span>DISTINTAS POSIBILIDADES.</span></h2>
      </div>
      <div className="tier-grid">
        {TIERS.map((tier) => (
          <article className={tier.active ? "tier-card active" : "tier-card"} key={tier.id}>
            <div className="tier-top"><strong>{tier.id}</strong><span>{tier.status}</span></div>
            <h3>{tier.title}</h3>
            <p>{tier.copy}</p>
            <button onClick={tier.active ? onStart : onLocked}>{tier.active ? "ENTRAR A LA BETA →" : "VER ESTADO"}</button>
          </article>
        ))}
      </div>
      <p className="credits-note">La matriz de precios, límites y beneficios de <b>T1–T3</b> está pendiente. No hay pagos activos en esta beta.</p>
    </section>
  );
}
