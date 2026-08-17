"use client";

import { useState } from "react";

import { bardera } from "./queen";

export function Navbar({ onCta }: { onCta: () => void }) {
  const [open, setOpen] = useState(false);
  return (
    <header className="site-header">
      <div className="wrap">
        <a className="brand-lockup" href="#top" aria-label="RiotQueens.ai, inicio">
          { }
          <img
            src="/brand/riotqueens-logo.jpeg"
            alt="RiotQueens logo oficial"
            width={1024}
            height={1024}
            decoding="async"
          />
          <span className="brand-text">
            <b>RIOTQUEENS.AI</b>
            <small>ANTI-PERFECT-GF</small>
          </span>
        </a>
        <nav aria-label="Navegación principal" className={open ? "open" : ""}>
          <a href="#manifiesto" onClick={() => setOpen(false)}>MANIFIESTO</a>
          <a href="#bardera" onClick={() => setOpen(false)}>BARDERA</a>
          <a href="#roster" onClick={() => setOpen(false)}>QUEENS</a>
          <a href="#tiers" onClick={() => setOpen(false)}>TIERS</a>
          <a href="#legal" onClick={() => setOpen(false)}>LEGAL</a>
          <button type="button" className="nav-link" onClick={onCta}>
            HABLÁ CON LA BARDERA →
          </button>
        </nav>
        <button
          type="button"
          className="menu-toggle"
          aria-label="Abrir menú"
          aria-expanded={open}
          onClick={() => setOpen((v) => !v)}
        >
          {open ? "CERRAR" : "MENÚ"}
        </button>
      </div>
    </header>
  );
}

// Avoid an unused-import warning when tree-shaking is conservative.
export const _bardera = bardera;
