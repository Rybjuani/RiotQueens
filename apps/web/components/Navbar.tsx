"use client";

import { useEffect, useState } from "react";

export function Navbar({ onCta }: { onCta: () => void }) {
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 16);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <header className={scrolled ? "site-header scrolled" : "site-header"}>
      <nav className="site-nav" aria-label="Navegación principal">
        <a className="brand-lockup" href="#top" aria-label="RiotQueens.ai, inicio">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src="/brand/riotqueens-logo.jpeg" alt="" />
          <span>RiotQueens<span>.ai</span></span>
        </a>
        <div className="nav-status"><b>+18</b><span>VIRTUAL</span><span>BETA</span></div>
        <button className="nav-cta" onClick={onCta}>ENTRAR →</button>
      </nav>
    </header>
  );
}
