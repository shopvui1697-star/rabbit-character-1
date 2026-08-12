"use client";

import { Star, Calendar, Film, ExternalLink } from "lucide-react";
import type { Movie } from "@/lib/types";

interface Props {
  movies?: Movie[];
}

export function MovieList({ movies = [] }: Props) {
  if (movies.length === 0) {
    return (
      <div className="py-4 text-center text-sm text-[var(--color-text-dim)]">
        No movies to display.
      </div>
    );
  }

  return (
    <div className="grid gap-3 py-4 sm:grid-cols-1">
      {movies.map((m) => (
        <MovieCard key={m.id} movie={m} />
      ))}
    </div>
  );
}

function MovieCard({ movie: m }: { movie: Movie }) {
  const year = m.release_date ? m.release_date.substring(0, 4) : "";

  return (
    <a
      href={m.source_url || `https://www.themoviedb.org/movie/${m.id}`}
      target="_blank"
      rel="noopener noreferrer"
      className="group flex overflow-hidden rounded-xl border border-[var(--color-border)] bg-[var(--color-surface-2)] transition-all hover:border-[var(--color-accent)]"
    >
      {/* Poster */}
      {m.poster_url ? (
        <div className="relative h-auto w-24 shrink-0 overflow-hidden bg-[var(--color-bg)]">
          <img
            src={m.poster_url}
            alt={m.title}
            className="h-full w-full object-cover transition-transform group-hover:scale-105"
          />
        </div>
      ) : (
        <div className="flex h-auto w-24 shrink-0 items-center justify-center bg-[var(--color-bg)]">
          <Film className="h-8 w-8 text-[var(--color-text-dim)]" />
        </div>
      )}

      {/* Info */}
      <div className="flex flex-1 flex-col gap-1.5 p-3">
        <div className="flex items-start justify-between gap-2">
          <h3 className="font-semibold text-[var(--color-text)] line-clamp-1">
            {m.title}
          </h3>
          <ExternalLink className="mt-0.5 h-3.5 w-3.5 shrink-0 text-[var(--color-text-dim)] opacity-0 group-hover:opacity-100 transition-opacity" />
        </div>

        {m.original_title && m.original_title !== m.title && (
          <p className="text-xs text-[var(--color-text-dim)]">
            {m.original_title}
          </p>
        )}

        {/* Meta row */}
        <div className="flex items-center gap-3 text-xs text-[var(--color-text-dim)]">
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
            </span>
          )}
          {m.runtime != null && m.runtime > 0 && (
            <span>{m.runtime} min</span>
          )}
        </div>

        {/* Overview */}
        {m.overview && (
          <p className="mt-1 text-xs text-[var(--color-text-dim)] line-clamp-2">
            {m.overview}
          </p>
        )}
      </div>
    </a>
  );
}
