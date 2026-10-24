"use client";

import { Database, Globe, Mail, MessageSquare } from "lucide-react";

interface Props {
  emailSync: boolean;
  setEmailSync: (v: boolean) => void;
  whatsappStatus: string;
  browserMode: "Headless" | "Headful";
  setBrowserMode: (v: "Headless" | "Headful") => void;
}

export function ControlPanel({
  emailSync,
  setEmailSync,
  whatsappStatus,
  browserMode,
  setBrowserMode,
}: Props) {
  return (
    <div className="flex flex-1 flex-col gap-3 overflow-y-auto pr-1">
      <div className="grid grid-cols-2 gap-3">
        <div className="glass-panel p-3">
          <h4 className="font-orbitron mb-2 flex items-center gap-2 text-xs text-cyber-cyan">
            <Mail size={14} /> Email Agent
          </h4>
          <div className="flex flex-col gap-2 font-mono text-xs">
            <div className="flex items-center justify-between rounded bg-slate-950/60 p-2">
              <span className="text-slate-400">Background Sync</span>
              <button
                onClick={() => setEmailSync(!emailSync)}
                className={`rounded px-2 py-0.5 text-[10px] font-bold ${
                  emailSync
                    ? "bg-emerald-500/20 text-emerald-400"
                    : "bg-slate-800 text-slate-500"
                }`}
              >
                {emailSync ? "ON" : "OFF"}
              </button>
            </div>
            <div className="flex items-center justify-between rounded bg-slate-950/60 p-2">
              <span className="text-slate-400">Priority Flags</span>
              <span className="text-slate-200">Enabled</span>
            </div>
          </div>
        </div>

        <div className="glass-panel p-3">
          <h4 className="font-orbitron mb-2 flex items-center gap-2 text-xs text-cyber-magenta">
            <MessageSquare size={14} /> Messaging Feeds
          </h4>
          <div className="flex flex-col gap-2 font-mono text-xs">
            <div className="flex items-center justify-between rounded bg-slate-950/60 p-2">
              <span className="text-slate-400">WhatsApp Status</span>
              <span className="text-slate-500">{whatsappStatus}</span>
            </div>
            <div className="flex items-center justify-between rounded bg-slate-950/60 p-2">
              <span className="text-slate-400">Teams Webhook</span>
              <span className="text-cyber-green">Active</span>
            </div>
          </div>
        </div>

        <div className="glass-panel p-3">
          <h4 className="font-orbitron mb-2 flex items-center gap-2 text-xs text-slate-300">
            <Globe size={14} /> Browser &amp; Vision
          </h4>
          <div className="flex flex-col gap-2 font-mono text-xs">
            <div className="flex items-center justify-between rounded bg-slate-950/60 p-2">
              <span className="text-slate-400">Playwright Engine</span>
              <button
                onClick={() =>
                  setBrowserMode(browserMode === "Headless" ? "Headful" : "Headless")
                }
                className="text-[10px] text-cyber-cyan hover:underline"
              >
                {browserMode}
              </button>
            </div>
            <div className="flex items-center justify-between rounded bg-slate-950/60 p-2">
              <span className="text-slate-400">Monitor Screen Capture</span>
              <span className="text-slate-200">Tesseract OCR Ready</span>
            </div>
          </div>
        </div>

        <div className="glass-panel p-3">
          <h4 className="font-orbitron mb-2 flex items-center gap-2 text-xs text-slate-300">
            <Database size={14} /> Graph Memory Visualizer
          </h4>
          <div className="flex flex-col gap-2 font-mono text-xs">
            <div className="flex items-center justify-between rounded bg-slate-950/60 p-2">
              <span className="text-slate-400">Neo4j Relationships</span>
              <span className="text-cyber-cyan">185 links active</span>
            </div>
            <div className="flex items-center justify-between rounded bg-slate-950/60 p-2">
              <span className="text-slate-400">Postgres Session DB</span>
              <span className="text-slate-200">Connected</span>
            </div>
          </div>
        </div>
      </div>

      <div className="glass-panel bg-slate-950/40 p-3 font-mono text-xs">
        <span className="font-bold text-cyber-cyan">SYSTEM TELEMETRY SUMMARY: </span>
        All agent nodes compiled. Speech synth pipelines mapped using ElevenLabs
        keys. Web browsers initialized on local loop. Press &ldquo;WAKE CORE&rdquo; to
        execute active queries.
      </div>
    </div>
  );
}
