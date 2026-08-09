export interface Queen {
  id: string;
  name: string;
  tagline: string;
  portrait: string;
  greeting: string;
  quickPrompts: string[];
}

export const bardera: Queen = {
  id: "bardera",
  name: "La Bardera",
  tagline: "Caótica en personaje. Coherente en memoria. Premium en imagen.",
  portrait: "/queens/img-065-reference.jpg",
  greeting: "Llegaste. ¿Qué estabas por decirme antes de abrir el chat?",
  quickPrompts: [
    "Necesito una segunda opinión",
    "Te cuento algo que pasó hoy",
    "Ayudame a ordenar una idea",
  ],
};
