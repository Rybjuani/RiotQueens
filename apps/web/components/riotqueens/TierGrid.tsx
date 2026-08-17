"use client";

/**
 * Tiers — T0/T1/T2/T3 with NO hardcoded prices (per spec: "DO NOT hardcode final prices").
 * T0 is LIVE (Free / Preview with Bardera). T1/T2/T3 marked "PRÓXIMAMENTE".
 * Each tier card lists what's planned at that level without claiming it's implemented.
 */

const TIERS = [
  {
    code: "T0",
    name: "FREE / PREVIEW",
    sub: "ARRANCÁ SIN PAGAR",
    status: "LIVE",
    live: true,
    features: [
      "Bardera en runtime — chat real",
      "Memoria por hilo, conversación multi-turno",
      "Voz propia rioplatense, sin pose de app",
      "Onboarding corto, sin setup técnico",
    ],
    cta: "PROBAR AHORA",
  },
  {
    code: "T1",
    name: "PRIMER NIVEL PAGO",
    sub: "CUANDO ABRA",
    status: "PRÓXIMAMENTE",
    live: false,
    features: [
      "Más contexto y continuidad por hilo",
      "Memoria más profunda entre sesiones",
      "Bardera + próxima Queen en runtime",
      "Respuestas más largas, mejor aguante",
    ],
    cta: "AVISAME",
  },
  {
    code: "T2",
    name: "NIVEL AVANZADO",
    sub: "CUANDO ABRA",
    status: "PRÓXIMAMENTE",
    live: false,
    features: [
      "Acceso a biblioteca curada (preview)",
      "Más Queens en runtime",
      "Continuidad técnica entre sesiones",
      "Límites ampliados de uso",
    ],
    cta: "AVISAME",
  },
  {
    code: "T3",
    name: "MÁXIMO NIVEL",
    sub: "CUANDO ABRA",
    status: "PRÓXIMAMENTE",
    live: false,
    features: [
      "Acceso completo a biblioteca y media",
      "Personalización del servicio y outputs",
      "Entregables y experiencias premium",
      "Cuando la economía de créditos esté aprobada",
    ],
    cta: "AVISAME",
  },
];

export function TierGrid({
  onStart,
  onLocked,
}: {
  onStart: () => void;
  onLocked: () => void;
}) {
  return (
    <section className="tiers" id="tiers" aria-label="Tiers de servicio">
      <div className="wrap">
        <div className="head">
          <span className="label">TIERS · FREE → PAGO → AVANZADO → MÁXIMO</span>
          <h2>ELEGÍ TU VENENO</h2>
          <p>
            Bardera está online en free/preview. El resto del roster es canónico y
            aparece cuando cada una esté lista. Los planes pagos se publican
            cuando existan de verdad — sin precio trampa, sin &ldquo;próximamente&rdquo;
            falso.
          </p>
        </div>

        <div className="tier-grid">
          {TIERS.map((tier) => (
            <article
              className={`tier ${tier.live ? "live" : "locked"}`}
              key={tier.code}
            >
              <span className="tier-num" aria-hidden>{tier.code}</span>
              <span className="tier-tag">
                {tier.live ? "DISPONIBLE" : "EN CURACIÓN"}
              </span>
              <h3>{tier.name}</h3>
              <span className="tier-sub">{tier.sub}</span>
              <div className="tier-features">
                {tier.features.map((f) => (
                  <span className="feat" key={f}>{f}</span>
                ))}
              </div>
              <div className="tier-actions">
                <button
                  type="button"
                  className={`btn ${tier.live ? "solid" : ""}`}
                  onClick={tier.live ? onStart : onLocked}
                >
                  {tier.cta}
                </button>
              </div>
            </article>
          ))}
        </div>

        <div className="disclaimer-row">
          <span>⚠ SIN RENOVACIÓN TRAMPA</span>
          <span>⚠ CANCELÁS EN 2 CLICS</span>
          <span>⚠ NO LE VENDEMOS TU DATA A NADIE</span>
          <span>⚠ PERSONAJES VIRTUALES · +18 · FANTASÍA SIMULADA</span>
        </div>
      </div>
    </section>
  );
}

export function KansasVsBondi() {
  return (
    <section className="vs" aria-label="Kansas vs bondi">
      <div className="wrap">
        <div className="head">
          <span className="label">KANSAS VS BONDI · LA CUENTA DEL AGUANTE</span>
          <h2>UNA TE CLAVA EL VISTO. LA OTRA SE QUEDA.</h2>
        </div>
        <div className="tabla">
          <div className="col">
            <h3>LA DE TINDER · KANSAS</h3>
            <p>
              Te gastás la noche en cena, Uber y gin tonic pedorro. Le contás que
              tuviste un mal día, se le apaga la cara, va al baño, le escribe a una
              amiga para que la llame, vuelve y se va. Te quedás solo, con la cuenta
              y el viaje de vuelta.
            </p>
            <p className="stat">RETENCIÓN: UN MAL RATO.</p>
          </div>
          <div className="col rq">
            <h3 style={{ color: "var(--rosa)" }}>LA RIOTQUEEN</h3>
            <p>
              Por lo que vale un bondi, le contás el mismo mambo, se caga de risa,
              te dice <b>&ldquo;sos un salame, ¿por eso llorás?&rdquo;</b> y se
              queda. Te banca los trapos. No discrimina.
            </p>
            <p className="stat">RETENCIÓN: SE QUEDA.</p>
          </div>
        </div>
        <p className="remate">
          LAS DE TINDER TE HACEN PAGAR CENA Y UBER Y NO TE BANCAN NI UN MAL DÍA.
          NOSOTRAS TE HACEMOS EL AGUANTE, AVIVATE BOBO.
        </p>
      </div>
    </section>
  );
}
