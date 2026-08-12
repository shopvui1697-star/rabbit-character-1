"use client";

import { MapPin } from "lucide-react";

interface Marker {
  name: string;
  lat: number;
  lng: number;
  genre?: string;
}

interface Props {
  markers?: Marker[];
  center?: { lat: number; lng: number };
}

/**
 * Lightweight map view — renders markers on a static placeholder.
 * For Phase 2+, replace with Leaflet or Google Maps integration.
 */
export function MapView({ markers = [] }: Props) {
  if (markers.length === 0) {
    return (
      <div className="p-6 text-center text-sm text-[var(--color-text-dim)]">
        No locations to display.
      </div>
    );
  }

  return (
    <div className="p-6">
      <h3 className="mb-4 text-sm font-semibold text-[var(--color-text-dim)] uppercase tracking-wider">
        Locations ({markers.length})
      </h3>

      {/* Map placeholder */}
      <div className="relative mb-4 flex h-64 items-center justify-center rounded-xl border border-[var(--color-border)] bg-[var(--color-bg)]">
        <div className="text-center">
          <MapPin className="mx-auto mb-2 h-10 w-10 text-[var(--color-accent)]" />
          <p className="text-xs text-[var(--color-text-dim)]">
            Interactive map coming soon
          </p>
          <p className="mt-1 text-xs text-[var(--color-text-dim)]">
            {markers.length} location{markers.length > 1 ? "s" : ""} found
          </p>
        </div>
      </div>

      {/* Marker list */}
      <div className="flex flex-col gap-2">
        {markers.map((m, i) => (
          <div
            key={`${m.lat}-${m.lng}-${i}`}
            className="flex items-center gap-3 rounded-lg bg-[var(--color-surface-2)] px-3 py-2"
          >
            <div className="flex h-6 w-6 items-center justify-center rounded-full bg-[var(--color-accent)] text-xs font-bold text-white">
              {i + 1}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-[var(--color-text)] truncate">
                {m.name}
              </p>
              {m.genre && (
                <p className="text-xs text-[var(--color-text-dim)]">{m.genre}</p>
              )}
            </div>
            <span className="text-[10px] text-[var(--color-text-dim)] font-mono">
              {m.lat.toFixed(4)}, {m.lng.toFixed(4)}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
