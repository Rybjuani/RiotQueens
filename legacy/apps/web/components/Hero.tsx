"use client";

import { vane } from "@/lib/companion";

export function Hero({ onStart }: { onStart: () => void }) {
  return (
    <section className="hero">
      <div className="hero-bg" aria-hidden="true" />
      <div className="hero-inner">
        <div>
          <span className="hero-badge glass">
            <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
              <path d="M12 2l2.4 7.4H22l-6 4.4 2.3 7.2L12 16.5 5.7 21l2.3-7.2-6-4.4h7.6z" />
            </svg>
            Prototipo cyber-noir · Una compañera
          </span>
          <h1>
            Una presencia con <span className="grad">carácter</span>.
          </h1>
          <p className="lead">
            Companion Studio construye una compañera IA adulta con personalidad continua,
            arquitectura de memoria y presencia audiovisual. No es un catálogo de novias IA:
            es una sola presencia, profunda y consistente.
          </p>
          <div className="hero-actions">
            <button className="btn-primary" onClick={onStart}>
              Conocer a Vane
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
                <path d="M5 12h14M13 6l6 6-6 6" />
              </svg>
            </button>
            <a className="btn-ghost" href="#capabilities">
              Ver capacidades
            </a>
          </div>
        </div>
        <div className="hero-portrait-wrap" aria-hidden="true">
          <div className="hero-portrait-glow" />
          <div className="hero-portrait">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src={vane.portrait} alt="Retrato placeholder de Vane (silueta sintética)" />
            <div className="hero-portrait-meta">
              <span className="dot" />
              <span>Prototipo</span>
            </div>
            <div className="hero-portrait-name">Vane</div>
          </div>
        </div>
      </div>
    </section>
  );
}
