"use client";

import { Play, Pause, SkipForward, SkipBack, Volume2 } from "lucide-react";
import { useState } from "react";

interface Props {
  track_name?: string;
  artist?: string;
  album_art?: string;
  duration?: string;
}

/**
 * Music player placeholder — for Phase 2+ with real audio integration.
 */
export function MusicPlayer({
  track_name = "Unknown Track",
  artist = "Unknown Artist",
  album_art,
  duration = "3:45",
}: Props) {
  const [playing, setPlaying] = useState(false);

  return (
    <div className="p-6">
      <div className="mx-auto max-w-sm">
        {/* Album art */}
        <div className="mb-6 aspect-square overflow-hidden rounded-2xl bg-[var(--color-bg)]">
          {album_art ? (
            <img
              src={album_art}
              alt={track_name}
              className="h-full w-full object-cover"
            />
          ) : (
            <div className="flex h-full items-center justify-center">
              <Volume2 className="h-16 w-16 text-[var(--color-border)]" />
            </div>
          )}
        </div>

        {/* Track info */}
        <div className="mb-4 text-center">
          <h3 className="text-lg font-semibold text-[var(--color-text)]">
            {track_name}
          </h3>
          <p className="text-sm text-[var(--color-text-dim)]">{artist}</p>
        </div>

        {/* Progress bar */}
        <div className="mb-4">
          <div className="h-1 overflow-hidden rounded-full bg-[var(--color-border)]">
            <div className="h-full w-1/3 rounded-full bg-[var(--color-accent)]" />
          </div>
          <div className="mt-1 flex justify-between text-xs text-[var(--color-text-dim)]">
            <span>1:15</span>
            <span>{duration}</span>
          </div>
        </div>

        {/* Controls */}
        <div className="flex items-center justify-center gap-6">
          <button className="text-[var(--color-text-dim)] hover:text-[var(--color-text)]">
            <SkipBack className="h-5 w-5" />
          </button>
          <button
            onClick={() => setPlaying(!playing)}
            className="flex h-12 w-12 items-center justify-center rounded-full bg-[var(--color-accent)] text-white"
          >
            {playing ? (
              <Pause className="h-5 w-5" />
            ) : (
              <Play className="ml-0.5 h-5 w-5" />
            )}
          </button>
          <button className="text-[var(--color-text-dim)] hover:text-[var(--color-text)]">
            <SkipForward className="h-5 w-5" />
          </button>
        </div>
      </div>
    </div>
  );
}
