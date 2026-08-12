"use client";

import { Bird } from "lucide-react";

export function ThinkingIndicator() {
  return (
    <div className="flex gap-3">
      <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-[var(--color-assistant-bubble)]">
        <Bird className="h-4 w-4 text-[var(--color-success)]" />
      </div>
      <div className="flex items-center gap-1 rounded-2xl rounded-tl-sm bg-[var(--color-assistant-bubble)] px-4 py-3">
        <span className="thinking-dot h-2 w-2 rounded-full bg-[var(--color-accent)]" />
        <span className="thinking-dot h-2 w-2 rounded-full bg-[var(--color-accent)]" />
        <span className="thinking-dot h-2 w-2 rounded-full bg-[var(--color-accent)]" />
      </div>
    </div>
  );
}
