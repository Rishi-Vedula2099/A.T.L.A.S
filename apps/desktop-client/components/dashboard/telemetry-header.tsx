"use client";

import { Activity, Cpu } from "lucide-react";
import type { DbStatus } from "@/lib/types";

interface Props {
  dbStatus: DbStatus;
  latency: number;
  systemLoad: number;
  connected: boolean;
}

const DB_KEYS: { key: keyof DbStatus; label: string }[] = [
  { key: "postgres", label: "POSTGRES" },
  { key: "redis", label: "REDIS" },
  { key: "qdrant", label: "QDRANT" },
  { key: "neo4j", label: "NEO4J" },
];

export function TelemetryHeader({ dbStatus, latency, systemLoad, connected }: Props) {
  return (
    <header
      className="glass-panel mb-3 flex items-center justify-between"
      style={{ padding: "0.75rem 1.25rem" }}
    >
      <div className="flex items-center gap-3">
        <div
          className="voice-core"
          style={{ width: 10, height: 10, position: "relative", animation: "none" }}
        />
        <h1 className="font-orbitron text-lg font-bold tracking-widest text-cyber-cyan">
          A.T.L.A.S // CONTROL DECK
        </h1>
        <span
          className={`ml-2 text-[10px] font-mono ${
            connected ? "text-cyber-green" : "text-cyber-magenta"
          }`}
        >
          {connected ? "● LIVE" : "○ CONNECTING"}
        </span>
      </div>

      <div className="flex items-center gap-5 font-mono text-xs">
        {DB_KEYS.map(({ key, label }) => (
          <div key={key} className="flex items-center gap-1.5">
            <span
              className={`status-dot ${
                dbStatus[key] ? "status-dot-green" : "status-dot-red"
              }`}
            />
            <span className="text-slate-400">{label}</span>
          </div>
        ))}
        <div className="h-4 w-px bg-slate-800" />
        <div className="flex items-center gap-1 text-slate-400">
          <Activity size={12} className="text-cyber-magenta" />
          <span>LATENCY: {latency}ms</span>
        </div>
        <div className="flex items-center gap-1 text-slate-400">
          <Cpu size={12} className="text-cyber-cyan" />
          <span>LOAD: {systemLoad}%</span>
        </div>
      </div>
    </header>
  );
}
