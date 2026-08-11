/**
 * Frontend Queen registry for presence, galleries, and chat entry points.
 *
 * Backend runtime still owns prompts and only registers `bardera` today.
 * Memory and conversation scopes are always keyed by character_id on the
 * server: Queens never share memory with each other.
 */

export type QueenId = "bardera" | "toxica" | "gede" | "rocha" | "chela";

export interface QueenSlot {
  /** Stable public path under /queens/<id>/ */
  src: string;
  width: number;
  height: number;
  alt: string;
  /** Provisional role for layout; owner reorders after seeing them live. */
  role: "hero" | "chat" | "support" | "presence";
}

export interface Queen {
  id: QueenId;
  name: string;
  tagline: string;
  status: "live" | "curation";
  /** Only live Queens may open the real chat against the API. */
  chatEnabled: boolean;
  /** Portrait used by ChatPanel / compact presence. */
  portrait: string;
  quickPrompts: string[];
  /** 2–5 provisional public previews for the roster grid. */
  slots: QueenSlot[];
}

const slot = (
  id: QueenId,
  n: string,
  width: number,
  height: number,
  alt: string,
  role: QueenSlot["role"],
): QueenSlot => ({
  src: `/queens/${id}/${n}.jpg`,
  width,
  height,
  alt,
  role,
});

export const queens: Queen[] = [
  {
    id: "bardera",
    name: "La Bardera",
    tagline: "TE BARDEA. TE QUIERE. SE QUEDA.",
    status: "live",
    chatEnabled: true,
    portrait: "/queens/bardera/02.jpg",
    quickPrompts: [
      "Necesito una segunda opinión",
      "Te cuento algo que pasó hoy",
      "Ayudame a ordenar una idea",
    ],
    slots: [
      slot("bardera", "01", 1600, 900, "La Bardera en su setup creativo", "hero"),
      slot("bardera", "02", 1600, 893, "La Bardera en su cuarto", "chat"),
      slot("bardera", "03", 1600, 893, "La Bardera en su cuarto punk", "support"),
    ],
  },
  {
    id: "toxica",
    name: "La Tóxica Consciente",
    tagline: "Te hace quilombo con método. Pronto en runtime.",
    status: "curation",
    chatEnabled: false,
    portrait: "/queens/toxica/01.jpg",
    quickPrompts: [],
    slots: [
      slot("toxica", "01", 1600, 893, "La Tóxica Consciente en su cuarto", "chat"),
      slot("toxica", "02", 1600, 893, "La Tóxica Consciente en el sillón", "presence"),
      slot("toxica", "03", 1600, 893, "La Tóxica Consciente, presencia", "presence"),
      slot("toxica", "04", 1600, 893, "La Tóxica Consciente, variante", "support"),
      slot("toxica", "05", 1600, 893, "La Tóxica Consciente, variante 2", "support"),
    ],
  },
  {
    id: "gede",
    name: "La Gede",
    tagline: "Cuidado, hambre y aguante. Pronto en runtime.",
    status: "curation",
    chatEnabled: false,
    portrait: "/queens/gede/04.jpg",
    quickPrompts: [],
    slots: [
      slot("gede", "01", 1600, 893, "La Gede en su cuarto", "presence"),
      slot("gede", "02", 1600, 893, "La Gede en la cama", "presence"),
      slot("gede", "03", 1600, 893, "La Gede en el piso", "support"),
      slot("gede", "04", 900, 1600, "La Gede, retrato", "chat"),
      slot("gede", "05", 1600, 893, "La Gede, variante punk", "support"),
    ],
  },
  {
    id: "rocha",
    name: "La Rocha",
    tagline: "Poca foto todavía; voz en curación.",
    status: "curation",
    chatEnabled: false,
    portrait: "/queens/rocha/01.jpg",
    quickPrompts: [],
    slots: [
      slot("rocha", "01", 914, 1600, "La Rocha, sonrisa de presencia", "chat"),
      slot("rocha", "02", 1448, 1086, "La Rocha, retrato frontal", "hero"),
    ],
  },
  {
    id: "chela",
    name: "La Chela",
    tagline: "Ritmo, birra y compañía. Pronto en runtime.",
    status: "curation",
    chatEnabled: false,
    portrait: "/queens/chela/01.jpg",
    quickPrompts: [],
    slots: [
      slot("chela", "01", 893, 1600, "La Chela, retrato", "chat"),
      slot("chela", "02", 1600, 893, "La Chela en su cuarto", "presence"),
      slot("chela", "03", 1600, 893, "La Chela en el piso", "presence"),
      slot("chela", "04", 1600, 893, "La Chela con auriculares", "support"),
      slot("chela", "05", 1600, 893, "La Chela en la escalera", "support"),
    ],
  },
];

export const bardera = queens.find((queen) => queen.id === "bardera")!;

export function getQueen(id: string): Queen | undefined {
  return queens.find((queen) => queen.id === id);
}
