"use client";

import { useEffect, useRef } from "react";
import type { OutboundMessage, WakeStatus } from "@/lib/types";

// Minimal type stub — webkitSpeechRecognition isn't in TS DOM lib by default.
type SpeechRecognitionLike = {
  continuous: boolean;
  interimResults: boolean;
  lang: string;
  onresult: ((event: any) => void) | null;
  onerror: ((event: any) => void) | null;
  onend: (() => void) | null;
  start: () => void;
  stop: () => void;
};

interface UseWakeWordArgs {
  wakeStatus: WakeStatus;
  send: (msg: OutboundMessage) => void;
  onLog?: (log: { type: "system"; message: string }) => void;
}

/**
 * Browser-native SpeechRecognition wake-word listener.
 * Detects "Hey Atlas" → captures the trailing command and sends it over WS.
 * When processing, "Sleep Atlas" deactivates the core.
 */
export function useWakeWord({ wakeStatus, send, onLog }: UseWakeWordArgs) {
  const recognitionRef = useRef<SpeechRecognitionLike | null>(null);

  useEffect(() => {
    if (typeof window === "undefined") return;

    const SR =
      (window as any).SpeechRecognition ||
      (window as any).webkitSpeechRecognition;
    if (!SR) {
      console.warn("[Voice] SpeechRecognition not supported in this browser.");
      return;
    }

    const rec: SpeechRecognitionLike = new SR();
    rec.continuous = true;
    rec.interimResults = false;
    rec.lang = "en-US";

    rec.onresult = (event: any) => {
      const transcript: string = event.results[event.results.length - 1][0].transcript
        .trim()
        .toLowerCase();
      console.log("[Voice] transcribed:", transcript);

      if (wakeStatus === "Listening") {
        if (transcript.includes("hey atlas")) {
          let command = "";
          const idx = transcript.indexOf("atlas");
          if (idx !== -1) command = transcript.substring(idx + 5).trim();

          onLog?.({
            type: "system",
            message: 'Wake word triggered: "Hey Atlas" detected.',
          });

          if (command) {
            onLog?.({
              type: "system",
              message: `Voice command parsed: "${command}"`,
            });
            send({ action: "command", text: command });
          } else {
            send({ action: "command", text: "Vocal core ping check" });
          }
        }
      } else if (wakeStatus === "Processing") {
        if (transcript.includes("sleep atlas")) {
          send({ action: "toggle_wake" });
        }
      }
    };

    rec.onerror = (event: any) => {
      console.error("[Voice] error", event.error);
    };

    rec.onend = () => {
      if (wakeStatus !== "Sleeping" && recognitionRef.current) {
        try {
          recognitionRef.current.start();
        } catch (e) {
          console.error("[Voice] failed to restart", e);
        }
      }
    };

    recognitionRef.current = rec;

    if (wakeStatus !== "Sleeping") {
      try {
        rec.start();
        console.log("[Voice] continuous listening started");
      } catch (e) {
        console.error("[Voice] failed to start", e);
      }
    }

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.onend = null;
        try {
          recognitionRef.current.stop();
        } catch {
          // ignore
        }
      }
    };
  }, [wakeStatus, send, onLog]);
}
