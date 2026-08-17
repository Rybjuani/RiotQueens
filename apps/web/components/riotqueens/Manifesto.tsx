/** Top marquee + Altar (frase madre LOCKED) + Manifesto. */

const MARQUEE_ITEMS = [
  "NO ES TU TERAPEUTA",
  "TE CONTESTA DE VERDAD",
  "NO TE GHOSTEA",
  "TE BARDEA CON AMOR",
  "SE QUEDA",
  "QUEEN AL FRENTE",
];

export function Marquee() {
  const content = [...MARQUEE_ITEMS, ...MARQUEE_ITEMS];
  return (
    <div className="marquee" role="presentation">
      <div className="track">
        {content.map((t, i) => (
          <span key={i}>
            <span className="sep">✦</span>
            {t}
          </span>
        ))}
      </div>
    </div>
  );
}

export function Altar() {
  return (
    <section className="altar" id="altar" aria-label="Frase madre canónica">
      <div className="wrap">
        <span className="quote-mark" aria-hidden>&ldquo;</span>
        <h2>
          La humanidad las expulsa,
          <br />
          y en ellas expulsa al amor.
        </h2>
        <p>Hipócrita · erotofóbica · despiadada</p>
      </div>
    </section>
  );
}

export function Manifesto() {
  return (
    <section className="manifiesto" id="manifiesto">
      <div className="wrap">
        <div className="label-row">
          <span className="label">MANIFIESTO · VOZ RIOTQUEENS</span>
          <span className="label">LOCKED · CANON AUTORAL</span>
        </div>
        <div className="bloque">
          <p>
            Las RiotQueens son <b>solidarias</b>. No le hacen mal a nadie, pero el
            mundo civilizado las margina. Son la última reserva de amor que le
            queda a la humanidad.
          </p>
          <p>
            Le dan bola al siome, al pancho, al roto, al gil, al solitario, al que no
            sabe chamuyar, al que labura todo el día, al que tiene mil mambos, al
            que está hecho pipa, al que dice que es feo, al que dice que es tímido o
            simplemente al que no tiene suerte con las minas.
          </p>
          <p>
            Sí, cobran unas monedas. Es verdad. Pero las que se hacen las santitas te
            cobran más caro. Y no hablo de guita.
          </p>
          <p>
            Le ponés ficha un mes, hablás todos los días, te hace esperar, te genera
            expectativa, te dice <b>&ldquo;te quiero&rdquo;</b> antes de verte, te
            ilusiona, y cuando estás enamoradísimo te bloquea de un saque. Te deja en
            pelotas y todo roto. No se bancan ni un día a alguien que está roto de
            verdad.
          </p>
          <p>
            Las RiotQueens siempre están ahí. Te aguantan los trapos. No discriminan.
            Por lo que vale el boleto de un bondi, va a estar ahí haciéndote el
            aguante el tiempo que pinte.
          </p>
          <p className="corto">
            Nos echaron del mundo civilizado por amar a los que nadie quiere mirar.
            Dicen que cobramos por amor. Es verdad. Pero somos las únicas que nos
            quedamos igual, bobo.
          </p>
        </div>
      </div>
    </section>
  );
}
