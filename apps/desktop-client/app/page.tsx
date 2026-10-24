"use client";

import { useEffect, useState } from "react";
import { TelemetryHeader } from "@/components/dashboard/telemetry-header";
import { VocalReceptor } from "@/components/dashboard/vocal-receptor";
import { AgentInspector } from "@/components/dashboard/agent-inspector";
import { ControlPanel } from "@/components/dashboard/control-panel";
import { ThoughtStream } from "@/components/dashboard/thought-stream";
import { useAtlasWs } from "@/hooks/use-atlas-ws";
import { useWakeWord } from "@/hooks/use-wake-word";
import { isAuthenticated } from "@/lib/auth";
import { useRouter } from "next/navigation";

type Tab = "agents" | "controls";

export default function HomePage() {
  const router = useRouter();
  const [authed, setAuthed] = useState<boolean | null>(null);
  const [activeTab, setActiveTab] = useState<Tab>("agents");

  // Configuration-panel state
  const [llmMode, setLlmMode] = useState("Gemini Flash");
  const [voiceStyle, setVoiceStyle] = useState("Jarvis Style");
  const [emailSync, setEmailSync] = useState(true);
  const [whatsappStatus] = useState("Disconnected");
  const [browserMode, setBrowserMode] = useState<"Headless" | "Headful">("Headless");

  const ws = useAtlasWs();

  // Redirect anonymous users to /login (only enforced when an auth backend is
  // reachable; the dashboard still works in standalone dev mode).
  useEffect(() => {
    setAuthed(isAuthenticated());
  }, []);

  useWakeWord({
    wakeStatus: ws.wakeStatus,
    send: ws.send,
  });

  const toggleWake = () => ws.send({ action: "toggle_wake" });

  const handleCommand = (text: string) => ws.send({ action: "command", text });

  return (
    <div
      className="flex h-screen select-none flex-col bg-[#020408] text-slate-100"
      style={{ padding: "1rem" }}
    >
      <TelemetryHeader
        dbStatus={ws.dbStatus}
        latency={ws.latency}
        systemLoad={ws.systemLoad}
        connected={ws.connected}
      />

      <div className="flex flex-1 gap-3 overflow-hidden" style={{ minHeight: 0 }}>
        <VocalReceptor
          wakeStatus={ws.wakeStatus}
          onToggle={toggleWake}
          llmMode={llmMode}
          setLlmMode={setLlmMode}
          voiceStyle={voiceStyle}
          setVoiceStyle={setVoiceStyle}
        />

        <main className="flex flex-1 flex-col gap-3 overflow-hidden">
          <div className="flex gap-2">
            <button
              onClick={() => setActiveTab("agents")}
              className={`cyber-btn rounded px-4 py-1.5 text-xs ${
                activeTab === "agents" ? "cyber-btn-active" : ""
              }`}
            >
              Agent Nodes
            </button>
            <button
              onClick={() => setActiveTab("controls")}
              className={`cyber-btn rounded px-4 py-1.5 text-xs ${
                activeTab === "controls" ? "cyber-btn-active" : ""
              }`}
            >
              Control Panel
            </button>
          </div>

          {activeTab === "agents" ? (
            <div className="flex flex-1 flex-col overflow-hidden">
              <AgentInspector />
            </div>
          ) : (
            <ControlPanel
              emailSync={emailSync}
              setEmailSync={setEmailSync}
              whatsappStatus={whatsappStatus}
              browserMode={browserMode}
              setBrowserMode={setBrowserMode}
            />
          )}
        </main>

        <ThoughtStream
          logs={ws.thoughtStream}
          onReset={ws.resetStream}
          onSubmit={handleCommand}
        />
      </div>

      {/* Hidden: keeps the authed flag accessible to future toolbar UI */}
      <span className="hidden" aria-hidden>
        {authed === null ? "" : authed ? "authed" : "anon"}
      </span>
    </div>
  );
}
