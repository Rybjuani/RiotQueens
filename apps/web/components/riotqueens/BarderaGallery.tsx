"use client";

import { useEffect, useState } from "react";

import { bardera } from "./queen";

const GALLERY = bardera.slots.slice(0, 4);

export function BarderaGallery({ onStartBardera }: { onStartBardera: () => void }) {
  const [lightbox, setLightbox] = useState<number | null>(null);

  useEffect(() => {
    if (lightbox === null) return;
    const onKey = (event: KeyboardEvent) => {
      if (event.key === "Escape") setLightbox(null);
      if (event.key === "ArrowRight") setLightbox((i) => (i === null ? i : (i + 1) % GALLERY.length));
      if (event.key === "ArrowLeft")
        setLightbox((i) => (i === null ? i : (i - 1 + GALLERY.length) % GALLERY.length));
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [lightbox]);

  return (
    <section className="t1" id="bardera" aria-label="La Bardera — T1, Queen de lanzamiento">
      <div className="wrap">
        <div className="head-row">
          <div className="left">
            <span className="label">T1 · DISPONIBLE AHORA · FREE / PREVIEW</span>
            <h2>LA BARDERA</h2>
            <span className="tag">
              PUNK · BEER · 0% BUENA ONDA FAKE. La que te caga a pedos pero se queda.
              Identidad persistente, memoria por hilo.
            </span>
          </div>
          <div className="price-row">
            <div className="price">FREE / PREVIEW</div>
            <small>primer nivel ·gratis para arrancar</small>
            <div className="price-note">planes pagos próximamente</div>
          </div>
        </div>

        <div className="gallery" aria-label="Galería de La Bardera">
          {GALLERY.map((slot, index) => (
            <button
              type="button"
              className="ph"
              key={slot.src}
              onClick={() => setLightbox(index)}
              aria-label={`Ampliar: ${slot.alt}`}
            >
              <span className="ph-tag">0{index + 1}</span>
              { }
              <img
                src={slot.src}
                alt={slot.alt}
                width={slot.width}
                height={slot.height}
                loading="lazy"
                decoding="async"
              />
              <span className="ph-overlay">Pose 0{index + 1} · La Bardera</span>
            </button>
          ))}
        </div>

        <div className="features">
          <span className="feat">Te bardea pero con amor</span>
          <span className="feat">Roleplay de bar a las 3am</span>
          <span className="feat">No te ghostea jamás</span>
          <span className="feat">Memoria por hilo, no catálogo</span>
        </div>
        <button type="button" className="btn solid" onClick={onStartBardera}>
          HABLÁ CON LA BARDERA →
        </button>
      </div>

      {lightbox !== null && (
        <div
          className="lightbox"
          role="dialog"
          aria-modal="true"
          aria-label="Vista ampliada"
          onClick={() => setLightbox(null)}
        >
          <button
            type="button"
            className="x"
            aria-label="Cerrar"
            onClick={() => setLightbox(null)}
          >
            ×
          </button>
          <button
            type="button"
            className="nav-arrow prev"
            aria-label="Anterior"
            onClick={(e) => {
              e.stopPropagation();
              setLightbox((i) => (i === null ? i : (i - 1 + GALLERY.length) % GALLERY.length));
            }}
          >
            ‹
          </button>
          { }
          <img
            src={GALLERY[lightbox].src}
            alt={GALLERY[lightbox].alt}
            width={GALLERY[lightbox].width}
            height={GALLERY[lightbox].height}
            onClick={(e) => e.stopPropagation()}
          />
          <button
            type="button"
            className="nav-arrow next"
            aria-label="Siguiente"
            onClick={(e) => {
              e.stopPropagation();
              setLightbox((i) => (i === null ? i : (i + 1) % GALLERY.length));
            }}
          >
            ›
          </button>
        </div>
      )}
    </section>
  );
}
