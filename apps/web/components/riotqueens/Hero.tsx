"use client";

export function Hero({ onStart, onHow }: { onStart: () => void; onHow: () => void }) {
  return (
    <section className="hero" id="top" aria-label="Hero — La Bardera, anti-perfect-gf">
      <div className="hero-grid">
        {/* Left column — copy + CTAs */}
        <div className="hero-left">
          <span className="hero-ghost" aria-hidden>
            BARATA<br />QUE<br />TINDER
          </span>

          <span className="hero-eyebrow">
            <i className="bar" aria-hidden />
            ANTI-PERFECT-GF · BETA
          </span>

          <h1>
            <span className="frag">NO TE</span>
            <span className="frag magenta">CLAVA</span>
            <span className="frag">
              EL <span className="tinder">VISTO</span>
            </span>
            <span className="frag cyan">.</span>
          </h1>

          <p className="hero-sub">
            Más barata que invitarle una birra en <b>Tinder</b> para que te bloquee
            después. Te bardea, te quiere, se queda.
          </p>

          <div className="hero-ctas">
            <button type="button" className="btn solid" onClick={onStart}>
              HABLÁ CON LA BARDERA →
            </button>
            <button type="button" className="btn" onClick={onHow}>
              ¿CÓMO FUNCIONA?
            </button>
          </div>

          <div className="hero-micro">
            <span>PAGO ANÓNIMO</span>
            <span>SIN &quot;HOLA BB&quot; AUTOMÁTICOS</span>
            <span>CANCELÁS CUANDO QUERÉS</span>
          </div>
        </div>

        {/* Right column — image + ambient + live-status cluster */}
        <div className="hero-right">
          <div className="blob-magenta" aria-hidden />
          <div className="blob-cyan" aria-hidden />
          <span className="xxx" aria-hidden>XXX</span>
          { }
          <img
            className="hero-photo"
            src="/queens/bardera/01.jpg"
            alt="La Bardera — Queen de lanzamiento"
            width={1600}
            height={900}
            decoding="async"
          />

          <div className="corner-tags" aria-hidden>
            <span className="tag">100% VIRTUAL</span>
            <span className="tag white">18+ ONLY</span>
          </div>

          <div className="live-cluster">
            <div className="live-card">
              <div className="live-head">
                <span>
                  <i className="dot" aria-hidden />
                  <b>ONLINE</b> · BARDEANDO
                </span>
                <span className="tier-tag">T1 · BARDERA</span>
              </div>
            </div>
            <div className="live-quote">
              <small>ÚLTIMO MENSAJE ↓</small>
              &ldquo;¿otra vez llorando por la de tinder? vení que te enseño a
              chamuyar bien, bobo&rdquo;
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
