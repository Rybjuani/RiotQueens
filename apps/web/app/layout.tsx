import type { Metadata } from "next";
import "./styles.css";

export const metadata: Metadata = {
  title: "RiotQueens.ai — Queen al frente",
  description: "Experiencia de entretenimiento +18 con personajes virtuales y ficticios que interactúan mediante IA.",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="es">
      <body>{children}</body>
    </html>
  );
}
