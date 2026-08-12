"use client";

import { useSessionStore } from "@/stores/session";
import { Mic, MicOff, ChevronDown, Wifi, WifiOff } from "lucide-react";

interface Props {
  onCollapse?: () => void;
}

/** Voice status row — Voice Off/On, connection, collapse button. */
export function VoiceStatus({ onCollapse }: Props) {
  const connectionStatus = useSessionStore((s) => s.connectionStatus);
  const voiceOn = false; // TODO: Phase 3 — wire to real voice state

  return (
    <div className="flex items-center justify-between px-1 py-2">
      <div className="flex items-center gap-2">
        <button
          type="button"
          onClick={onCollapse}
          className="flex shrink-0 items-center justify-center rounded-lg p-2 text-[var(--color-text-dim)] hover:bg-[var(--color-surface-2)] hover:text-[var(--color-text)]"
          aria-label="Collapse chat"
        >
          <ChevronDown className="h-5 w-5" />
        </button>
        <div
          className={`h-2 w-2 shrink-0 rounded-full ${
            voiceOn ? "bg-[var(--color-success)]" : "bg-[var(--color-text-dim)]"
          }`}
        />
        <span className="text-xs text-[var(--color-text-dim)]">
          {voiceOn ? "Voice On" : "Voice Off"}
        </span>
      </div>

      <div className="flex items-center gap-2">
        {voiceOn ? (
          <Mic className="h-4 w-4 text-[var(--color-accent)]" />
        ) : (
          <MicOff className="h-4 w-4 text-[var(--color-text-dim)]" />
        )}
        <span
          className={`flex items-center gap-1 text-xs ${
            connectionStatus === "connected"
              ? "text-[var(--color-success)]"
              : "text-[var(--color-text-dim)]"
          }`}
        >
          {connectionStatus === "connected" ? (
            <Wifi className="h-3 w-3" />
          ) : (
            <WifiOff className="h-3 w-3" />
          )}
        </span>
      </div>
    </div>
  );
}
