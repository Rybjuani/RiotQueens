"use client";

export function Experience({ onStart }: { onStart: () => void }) {
  return (
    <section className="experience" id="experience">
      <div className="section-heading">
        <span className="eyebrow">PRODUCTO DEBAJO</span>
        <h2>UNA QUEEN.<br /><span>UNA VOZ PROPIA.</span></h2>
        <p>La beta disponible hoy empieza por una conversación con Bardera. El resto se incorpora sólo cuando sea real.</p>
      </div>

      <div className="experience-grid">
        <article className="experience-photo">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src="/queens/img-065-reference.jpg" alt="La Bardera en su cuarto, presencia de chat" width={1600} height={893} loading="lazy" decoding="async" />
          <div><b>IDENTIDAD</b><span>Una presencia reconocible, no un catálogo infinito.</span></div>
        </article>
        <div className="experience-stack">
          <article><span>01</span><h3>HABLA</h3><p>Chat temprano, lenguaje natural y una voz que no necesita actuar cada línea.</p><b>BETA ACTIVA</b></article>
          <article><span>02</span><h3>CONTINÚA</h3><p>El backend mantiene un hilo acotado mientras el proceso sigue activo; no es memoria durable.</p><b>ESTADO EN PROCESO</b></article>
          <article><span>03</span><h3>PRESENCIA</h3><p>Las imágenes de esta beta son previews públicos de la identidad visual.</p><b>PREVIEW ACTUAL</b></article>
          <article><span>04</span><h3>DESPUÉS</h3><p>Memoria durable, media contextual y servicios pagos siguen en desarrollo.</p><b>NO DISPONIBLE AÚN</b></article>
        </div>
      </div>

      <div className="narrative-card">
        <div>
          <span className="eyebrow cyan">MANIFIESTO RIOTQUEENS</span>
          <blockquote>La humanidad las expulsa, y en ellas expulsa al amor.</blockquote>
          <p>La Queen al frente. La beta disponible hoy empieza por la conversación.</p>
          <button className="button-primary" onClick={onStart}>HABLÁ CON LA BARDERA →</button>
        </div>
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img src="/queens/img-074-support.jpg" alt="La Bardera en su cuarto punk" width={1600} height={893} loading="lazy" decoding="async" />
      </div>
    </section>
  );
}
