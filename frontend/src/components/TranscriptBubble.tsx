"use client";

import type { ChatMessage } from "@/lib/types";
import { Lightbulb, Bird } from "lucide-react";

interface Props {
  message: ChatMessage;
}

export function TranscriptBubble({ message }: Props) {
  const isUser = message.role === "user";

  return (
    <div
      className={`flex gap-3 ${isUser ? "flex-row-reverse" : "flex-row"}`}
    >
      {/* Avatar icon */}
      <div
        className={`flex h-7 w-7 shrink-0 items-center justify-center rounded-full ${
          isUser
            ? "bg-[var(--color-surface-2)]"
            : "bg-[var(--color-assistant-bubble)]"
        }`}
      >
        {isUser ? (
          <Lightbulb className="h-4 w-4 text-[var(--color-accent)]" />
        ) : (
          <Bird className="h-4 w-4 text-[var(--color-success)]" />
        )}
      </div>

      {/* Bubble */}
      <div
        className={`max-w-[85%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed ${
          isUser
            ? "rounded-tr-sm bg-[var(--color-user-bubble)] text-[var(--color-text)]"
            : "rounded-tl-sm bg-[var(--color-assistant-bubble)] text-[var(--color-text)]"
        }`}
      >
        {message.text}
      </div>
    </div>
  );
}
