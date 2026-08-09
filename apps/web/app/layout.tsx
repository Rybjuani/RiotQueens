import type { Metadata } from "next";
import "./styles.css";

export const metadata: Metadata = {
  title: "RiotQueens.ai — Queen al frente",
  description: "Conversación, memoria y presencia audiovisual con identidad propia.",
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
