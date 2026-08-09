export function Footer() {
  return (
    <footer className="site-footer">
      <div className="footer-brand">
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img src="/brand/riotqueens-logo.jpeg" alt="Logo de RiotQueens" />
        <div><b>RiotQueens.ai</b><span>QUEEN AL FRENTE.</span></div>
      </div>
      <div className="footer-links"><a href="/legal">LEGAL</a><a href="/privacy">PRIVACIDAD</a></div>
      <p>© {new Date().getFullYear()} RiotQueens.ai · +18</p>
    </footer>
  );
}
