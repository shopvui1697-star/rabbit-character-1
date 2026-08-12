"use client";

import { Clock, MapPin } from "lucide-react";

interface PlanItem {
  time: string;
  activity: string;
  location?: string;
  notes?: string;
}

interface Props {
  title?: string;
  date?: string;
  items?: PlanItem[];
}

/**
 * Plan timeline view — renders a sequence of planned activities.
 */
export function PlanEditor({ title, date, items = [] }: Props) {
  return (
    <div className="p-6">
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-[var(--color-text)]">
          {title || "Your Plan"}
        </h3>
        {date && (
          <p className="text-sm text-[var(--color-text-dim)]">{date}</p>
        )}
      </div>

      {items.length === 0 ? (
        <p className="text-sm text-[var(--color-text-dim)]">
          No plan items yet. Describe what you&apos;d like to do!
        </p>
      ) : (
        <div className="relative pl-6">
          {/* Timeline line */}
          <div className="absolute left-[9px] top-2 bottom-2 w-px bg-[var(--color-border)]" />

          <div className="flex flex-col gap-6">
            {items.map((item, i) => (
              <div key={i} className="relative">
                {/* Dot */}
                <div className="absolute -left-6 top-1 h-[18px] w-[18px] rounded-full border-2 border-[var(--color-accent)] bg-[var(--color-surface)]" />

                <div className="rounded-xl border border-[var(--color-border)] bg-[var(--color-surface-2)] p-4">
                  <div className="mb-1 flex items-center gap-2">
                    <Clock className="h-3.5 w-3.5 text-[var(--color-accent)]" />
                    <span className="text-xs font-medium text-[var(--color-accent)]">
                      {item.time}
                    </span>
                  </div>
                  <p className="font-medium text-[var(--color-text)]">
                    {item.activity}
                  </p>
                  {item.location && (
                    <p className="mt-1 flex items-center gap-1 text-xs text-[var(--color-text-dim)]">
                      <MapPin className="h-3 w-3" />
                      {item.location}
                    </p>
                  )}
                  {item.notes && (
                    <p className="mt-1.5 text-xs text-[var(--color-text-dim)]">
                      {item.notes}
                    </p>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
