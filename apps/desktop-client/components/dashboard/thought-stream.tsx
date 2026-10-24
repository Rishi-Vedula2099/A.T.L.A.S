"use client";

import { useEffect, useRef, useState } from "react";
import { RefreshCw, Send, Paperclip, Terminal } from "lucide-react";
import type { ThoughtLog } from "@/lib/types";

interface Props {
  logs: ThoughtLog[];
  onReset: () => void;
  onSubmit: (text: string) => void;
}

const STYLES: Record<ThoughtLog["type"], { color: string; prefix: string }> = {
  system: { color: "text-slate-400", prefix: "[SYS]" },
  db: { color: "text-cyber-green", prefix: "[DB ]" },
  agent: { color: "text-cyber-cyan", prefix: "[AGT]" },
  user: { color: "text-cyber-magenta font-semibold", prefix: "[USR]" },
};

export function ThoughtStream({ logs, onReset, onSubmit }: Props) {
  const [input, setInput] = useState("");
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [logs]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;
    onSubmit(input);
    setInput("");
  };

  return (
    <section className="glass-panel bg-[#03060a] flex w-1/3 flex-col overflow-hidden">
      <header className="flex items-center justify-between border-b border-slate-800 bg-slate-950 p-3">
        <div className="flex items-center gap-2">
          <Terminal size={14} className="text-cyber-cyan" />
          <span className="font-orbitron text-xs text-slate-300">
            Orchestrator Thought Stream
          </span>
        </div>
        <button
          onClick={onReset}
          className="rounded p-1 text-slate-500 transition-colors hover:bg-slate-900 hover:text-slate-300"
        >
          <RefreshCw size={11} />
        </button>
      </header>

      <div className="flex flex-1 flex-col gap-2 overflow-y-auto bg-[#020408]/90 p-3 font-mono text-xs">
        {logs.map((log, i) => {
          const style = STYLES[log.type];
          return (
            <div
              key={i}
              className="flex items-start gap-2 text-[11px] leading-normal"
            >
              <span className="flex-shrink-0 text-slate-600">{log.time}</span>
              <span className={`flex-shrink-0 ${style.color}`}>{style.prefix}</span>
              <span
                className={`whitespace-pre-wrap ${
                  log.type === "user" ? "text-slate-200" : "text-slate-300"
                }`}
              >
                {log.message}
              </span>
            </div>
          );
        })}
        <div ref={endRef} />
      </div>

      <form
        onSubmit={handleSubmit}
        className="flex items-center gap-2 border-t border-slate-800 bg-slate-950 p-3"
      >
        <Paperclip size={14} className="cursor-pointer text-slate-500 hover:text-slate-300" />
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Inject command or request to ATLAS..."
          className="cyber-input flex-1 border-0 px-2 py-1 text-xs text-slate-200 outline-none placeholder:text-slate-700"
        />
        <button type="submit" className="cyber-btn rounded p-1.5" style={{ minWidth: 32 }}>
          <Send size={12} />
        </button>
      </form>
    </section>
  );
}
