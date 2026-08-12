"use client";

import { useState, useRef, type FormEvent, type KeyboardEvent } from "react";
import { Send } from "lucide-react";
import { useSessionStore } from "@/stores/session";

interface Props {
  onSend: (text: string) => void;
}

export function ChatInput({ onSend }: Props) {
  const [text, setText] = useState("");
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const connectionStatus = useSessionStore((s) => s.connectionStatus);
  const agentStatus = useSessionStore((s) => s.agentStatus);

  const disabled = connectionStatus !== "connected" || agentStatus === "thinking";

  const handleSubmit = (e?: FormEvent) => {
    e?.preventDefault();
    const trimmed = text.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed);
    setText("");
    inputRef.current?.focus();
  };

  const handleKeyDown = (e: KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="flex items-end gap-2 p-2"
    >
      <textarea
        ref={inputRef}
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={
          disabled
            ? agentStatus === "thinking"
              ? "Thinking…"
              : "Connecting…"
            : 'Type a command (e.g., "guide me")'
        }
        disabled={disabled}
        rows={1}
        className="flex-1 resize-none rounded-xl border border-[var(--color-border)] bg-[var(--color-surface-2)] px-4 py-2.5 text-sm text-[var(--color-text)] placeholder-[var(--color-text-dim)] outline-none transition-colors focus:border-[var(--color-accent)] disabled:opacity-50"
      />
      <button
        type="submit"
        disabled={disabled || !text.trim()}
        className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-[var(--color-accent)] text-white transition-opacity hover:opacity-90 disabled:opacity-30"
        aria-label="Send"
      >
        <Send className="h-5 w-5" />
      </button>
    </form>
  );
}
