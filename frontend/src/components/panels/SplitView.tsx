"use client";

import type { UIAction } from "@/lib/types";
import { DynamicContent } from "../DynamicContent";

interface Props {
  left?: UIAction;
  right?: UIAction;
}

/**
 * SplitView renders two panels side by side.
 * Each side receives a single UIAction to render.
 */
export function SplitView({ left, right }: Props) {
  return (
    <div className="flex h-full">
      <div className="flex-1 overflow-auto border-r border-[var(--color-border)]">
        {left ? (
          <DynamicContent actions={[left]} />
        ) : (
          <Empty />
        )}
      </div>
      <div className="flex-1 overflow-auto">
        {right ? (
          <DynamicContent actions={[right]} />
        ) : (
          <Empty />
        )}
      </div>
    </div>
  );
}

function Empty() {
  return (
    <div className="flex h-full items-center justify-center text-sm text-[var(--color-text-dim)]">
      No content
    </div>
  );
}
