"use client";

import { useState } from "react";
import { CheckCircle } from "lucide-react";
import { AGENTS } from "@/lib/agents";

export function AgentInspector() {
  const [active, setActive] = useState<string>("orchestrator");
  const activeAgent = AGENTS.find((a) => a.key === active) ?? AGENTS[0];
  const ActiveIcon = activeAgent.icon;

  return (
    <>
      <div className="grid grid-cols-4 gap-2">
        {AGENTS.map((agent) => {
          const Icon = agent.icon;
          const isActive = active === agent.key;
          return (
            <button
              key={agent.key}
              onClick={() => setActive(agent.key)}
              className={`glass-panel cursor-pointer p-3 text-left transition-all ${
                isActive ? "border-cyber-cyan bg-[#0c1421]" : "hover:border-slate-700"
              }`}
            >
              <div className="mb-2 flex items-center justify-between">
                <div
                  className={`rounded p-1.5 ${
                    isActive ? "text-cyber-cyan" : "text-slate-400"
                  }`}
                >
                  <Icon size={16} />
                </div>
              </div>
              <h3 className="mb-1 text-xs font-bold text-slate-200">
                {agent.name}
              </h3>
              <p className="line-clamp-2 font-mono text-[10px] leading-normal text-slate-400">
                {agent.desc}
              </p>
            </button>
          );
        })}
      </div>

      <div className="glass-panel bg-[#05080c] mt-3 flex flex-1 flex-col justify-between p-4">
        <div>
          <div className="mb-3 flex items-center gap-3 border-b border-slate-800 pb-2">
            <div className="rounded bg-slate-950 p-2 text-cyber-cyan">
              <ActiveIcon size={20} />
            </div>
            <div>
              <h2 className="font-orbitron text-sm font-bold text-slate-200">
                {activeAgent.name}
              </h2>
              <p className="text-xs text-slate-400">{activeAgent.desc}</p>
            </div>
          </div>

          <div className="mb-3 grid grid-cols-3 gap-3">
            {Object.entries(activeAgent.stats).map(([k, v]) => (
              <div
                key={k}
                className="flex flex-col rounded border border-white/[0.02] bg-[#090d16] p-2.5 font-mono"
              >
                <span className="mb-0.5 text-[9px] uppercase tracking-wider text-cyber-magenta">
                  {k}
                </span>
                <span className="text-xs font-semibold text-slate-200">{v}</span>
              </div>
            ))}
          </div>

          <div className="rounded border border-white/[0.01] bg-[#03060a] p-3">
            <h4 className="font-orbitron mb-1 text-xs uppercase tracking-wider text-cyber-cyan">
              Functional Capabilities
            </h4>
            <p className="font-mono text-xs leading-relaxed text-slate-300">
              {activeAgent.details}
            </p>
          </div>
        </div>

        <div className="flex items-center justify-between border-t border-slate-800 pt-2 font-mono text-[10px] text-slate-500">
          <span>NODE SCHEMA: active_system_agent</span>
          <span className="flex items-center gap-1 text-cyber-green">
            <CheckCircle size={10} /> LINK VERIFIED
          </span>
        </div>
      </div>
    </>
  );
}
