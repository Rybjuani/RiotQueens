"use client";

import { useState } from "react";

const choices = [
  ["personalidad", "¿Qué energía te atrae?", ["Caótica y divertida", "Serena y curiosa", "Intensa y creativa"]],
  ["dinamica", "¿Cómo querés que se sienta el vínculo?", ["Cómplice", "Coqueto", "Compañeros de proyecto"]],
  ["iniciativa", "¿Cuánto debería tomar la iniciativa?", ["Cuando se lo pida", "A veces sorprenderme", "Que proponga seguido"]],
  ["intensidad", "¿Qué nivel de romance preferís?", ["Suave", "Cercano", "Sensual, sin ser explícito"]],
  ["visual", "¿Qué estilo visual imaginás?", ["Cotidiano", "Cinematográfico", "Editorial"]],
];

export default function Home() {
  const [step, setStep] = useState(0);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [message, setMessage] = useState("");
  const [reply, setReply] = useState("Todavía no hay mensajes.");
  const choose = (value: string) => {
    setAnswers({ ...answers, [choices[step][0] as string]: value });
    setStep(step + 1);
  };
  const send = async () => {
    if (!message.trim()) return;
    const api = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
    const response = await fetch(`${api}/v1/chat`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ message }) });
    const data = await response.json();
    setReply(data.response.content);
    setMessage("");
  };
  const confirmed = step >= choices.length;
  return <main className="shell">
    <header><span className="eyebrow">COMPANION STUDIO · PROTOTIPO</span><h1>Una presencia con carácter.</h1><p>Precisión profunda para quien la busca. Simplicidad absoluta para quien solo quiere empezar.</p></header>
    {!confirmed ? <section className="card" aria-labelledby="onboarding-title">
      <div className="progress">Decisión {step + 1} de 5</div><h2 id="onboarding-title">{choices[step][1]}</h2>
      <div className="options">{(choices[step][2] as string[]).map((option) => <button key={option} onClick={() => choose(option)}>{option}</button>)}</div>
      <p className="hint">Podés ajustar todo después. No hay respuestas incorrectas.</p>
    </section> : <section className="grid">
      <div className="card"><div className="progress">Tu punto de partida</div><h2>Así podría sentirse</h2><p>Una compañera adulta, creativa y con iniciativa medida. El perfil es editable y queda separado de los ajustes temporales.</p><dl>{Object.entries(answers).map(([key, value]) => <div key={key}><dt>{key}</dt><dd>{value}</dd></div>)}</dl><button className="secondary" onClick={() => setStep(0)}>Volver y editar</button></div>
      <div className="card chat"><div className="progress">CHAT DE PRUEBA · PROVIDER: MOCK</div><div className="bubble assistant">{reply}</div><div className="composer"><input aria-label="Mensaje" value={message} onChange={(event) => setMessage(event.target.value)} onKeyDown={(event) => event.key === "Enter" && send()} placeholder="Escribile algo..." /><button onClick={send}>Enviar</button></div><p className="dev">Desarrollo: la validación de salida está activa en la API.</p><div className="media">▣ Video enviado · placeholder · no generado en vivo</div></div>
    </section>}
  </main>;
}
