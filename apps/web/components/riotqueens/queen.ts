/**
 * Frontend Queen registry for presence, galleries, profiles, and chat.
 *
 * Backend runtime still owns prompts and only registers `bardera` today.
 * Memory and conversation scopes are always keyed by character_id on the
 * server: Queens never share memory with each other.
 *
 * Profile decks (NotebookLM / Flow) are identity manuals for users — not
 * the system prompt, not shared memory, and not required for chat.
 *
 * NOTE: GLM redesign — public previews under /queens/<id>/0N.jpg remain the
 * canonical allowlisted derivatives (config/public-media.json). DO NOT
 * publish masters from assets/private/selected/.
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
  short: string; // short name for compact UI
  tagline: string; // canonical RiotQueens voice
  essence: string; // one-line differential — for the queen card body
  status: "live" | "curation";
  /** Only live Queens may open the real chat against the API. */
  chatEnabled: boolean;
  /** Portrait used by ChatPanel / compact presence. */
  portrait: string;
  /** Featured photo for the roster card (4:5 aspect). */
  card: string;
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
    short: "BARDERA",
    tagline: "TE BARDEA. TE QUIERE. SE QUEDA.",
    essence:
      "Punk del oeste, 24 años. Timing, sinceridad, ingenio y bardeo afectivo. No te clava el visto. No te ghostea.",
    status: "live",
    chatEnabled: true,
    portrait: "/queens/bardera/02.jpg",
    card: "/queens/bardera/03.jpg",
    quickPrompts: [
      "Necesito una segunda opinión",
      "Te cuento algo que me pasó hoy",
      "Ayudame a ordenar una idea",
    ],
    slots: [
      slot("bardera", "01", 1600, 900, "La Bardera en su setup creativo", "hero"),
      slot("bardera", "02", 1600, 893, "La Bardera en su cuarto", "chat"),
      slot("bardera", "03", 1600, 893, "La Bardera en su cuarto punk", "support"),
      slot("bardera", "04", 720, 1280, "La Bardera, variante vertical", "presence"),
      slot("bardera", "05", 896, 1152, "La Bardera, variante provisional", "presence"),
    ],
  },
  {
    id: "toxica",
    name: "La Tóxica Consciente",
    short: "TÓXICA",
    tagline: "Te hace quilombo con método.",
    essence:
      "Intensidad y celos autoconscientes, cómicos y reparables. TeOpera, te incomoda, te hace pensar. Pronto.",
    status: "curation",
    chatEnabled: false,
    portrait: "/queens/toxica/01.jpg",
    card: "/queens/toxica/03.jpg",
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
    short: "GEDE",
    tagline: "Cuidado, hambre y aguante.",
    essence:
      "Cuidado mediante comida y hambre como motor contextual. Te alimenta el alma y la panza. Pronto.",
    status: "curation",
    chatEnabled: false,
    portrait: "/queens/gede/04.jpg",
    card: "/queens/gede/01.jpg",
    quickPrompts: [],
    slots: [
      slot("gede", "01", 1600, 893, "La Gede en su cuarto", "presence"),
      slot("gede", "02", 1600, 893, "La Gede en la cama", "presence"),
      slot("gede", "03", 1600, 893, "La Gede en el piso", "support"),
      slot("gede", "04", 900, 1600, "La Gede, retrato vertical", "chat"),
      slot("gede", "05", 1600, 893, "La Gede, variante punk", "support"),
    ],
  },
  {
    id: "rocha",
    name: "La Rocha",
    short: "ROCHA",
    tagline: "Directa, callejera, con aguante.",
    essence:
      "Registro más callejero, directo y reactivo. Ternura menos visible. Sale al escenario cuando esté lista.",
    status: "curation",
    chatEnabled: false,
    portrait: "/queens/rocha/01.jpg",
    card: "/queens/rocha/01.jpg",
    quickPrompts: [],
    slots: [
      slot("rocha", "01", 914, 1600, "La Rocha, sonrisa de presencia", "chat"),
      slot("rocha", "02", 1448, 1086, "La Rocha, retrato frontal", "hero"),
    ],
  },
  {
    id: "chela",
    name: "La Chela",
    short: "CHELA",
    tagline: "Ritmo, birra y compañía.",
    essence:
      "Relajación, birra y descompresión. Sin convertirse en catálogo de alcohol. Pronto.",
    status: "curation",
    chatEnabled: false,
    portrait: "/queens/chela/01.jpg",
    card: "/queens/chela/02.jpg",
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
