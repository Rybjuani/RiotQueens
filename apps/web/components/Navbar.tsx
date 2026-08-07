"use client";

import { useEffect, useState } from "react";

export function Navbar({ onCta }: { onCta: () => void }) {
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 12);
    onScroll();
    window.addEventListener("scroll", onScroll);
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <header className={scrolled ? "navbar scrolled" : "navbar"}>
      <nav className="navbar-inner">
        <div className="brand">
          <div className="brand-mark">
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <path d="M12 21s-7-4.5-9-9c-1.5-3.5 0.5-7 4-7 2 0 3.5 1 5 3 1.5-2 3-3 5-3 3.5 0 5.5 3.5 4 7-2 4.5-9 9-9 9z" />
            </svg>
          </div>
          <div className="brand-text">
            <span className="name">Companion</span>
            <span className="tag">Studio</span>
          </div>
        </div>
        <div className="nav-links">
          <button onClick={() => document.getElementById("companion")?.scrollIntoView({ behavior: "smooth" })}>La compañera</button>
          <button onClick={() => document.getElementById("capabilities")?.scrollIntoView({ behavior: "smooth" })}>Capacidades</button>
        </div>
        <button className="nav-cta" onClick={onCta}>Empezar</button>
      </nav>
    </header>
  );
}
