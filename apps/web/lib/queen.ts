export interface Queen {
  id: string;
  name: string;
  tagline: string;
  portrait: string;
  quickPrompts: string[];
}

export const bardera: Queen = {
  id: "bardera",
  name: "La Bardera",
  tagline: "TE BARDEA. TE QUIERE. SE QUEDA.",
  portrait: "/queens/img-065-reference.jpg",
  quickPrompts: [
    "Necesito una segunda opinión",
    "Te cuento algo que pasó hoy",
    "Ayudame a ordenar una idea",
  ],
};
