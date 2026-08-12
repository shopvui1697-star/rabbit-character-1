"use client";

import { useState } from "react";
import { AppHeader } from "@/components/AppHeader";
import { ChatPanel } from "@/components/ChatPanel";
import { DynamicContent } from "@/components/DynamicContent";
import { useWebSocket } from "@/hooks/useWebSocket";
import { useSessionStore } from "@/stores/session";

export default function Home() {
  const { sendText, selectChip } = useWebSocket();
  const currentUIActions = useSessionStore((s) => s.currentUIActions);
  const [chatExpanded, setChatExpanded] = useState(true);

  return (
    <div className="mx-auto flex min-h-screen max-w-2xl flex-col bg-[var(--color-bg)]">
      {/* Header — logo + title */}
      <AppHeader />

      {/* Main content — scrollable, pad bottom so content isn't hidden under fixed chat */}
      <main
        className="flex-1 overflow-y-auto px-4 transition-[padding] duration-200"
        style={{
          paddingBottom: chatExpanded ? "360px" : "80px",
        }}
      >
        {currentUIActions.length > 0 ? (
          <DynamicContent actions={currentUIActions} />
        ) : (
          <EmptyState onSend={sendText} />
        )}
      </main>

      {/* Chat section — fixed at bottom, collapsible */}
      <section className="fixed bottom-0 left-0 right-0 z-10 mx-auto max-w-2xl border-t border-[var(--color-border)] bg-[var(--color-surface)] px-4 pb-4 pt-2 transition-all duration-200">
        <ChatPanel
          onSend={sendText}
          onChipSelect={selectChip}
          isExpanded={chatExpanded}
          onToggleExpand={() => setChatExpanded((e) => !e)}
        />
      </section>
    </div>
  );
}

function EmptyState({ onSend }: { onSend: (t: string) => void }) {
  return (
    <div className="rounded-xl border border-[var(--color-border)] bg-[var(--color-surface-2)] p-6">
      <p className="mb-4 text-center text-sm text-[var(--color-text-dim)]">
        Ask me to find restaurants, plan an outing, or explore music.
      </p>
      <div className="flex flex-wrap justify-center gap-2">
        {[
          "Find Italian restaurants in Shibuya",
          "Find sushi in Shibuya",
          "Find anime movies like Spirited Away",
        ].map((example) => (
          <button
            key={example}
            onClick={() => onSend(example)}
            className="rounded-lg border border-[var(--color-border)] bg-[var(--color-bg)] px-4 py-2 text-sm text-[var(--color-text-dim)] transition-colors hover:border-[var(--color-accent)] hover:text-[var(--color-text)]"
          >
            {example}
          </button>
        ))}
      </div>
    </div>
  );
}
