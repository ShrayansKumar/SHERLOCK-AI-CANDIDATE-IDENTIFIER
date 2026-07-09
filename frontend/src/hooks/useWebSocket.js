import { useEffect, useRef, useState, useCallback } from "react";

const host = typeof window !== "undefined" && window.location.hostname ? window.location.hostname : "localhost";
const WS_URL = `ws://${host}:8000/ws`;

/**
 * useWebSocket - connects to the Sherlock AI WebSocket and dispatches
 * incoming confidence/evidence/transcript/upload events to caller-provided handlers.
 *
 * @param {object} handlers  - { onConfidence, onEvidence, onTranscript, onRaw }
 * @param {boolean} enabled  - set false to keep socket closed
 */
export default function useWebSocket(handlers = {}, enabled = true) {
  const wsRef = useRef(null);
  const [connected, setConnected] = useState(false);
  const [lastEvent, setLastEvent] = useState(null);
  const handlersRef = useRef(handlers);

  useEffect(() => {
    handlersRef.current = handlers;
  });

  const connect = useCallback(() => {
    if (wsRef.current) return;

    const ws = new WebSocket(WS_URL);
    wsRef.current = ws;

    ws.onopen = () => setConnected(true);

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        setLastEvent(data);

        const { onConfidence, onEvidence, onTranscript, onRaw } =
          handlersRef.current;

        const type = String(data.type || data.event_type || "").toLowerCase();

        // 1. Confidence updates
        if (
          type.includes("confidence") ||
          data.confidence !== undefined ||
          type.includes("upload")
        ) {
          onConfidence?.(data);
        }

        // 2. Evidence updates
        if (
          type.includes("evidence") ||
          type.includes("explanation") ||
          data.evidence_type !== undefined ||
          type.includes("confidence") ||
          type.includes("upload")
        ) {
          onEvidence?.(data);
        }

        // 3. Transcript updates
        if (
          type.includes("transcript") ||
          data.transcript !== undefined ||
          type.includes("audio")
        ) {
          onTranscript?.(data);
        }

        onRaw?.(data);
      } catch {
        // Non-JSON pings — ignore
      }
    };

    ws.onclose = () => {
      setConnected(false);
      wsRef.current = null;
      setTimeout(() => {
        if (enabled) connect();
      }, 3000);
    };

    ws.onerror = () => ws.close();
  }, [enabled]);

  const disconnect = useCallback(() => {
    wsRef.current?.close();
    wsRef.current = null;
    setConnected(false);
  }, []);

  useEffect(() => {
    if (enabled) {
      connect();
    } else {
      disconnect();
    }
    return () => {
      wsRef.current?.close();
      wsRef.current = null;
    };
  }, [enabled, connect, disconnect]);

  return { connected, lastEvent };
}
