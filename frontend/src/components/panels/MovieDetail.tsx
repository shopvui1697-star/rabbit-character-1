"use client";

import { Star, Calendar, Clock, Film, ExternalLink } from "lucide-react";
import type { Movie } from "@/lib/types";

interface Props {
  movie?: Movie;
}

export function MovieDetail({ movie }: Props) {
  if (!movie) {
    return (
      <div className="py-4 text-center text-sm text-[var(--color-text-dim)]">
        No movie details available.
      </div>
    );
  }

  const m = movie;
  const year = m.release_date ? m.release_date.substring(0, 4) : "";

  return (
    <div className="overflow-hidden rounded-xl border border-[var(--color-border)] bg-[var(--color-surface-2)]">
      {/* Backdrop */}
      {m.backdrop_url && (
        <div className="relative h-44 overflow-hidden bg-[var(--color-bg)]">
          <img
            src={m.backdrop_url}
            alt={m.title}
            className="h-full w-full object-cover"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-[var(--color-surface-2)] to-transparent" />
        </div>
      )}

      <div className="flex gap-4 p-4">
        {/* Poster */}
        {m.poster_url ? (
          <div className="relative -mt-12 h-36 w-24 shrink-0 overflow-hidden rounded-lg shadow-lg">
            <img
              src={m.poster_url}
              alt={m.title}
              className="h-full w-full object-cover"
            />
          </div>
        ) : (
          <div className="flex h-36 w-24 shrink-0 items-center justify-center rounded-lg bg-[var(--color-bg)]">
            <Film className="h-10 w-10 text-[var(--color-text-dim)]" />
          </div>
        )}

        {/* Title & meta */}
        <div className="flex flex-1 flex-col gap-1">
          <h2 className="text-lg font-bold text-[var(--color-text)]">
            {m.title}
          </h2>

          {m.original_title && m.original_title !== m.title && (
            <p className="text-sm text-[var(--color-text-dim)]">
              {m.original_title}
            </p>
          )}

          <div className="mt-1 flex flex-wrap items-center gap-3 text-xs text-[var(--color-text-dim)]">
            {year && (
              <span className="flex items-center gap-1">
                <Calendar className="h-3 w-3" />
                {year}
              </span>
            )}
            {m.vote_average != null && m.vote_average > 0 && (
              <span className="flex items-center gap-1 text-yellow-400">
                <Star className="h-3 w-3 fill-current" />
                {m.vote_average.toFixed(1)}
                {m.vote_count > 0 && (
                  <span className="text-[var(--color-text-dim)]">
                    ({m.vote_count.toLocaleString()})
                  </span>
                )}
              </span>
            )}
            {m.runtime != null && m.runtime > 0 && (
              <span className="flex items-center gap-1">
                <Clock className="h-3 w-3" />
                {m.runtime} min
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Overview */}
      {m.overview && (
        <div className="px-4 pb-4">
          <p className="text-sm leading-relaxed text-[var(--color-text-dim)]">
            {m.overview}
          </p>
        </div>
      )}

      {/* Link */}
      {m.source_url && (
        <div className="border-t border-[var(--color-border)] px-4 py-3">
          <a
            href={m.source_url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1.5 text-xs text-[var(--color-accent)] hover:underline"
          >
            <ExternalLink className="h-3 w-3" />
            View on TMDB
          </a>
        </div>
      )}
    </div>
  );
}
