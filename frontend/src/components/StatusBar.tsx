"use client";

import { useSessionStore } from "@/stores/session";
import { Wifi, WifiOff, Loader2 } from "lucide-react";

export function StatusBar() {
  const connectionStatus = useSessionStore((s) => s.connectionStatus);
  const agentStatus = useSessionStore((s) => s.agentStatus);

  return (
    <header className="flex h-12 items-center justify-between border-b border-[var(--color-border)] bg-[var(--color-surface)] px-4">
      <div className="flex items-center gap-2">
        <span className="text-lg font-bold text-[var(--color-accent)]">
          🐰 Rabbit3
        </span>
      </div>

      <div className="flex items-center gap-4 text-xs">
        {/* Agent status */}
        {agentStatus === "thinking" && (
          <span className="flex items-center gap-1.5 text-[var(--color-accent)]">
            <Loader2 className="h-3 w-3 animate-spin" />
            Thinking…
          </span>
        )}

        {/* Connection indicator */}
        <span
          className={`flex items-center gap-1.5 ${
            connectionStatus === "connected"
              ? "text-[var(--color-success)]"
              : connectionStatus === "connecting"
                ? "text-yellow-400"
                : "text-[var(--color-error)]"
          }`}
        >
          {connectionStatus === "connected" ? (
            <Wifi className="h-3 w-3" />
          ) : (
            <WifiOff className="h-3 w-3" />
          )}
          {connectionStatus}
        </span>
      </div>
    </header>
  );
}
