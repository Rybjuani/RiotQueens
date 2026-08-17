"use client";

import { queens } from "./queen";

export function QueenRoster({
  onStartBardera,
  onLocked,
}: {
  onStartBardera: () => void;
  onLocked: (queenName: string) => void;
}) {
  return (
    <section className="roster" id="roster" aria-label="Roster de Queens canónicas">
      <div className="wrap">
        <div className="head">
          <span className="label">ROSTER · 5 QUEENS CANÓNICAS</span>
          <h2>ELEGÍ TU RIOT QUEEN</h2>
          <p>
            Cinco identidades. Una esencia. Bardera es la única en runtime hoy; las
            demás son canónicas y salen al escenario cuando cada una esté lista.
            Sin placeholder negro: si tiene foto, está.
          </p>
        </div>

        <div className="queen-grid">
          {queens.map((queen) => {
            const live = queen.chatEnabled;
            return (
              <article
                className={`queen-card ${live ? "live" : "curation"}`}
                key={queen.id}
                id={`queen-${queen.id}`}
              >
                <div className="photo">
                  <span className="badge">{live ? "LIVE · T1" : "EN CURACIÓN"}</span>
                  { }
                  <img
                    src={queen.card}
                    alt={`${queen.name} — portrait`}
                    width={900}
                    height={1125}
                    loading="lazy"
                    decoding="async"
                  />
                  {live && (
                    <span className="live-pill">
                      <i className="dot" aria-hidden />
                      ONLINE
                    </span>
                  )}
                </div>
                <div className="body">
                  <h3>{queen.name}</h3>
                  <span className="tag">{queen.tagline}</span>
                  <p className="desc">{queen.essence}</p>
                  <div className="actions">
                    {live ? (
                      <button
                        type="button"
                        className="btn solid"
                        onClick={onStartBardera}
                      >
                        HABLÁ CON LA BARDERA →
                      </button>
                    ) : (
                      <button
                        type="button"
                        className="btn"
                        onClick={() => onLocked(queen.name)}
                      >
                        PRÓXIMAMENTE
                      </button>
                    )}
                  </div>
                </div>
              </article>
            );
          })}
        </div>
      </div>
    </section>
  );
}
