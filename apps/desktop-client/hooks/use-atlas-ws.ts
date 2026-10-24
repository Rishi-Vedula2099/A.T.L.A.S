"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import { getAccessToken } from "@/lib/auth";
import type {
  DbStatus,
  ThoughtLog,
  WakeStatus,
  WsPayload,
  OutboundMessage,
} from "@/lib/types";

const WS_URL = process.env.NEXT_PUBLIC_WS_URL ?? "ws://localhost:8000/ws";

const INITIAL_DB: DbStatus = {
  postgres: false,
  redis: false,
  qdrant: false,
  neo4j: false,
};

const INITIAL_LOGS: ThoughtLog[] = [
  { time: "00:00:01", type: "system", message: "A.T.L.A.S Core OS v0.9.5 online." },
  { time: "00:00:02", type: "db",     message: "PostgreSQL: Link initialized." },
  { time: "00:00:02", type: "agent",  message: 'Ready for phrase activation. Wake phrase: "Hey Atlas"' },
];

export interface AtlasWsState {
  wakeStatus: WakeStatus;
  latency: number;
  systemLoad: number;
  dbStatus: DbStatus;
  thoughtStream: ThoughtLog[];
  connected: boolean;
  send: (msg: OutboundMessage) => void;
  resetStream: () => void;
}

export function useAtlasWs(): AtlasWsState {
  const [wakeStatus, setWakeStatus] = useState<WakeStatus>("Listening");
  const [latency, setLatency] = useState(12);
  const [systemLoad, setSystemLoad] = useState(24);
  const [dbStatus, setDbStatus] = useState<DbStatus>(INITIAL_DB);
  const [thoughtStream, setThoughtStream] = useState<ThoughtLog[]>(INITIAL_LOGS);
  const [connected, setConnected] = useState(false);

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  const connect = useCallback(() => {
    // Append access token if available (anonymous still works during scaffolding).
    const token = getAccessToken();
    const url = token ? `${WS_URL}?token=${encodeURIComponent(token)}` : WS_URL;

    let socket: WebSocket;
    try {
      socket = new WebSocket(url);
    } catch (err) {
      console.error("[WS] construction failed", err);
      return;
    }
    wsRef.current = socket;

    socket.onopen = () => setConnected(true);

    socket.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data) as WsPayload;
        if (payload.type === "telemetry") {
          setWakeStatus(payload.wakeStatus);
          setLatency(payload.latency);
          setSystemLoad(payload.load);
          if (payload.dbs) setDbStatus(payload.dbs);
        } else if (payload.type === "log") {
          setThoughtStream((prev) => [...prev, payload.log]);
        }
      } catch (err) {
        console.error("[WS] failed to parse message", err);
      }
    };

    socket.onclose = () => {
      setConnected(false);
      // Reconnect with backoff
      reconnectTimer.current = setTimeout(connect, 3000);
    };

    socket.onerror = (err) => {
      console.error("[WS] error", err);
    };
  }, []);

  useEffect(() => {
    connect();
    return () => {
      if (reconnectTimer.current) clearTimeout(reconnectTimer.current);
      wsRef.current?.close();
    };
  }, [connect]);

  const send = useCallback((msg: OutboundMessage) => {
    const socket = wsRef.current;
    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify(msg));
    }
  }, []);

  const resetStream = useCallback(() => {
    setThoughtStream([
      {
        time: new Date().toLocaleTimeString("en-US", { hour12: false }),
        type: "system",
        message: "Thought Stream Reset.",
      },
    ]);
  }, []);

  return {
    wakeStatus,
    latency,
    systemLoad,
    dbStatus,
    thoughtStream,
    connected,
    send,
    resetStream,
  };
}
