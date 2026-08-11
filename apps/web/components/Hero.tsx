"use client";

export function Hero({ onStart, onHow }: { onStart: () => void; onHow: () => void }) {
  return (
    <section className="hero" id="top">
      <div className="hero-copy">
        <span className="eyebrow cyan">NO TE CLAVA EL VISTO</span>
        <h1>
          NO ES UNA<br />
          <span className="glitch">GALERÍA.</span><br />
          <em>ESTÁ AHÍ.</em>
        </h1>
        <p className="hero-lead">
          Te bardea. Te quiere. Se queda.
          <strong> Queen al frente. Complejidad escondida.</strong>
        </p>
        <div className="hero-actions">
          <button className="button-primary" onClick={onStart}>HABLÁ CON LA BARDERA →</button>
          <button className="button-ghost" onClick={onHow}>¿CÓMO?</button>
        </div>
        <div className="hero-proof">
          <span>ACCESO FREE</span>
          <span>BETA ACTIVA</span>
          <span>PERSONAJE VIRTUAL +18</span>
        </div>
      </div>
      <div className="hero-visual">
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img src="/queens/img-042-hero.jpg" alt="La Bardera en su setup creativo" width={1672} height={941} decoding="async" fetchPriority="high" />
        <div className="hero-vignette" />
        <div className="hero-stamp">BARDERA<br /><span>QUEEN DE LANZAMIENTO</span></div>
        <div className="live-card">
          <span>ACCESO FREE / BETA</span>
          <strong><i /> CHAT DISPONIBLE</strong>
          <p>NO TE CLAVA EL VISTO.</p>
        </div>
      </div>
    </section>
  );
}
