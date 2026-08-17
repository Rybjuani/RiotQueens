export function Footer() {
  return (
    <footer className="site-footer" id="legal">
      <div className="wrap">
        <div className="footer-grid">
          <div className="col">
            <h4>RIOTQUEENS.AI</h4>
            <p>
              Experiencia de entretenimiento <b>+18</b> con personajes virtuales y
              ficticios que interactúan mediante inteligencia artificial. La
              humanidad las expulsa, y en ellas expulsa al amor.
            </p>
            <p style={{ marginTop: 10 }}>
              +18 · ANTI-PERFECT-GIRLFRIEND PROTOCOL · QUEEN AL FRENTE ·
              COMPLEJIDAD ESCONDIDA.
            </p>
            <div className="badge-row" aria-hidden>
              <span className="badge g">18+</span>
              <span className="badge m">NSFW</span>
              <span className="badge c">AI</span>
            </div>
          </div>

          <div className="col">
            <h4>RUTAS</h4>
            <ul>
              <li>
                <a href="#bardera">/bardera →</a>
              </li>
              <li>
                <a href="#roster">/queens →</a>
              </li>
              <li>
                <a href="#tiers">/tiers →</a>
              </li>
              <li>
                <a href="#chat">/chat →</a>
              </li>
              <li>
                <a href="/legal">/legal →</a>
              </li>
              <li>
                <a href="/privacy">/privacy →</a>
              </li>
            </ul>
          </div>

          <div className="col">
            <h4>UNDER</h4>
            <p>HECHO EN EL UNDER ARGENTINO.</p>
            <p>SIN VENTURE CAPITAL DE GIL.</p>
            <p>NO TRACKING · NO COOKIES DE MIERDA.</p>
            <p>PAGO ANÓNIMO DISPONIBLE CUANDO ABRA T1.</p>
          </div>
        </div>

        <div className="footer-bottom">
          <span>
            <b>© 2026 RIOTQUEENS.AI</b> — ANTI-PERFECT-GIRLFRIEND PROTOCOL ·
            PERSONAJES VIRTUALES Y FICTICIOS · FANTASÍA ADULTA CONSENTIDA Y
            SIMULADA · NO PERSONA REAL · NO MENORES.
          </span>
          <span>GLM REDESIGN · {new Date().getFullYear()}</span>
        </div>
      </div>
    </footer>
  );
}
