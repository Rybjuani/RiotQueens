"use client";

import { useState } from "react";
import { Navbar } from "@/components/Navbar";
import { Hero } from "@/components/Hero";
import { Onboarding } from "@/components/Onboarding";
import { ChatPanel } from "@/components/ChatPanel";
import { Capabilities } from "@/components/Capabilities";
import { Footer } from "@/components/Footer";

type Phase = "landing" | "onboarding" | "chat";

export default function Home() {
  const [phase, setPhase] = useState<Phase>("landing");
  const [answers, setAnswers] = useState<Record<string, string>>({});

  const scrollToOnboarding = () => {
    setPhase("onboarding");
    setTimeout(() => {
      document.getElementById("onboarding")?.scrollIntoView({ behavior: "smooth" });
    }, 50);
  };

  return (
    <div className="shell">
      <Navbar onCta={scrollToOnboarding} />
      <main>
        <Hero onStart={scrollToOnboarding} />

        {phase === "onboarding" && (
          <Onboarding
            onComplete={(a) => {
              setAnswers(a);
              setPhase("chat");
              setTimeout(() => {
                document.getElementById("chat")?.scrollIntoView({ behavior: "smooth" });
              }, 50);
            }}
          />
        )}

        {phase === "chat" && (
          <ChatPanel answers={answers} onEdit={() => setPhase("onboarding")} />
        )}

        <Capabilities />
      </main>
      <Footer />
    </div>
  );
}
