"use client";

export function Experience({ onStart }: { onStart: () => void }) {
  return (
    <section className="experience" id="experience">
      <div className="section-heading">
        <span className="eyebrow">PRODUCTO DEBAJO</span>
        <h2>UNA QUEEN.<br /><span>CONTINUIDAD REAL.</span></h2>
        <p>No hace falta entender el stack. Entrás a hablar; el sistema sostiene el resto.</p>
      </div>

      <div className="experience-grid">
        <article className="experience-photo">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src="/queens/img-065-reference.jpg" alt="Retrato de cuerpo completo de La Bardera" />
          <div><b>IDENTIDAD</b><span>Una presencia reconocible, no un catálogo infinito.</span></div>
        </article>
        <div className="experience-stack">
          <article><span>01</span><h3>HABLA</h3><p>Chat temprano, lenguaje natural y una voz que no necesita actuar cada línea.</p><b>PROTOTIPO ACTIVO</b></article>
          <article><span>02</span><h3>RECUERDA</h3><p>El backend conserva el hilo de la conversación. Persistencia durable: próximo corte.</p><b>EN PROCESO</b></article>
          <article><span>03</span><h3>APARECE</h3><p>Fotos y escenas llegan desde una biblioteca curada, con origen y nivel registrados.</p><b>LIBRARY-FIRST</b></article>
          <article><span>04</span><h3>PRODUCE</h3><p>Pedidos personalizados y Cloud Lab se habilitan cuando tier y créditos lo permitan.</p><b>PLANIFICADO</b></article>
        </div>
      </div>

      <div className="narrative-card">
        <div>
          <span className="eyebrow cyan">PRESENCIA / INICIATIVA</span>
          <blockquote>“Salí tarde. Vi algo que te habría hecho reír. Después te cuento.”</blockquote>
          <p>Contexto, sorpresa y continuidad. La voz siempre tiene dueño.</p>
          <button className="button-primary" onClick={onStart}>ABRIR EL CHAT →</button>
        </div>
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img src="/queens/img-074-support.jpg" alt="La Bardera en una terraza al atardecer" />
      </div>
    </section>
  );
}
