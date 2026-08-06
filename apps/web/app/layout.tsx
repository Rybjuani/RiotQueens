import type { Metadata } from "next";
import "./styles.css";

export const metadata: Metadata = { title: "Companion Studio", description: "Bootstrap vertical" };

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="es"><body>{children}</body></html>;
}
