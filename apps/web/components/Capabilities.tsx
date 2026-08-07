"use client";

interface Capability {
  title: string;
  desc: string;
  status: "implemented" | "prototype" | "planned";
  icon: React.ReactNode;
}

const ICONS = {
  identity: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <circle cx="12" cy="8" r="4" />
      <path d="M4 21c0-4 4-7 8-7s8 3 8 7" />
    </svg>
  ),
  memory: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M12 2v20M2 12h20M5 5l14 14M19 5L5 19" />
    </svg>
  ),
  chat: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
    </svg>
  ),
  audiovisual: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <rect x="2" y="4" width="20" height="14" rx="2" />
      <path d="M10 9l5 3-5 3z" />
    </svg>
  ),
  agent: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M12 2a3 3 0 0 0-3 3v1a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3z" />
      <path d="M5 12h14M12 8v8" />
    </svg>
  ),
  scene: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M3 7h18M3 12h18M3 17h18" />
    </svg>
  ),
};

const CAPABILITIES: Capability[] = [
  {
    title: "Identidad consistente",
    desc: "Una sola compañera con carácter definido: caótica, creativa, afectuosa sin ser sumisa.",
    status: "implemented",
    icon: ICONS.identity,
  },
  {
    title: "Chat en tiempo real",
    desc: "Conversación vía el backend FastAPI canónico con validación de salida.",
    status: "prototype",
    icon: ICONS.chat,
  },
  {
    title: "Arquitectura de memoria",
    desc: "Memoria persistente entre sesiones para recordar detalles y contexto.",
    status: "planned",
    icon: ICONS.memory,
  },
  {
    title: "Presencia audiovisual",
    desc: "Retrato, voz y escenas contextuales que enriquecen la presencia.",
    status: "planned",
    icon: ICONS.audiovisual,
  },
  {
    title: "Capacidades de agente",
    desc: "Tareas concretas y útiles más allá de la charla, sin perder identidad.",
    status: "planned",
    icon: ICONS.agent,
  },
  {
    title: "Escenas contextuales",
    desc: "Ambientes y momentos que dan contexto a la interacción.",
    status: "planned",
    icon: ICONS.scene,
  },
];

const LABELS: Record<Capability["status"], string> = {
  implemented: "Implementado",
  prototype: "Prototipo",
  planned: "Planificado",
};

export function Capabilities() {
  return (
    <section className="section" id="capabilities">
      <div className="section-inner">
        <span className="section-eyebrow glass">Capacidades</span>
        <h2>
          Lo que <span className="grad">es</span>, lo que viene
        </h2>
        <p className="lead">
          Transparencia primero. Esto es lo que Companion Studio tiene hoy y lo que está
          planificado. Sin métricas fabricadas, sin promesas vacías.
        </p>
        <div className="cap-grid">
          {CAPABILITIES.map((c) => (
            <div key={c.title} className="cap-card">
              <div className="cap-icon">{c.icon}</div>
              <h3>{c.title}</h3>
              <p>{c.desc}</p>
              <span className={`cap-badge ${c.status}`}>{LABELS[c.status]}</span>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
