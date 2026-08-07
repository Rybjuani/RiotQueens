"use client";

import { useState } from "react";

const CHOICES: [string, string, string[]][] = [
  ["personalidad", "¿Qué energía te atrae?", ["Caótica y divertida", "Serena y curiosa", "Intensa y creativa"]],
  ["dinamica", "¿Cómo querés que se sienta el vínculo?", ["Cómplice", "Coqueto", "Compañeros de proyecto"]],
  ["iniciativa", "¿Cuánto debería tomar la iniciativa?", ["Cuando se lo pida", "A veces sorprenderme", "Que proponga seguido"]],
  ["intensidad", "¿Qué nivel de romance preferís?", ["Suave", "Cercano", "Sensual, sin ser explícito"]],
  ["visual", "¿Qué estilo visual imaginás?", ["Cotidiano", "Cinematográfico", "Editorial"]],
];

export function Onboarding({ onComplete }: { onComplete: (answers: Record<string, string>) => void }) {
  const [step, setStep] = useState(0);
  const [answers, setAnswers] = useState<Record<string, string>>({});

  const choose = (value: string) => {
    const next = { ...answers, [CHOICES[step][0]]: value };
    setAnswers(next);
    if (step + 1 >= CHOICES.length) {
      onComplete(next);
    } else {
      setStep(step + 1);
    }
  };

  const [key, label, options] = CHOICES[step];

  return (
    <section className="section" id="onboarding">
      <div className="section-inner">
        <div className="onboarding-card glass-strong">
          <div className="progress">Decisión {step + 1} de 5</div>
          <h2>{label}</h2>
          <div className="options">
            {options.map((option) => (
              <button key={option} className="option-btn" onClick={() => choose(option)}>
                {option}
              </button>
            ))}
          </div>
          <p className="hint">Podés ajustar todo después. No hay respuestas incorrectas.</p>
        </div>
      </div>
    </section>
  );
}
