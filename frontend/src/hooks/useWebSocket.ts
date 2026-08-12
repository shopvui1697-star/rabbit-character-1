"use client";

import { useCallback, useEffect, useRef } from "react";
import { WS_URL, MAX_RECONNECT_ATTEMPTS, RECONNECT_DELAY_MS } from "@/lib/constants";
import type { ClientMessage, ServerMessage } from "@/lib/ws-protocol";
import { useSessionStore } from "@/stores/session";

export function useWebSocket() {
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectCount = useRef(0);

  const setConnectionStatus = useSessionStore((s) => s.setConnectionStatus);
  const setAgentStatus = useSessionStore((s) => s.setAgentStatus);
  const addMessage = useSessionStore((s) => s.addMessage);
  const updateLastAssistantMessage = useSessionStore(
    (s) => s.updateLastAssistantMessage
  );
  const setCurrentUIActions = useSessionStore((s) => s.setCurrentUIActions);
  const setCurrentSuggestions = useSessionStore((s) => s.setCurrentSuggestions);

  const handleMessage = useCallback(
    (event: MessageEvent) => {
      try {
        const msg: ServerMessage = JSON.parse(event.data);

        switch (msg.type) {
          case "voice_response":
            addMessage({
              id: crypto.randomUUID(),
              role: "assistant",
              text: msg.data.text,
              timestamp: Date.now(),
            });
            break;

          case "ui_update":
            setCurrentUIActions(msg.data.actions);
            updateLastAssistantMessage({ uiActions: msg.data.actions });
            break;

          case "suggestions":
            setCurrentSuggestions(msg.data.chips);
            updateLastAssistantMessage({ suggestions: msg.data.chips });
            break;

          case "status":
            setAgentStatus(msg.data.state);
            break;

          case "error":
            console.error("Server error:", msg.data.message);
            break;
        }
      } catch (err) {
        console.error("Failed to parse WS message:", err);
      }
    },
    [
      addMessage,
      updateLastAssistantMessage,
      setCurrentUIActions,
      setCurrentSuggestions,
      setAgentStatus,
    ]
  );

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    setConnectionStatus("connecting");
    const ws = new WebSocket(WS_URL);
    wsRef.current = ws;

    ws.onopen = () => {
      setConnectionStatus("connected");
      reconnectCount.current = 0;
    };

    ws.onmessage = handleMessage;

    ws.onclose = () => {
      setConnectionStatus("disconnected");
      wsRef.current = null;

      // Auto-reconnect
      if (reconnectCount.current < MAX_RECONNECT_ATTEMPTS) {
        reconnectCount.current += 1;
        setTimeout(connect, RECONNECT_DELAY_MS);
      }
    };

    ws.onerror = () => {
      ws.close();
    };
  }, [setConnectionStatus, handleMessage]);

  useEffect(() => {
    connect();
    return () => {
      wsRef.current?.close();
    };
  }, [connect]);

  const send = useCallback((message: ClientMessage) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    }
  }, []);

  const sendText = useCallback(
    (text: string) => {
      send({ type: "text_input", data: { text } });
      addMessage({
        id: crypto.randomUUID(),
        role: "user",
        text,
        timestamp: Date.now(),
      });
    },
    [send, addMessage]
  );

  const selectChip = useCallback(
    (chip: string) => {
      send({ type: "chip_selected", data: { chip } });
      addMessage({
        id: crypto.randomUUID(),
        role: "user",
        text: chip,
        timestamp: Date.now(),
      });
    },
    [send, addMessage]
  );

  return { sendText, selectChip, send };
}
