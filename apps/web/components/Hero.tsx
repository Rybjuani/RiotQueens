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
          Habla, recuerda, reacciona y aparece cuando la conversación lo pide.
          <strong> Queen al frente. Complejidad escondida.</strong>
        </p>
        <div className="hero-actions">
          <button className="button-primary" onClick={onStart}>HABLÁ CON LA BARDERA →</button>
          <button className="button-ghost" onClick={onHow}>¿CÓMO?</button>
        </div>
        <div className="hero-proof">
          <span>CONVERSACIÓN REAL</span>
          <span>MEMORIA EN CONSTRUCCIÓN</span>
          <span>BIBLIOTECA CURADA</span>
        </div>
      </div>
      <div className="hero-visual">
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img src="/queens/img-042-hero.jpg" alt="La Bardera en estudio con luces violetas" />
        <div className="hero-vignette" />
        <div className="hero-stamp">T1<br /><span>LA BARDERA</span></div>
        <div className="live-card">
          <span>LIVE STATUS</span>
          <strong><i /> BETA ONLINE</strong>
          <p>“Dale. Contame desde el principio, sin versión prolija.”</p>
        </div>
      </div>
    </section>
  );
}
