import type { Metadata } from "next";
import "./styles.css";

export const metadata: Metadata = {
  title: "Companion Studio — Una presencia con carácter",
  description:
    "Companion Studio: una compañera IA adulta con personalidad continua, " +
    "arquitectura de memoria y presencia audiovisual. Prototipo visual cyber-noir.",
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
