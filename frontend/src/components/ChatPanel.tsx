"use client";

import { useEffect, useRef } from "react";
import { ChevronUp } from "lucide-react";
import { useSessionStore } from "@/stores/session";
import { ChatInput } from "./ChatInput";
import { SuggestionChips } from "./SuggestionChips";
import { ThinkingIndicator } from "./ThinkingIndicator";
import { TranscriptBubble } from "./TranscriptBubble";
import { VoiceStatus } from "./VoiceStatus";

interface Props {
  onSend: (text: string) => void;
  onChipSelect: (chip: string) => void;
  isExpanded: boolean;
  onToggleExpand: () => void;
}

export function ChatPanel({ onSend, onChipSelect, isExpanded, onToggleExpand }: Props) {
  const messages = useSessionStore((s) => s.messages);
  const agentStatus = useSessionStore((s) => s.agentStatus);
  const currentSuggestions = useSessionStore((s) => s.currentSuggestions);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, agentStatus]);

  if (!isExpanded) {
    return (
      <div className="flex items-center gap-2">
        <button
          type="button"
          onClick={onToggleExpand}
          className="flex shrink-0 items-center justify-center rounded-lg p-2 text-[var(--color-text-dim)] hover:bg-[var(--color-surface-2)] hover:text-[var(--color-text)]"
          aria-label="Expand chat"
        >
          <ChevronUp className="h-5 w-5" />
        </button>
        <div className="min-w-0 flex-1">
          <ChatInput onSend={onSend} />
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col">
      {/* Voice status row — chevron collapses */}
      <VoiceStatus onCollapse={onToggleExpand} />

      {/* Messages area */}
      <div className="max-h-48 overflow-y-auto">
        <div className="flex flex-col gap-3 py-2">
          {messages.map((msg) => (
            <TranscriptBubble key={msg.id} message={msg} />
          ))}
          {agentStatus === "thinking" && <ThinkingIndicator />}
          <div ref={bottomRef} />
        </div>
      </div>

      {/* Suggestion chips */}
      <SuggestionChips chips={currentSuggestions} onSelect={onChipSelect} />

      {/* Input */}
      <ChatInput onSend={onSend} />
    </div>
  );
}
