"use client";

import { Star } from "lucide-react";

interface Review {
  author: string;
  rating: number;
  text: string;
  date?: string;
}

interface Props {
  restaurant_name?: string;
  average_rating?: number;
  reviews?: Review[];
}

export function ReviewsPanel({
  restaurant_name,
  average_rating,
  reviews = [],
}: Props) {
  return (
    <div className="p-6">
      {restaurant_name && (
        <h3 className="mb-1 text-lg font-semibold text-[var(--color-text)]">
          {restaurant_name}
        </h3>
      )}

      {average_rating !== undefined && (
        <div className="mb-4 flex items-center gap-2">
          <Stars rating={average_rating} />
          <span className="text-sm font-medium text-[var(--color-text)]">
            {average_rating.toFixed(1)}
          </span>
          <span className="text-xs text-[var(--color-text-dim)]">
            ({reviews.length} reviews)
          </span>
        </div>
      )}

      {reviews.length === 0 ? (
        <p className="text-sm text-[var(--color-text-dim)]">
          No reviews available yet.
        </p>
      ) : (
        <div className="flex flex-col gap-3">
          {reviews.map((r, i) => (
            <div
              key={i}
              className="rounded-xl border border-[var(--color-border)] bg-[var(--color-surface-2)] p-4"
            >
              <div className="mb-2 flex items-center justify-between">
                <span className="text-sm font-medium text-[var(--color-text)]">
                  {r.author}
                </span>
                <Stars rating={r.rating} size="small" />
              </div>
              <p className="text-sm leading-relaxed text-[var(--color-text-dim)]">
                {r.text}
              </p>
              {r.date && (
                <span className="mt-2 block text-xs text-[var(--color-text-dim)]">
                  {r.date}
                </span>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function Stars({
  rating,
  size = "normal",
}: {
  rating: number;
  size?: "normal" | "small";
}) {
  const iconSize = size === "small" ? "h-3 w-3" : "h-4 w-4";
  return (
    <div className="flex">
      {[1, 2, 3, 4, 5].map((n) => (
        <Star
          key={n}
          className={`${iconSize} ${
            n <= rating
              ? "fill-yellow-400 text-yellow-400"
              : "text-[var(--color-border)]"
          }`}
        />
      ))}
    </div>
  );
}
