export function Footer() {
  return (
    <>
      <footer className="footer">
        <div className="footer-inner">
          <div className="footer-brand">
            <div className="brand-mark" style={{ width: 32, height: 32 }}>
              <svg viewBox="0 0 24 24" style={{ width: 16, height: 16 }} aria-hidden="true">
                <path d="M12 21s-7-4.5-9-9c-1.5-3.5 0.5-7 4-7 2 0 3.5 1 5 3 1.5-2 3-3 5-3 3.5 0 5.5 3.5 4 7-2 4.5-9 9-9 9z" fill="white" />
              </svg>
            </div>
            <span className="name" style={{ fontSize: 14, fontWeight: 600 }}>Companion Studio</span>
          </div>
          <p className="footer-copy">
            © {new Date().getFullYear()} Companion Studio. Prototipo visual cyber-noir.
          </p>
          <p className="footer-note">+18 · Experiencia para adultos con responsabilidad</p>
        </div>
      </footer>
      <div className="adult-note">
        Las companionas son IA. No son personas reales. Contenido para +18.
      </div>
    </>
  );
}
