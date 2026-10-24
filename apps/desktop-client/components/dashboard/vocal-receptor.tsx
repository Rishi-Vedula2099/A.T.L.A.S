"use client";

import { Settings } from "lucide-react";
import type { WakeStatus } from "@/lib/types";

interface Props {
  wakeStatus: WakeStatus;
  onToggle: () => void;
  llmMode: string;
  setLlmMode: (v: string) => void;
  voiceStyle: string;
  setVoiceStyle: (v: string) => void;
}

export function VocalReceptor({
  wakeStatus,
  onToggle,
  llmMode,
  setLlmMode,
  voiceStyle,
  setVoiceStyle,
}: Props) {
  return (
    <aside className="flex w-1/4 flex-col gap-3">
      <div className="glass-panel flex flex-1 flex-col items-center justify-center p-4 text-center">
        <h2 className="font-orbitron mb-4 text-xs uppercase tracking-widest text-cyber-cyan">
          Vocal Receptor
        </h2>

        <div className="relative mb-6 flex items-center justify-center">
          <div className="hologram-ring">
            <div className="voice-core" />
          </div>
        </div>

        <div className="mb-4 flex flex-col gap-1">
          <span className="text-sm font-semibold tracking-wide text-slate-200">
            WAKE CORE STATUS: {wakeStatus}
          </span>
          <span className="font-mono text-xs text-slate-400">
            {wakeStatus === "Listening" && 'Access: "Hey Atlas"'}
            {wakeStatus === "Processing" && "Resolving Neural Graph..."}
            {wakeStatus === "Sleeping" && "System Suspended"}
          </span>
        </div>

        <button
          onClick={onToggle}
          className={`cyber-btn rounded px-6 py-2 text-xs ${
            wakeStatus === "Sleeping" ? "cyber-btn-secondary" : ""
          }`}
        >
          {wakeStatus === "Sleeping" ? "ACTIVATE CORE" : "SLEEP SYSTEM"}
        </button>
      </div>

      <div className="glass-panel p-3">
        <h3 className="font-orbitron mb-3 flex items-center gap-1.5 text-xs uppercase text-slate-300">
          <Settings size={14} className="text-cyber-cyan" />
          Interface Settings
        </h3>

        <div className="flex flex-col gap-2 font-mono text-xs">
          <label className="flex flex-col gap-1">
            <span className="text-[10px] text-slate-400">LLM LAYER ENGINE</span>
            <select
              value={llmMode}
              onChange={(e) => setLlmMode(e.target.value)}
              className="cyber-input p-1.5 text-xs focus:outline-none"
            >
              <option>Gemini Flash</option>
              <option>Claude Sonnet</option>
              <option>GPT-4o</option>
              <option>Ollama Local</option>
            </select>
          </label>

          <label className="mt-1 flex flex-col gap-1">
            <span className="text-[10px] text-slate-400">VOICE SYNTH CLONE</span>
            <select
              value={voiceStyle}
              onChange={(e) => setVoiceStyle(e.target.value)}
              className="cyber-input p-1.5 text-xs focus:outline-none"
            >
              <option>Jarvis Style</option>
              <option>Friday Style</option>
              <option>Professional</option>
              <option>Friendly</option>
            </select>
          </label>

          <div className="mt-2 flex items-center justify-between border-t border-slate-800 pt-2">
            <span className="text-slate-400">Local LLM Mode</span>
            <span
              className={`text-[10px] ${
                llmMode === "Ollama Local" ? "text-cyber-green" : "text-slate-500"
              }`}
            >
              {llmMode === "Ollama Local" ? "ACTIVE" : "OFFLINE"}
            </span>
          </div>
        </div>
      </div>
    </aside>
  );
}
