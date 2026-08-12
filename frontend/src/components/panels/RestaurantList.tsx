"use client";

import { MapPin, CreditCard, Wifi, Baby, Dog } from "lucide-react";
import type { Restaurant } from "@/lib/types";

interface Props {
  restaurants?: Restaurant[];
}

export function RestaurantList({ restaurants = [] }: Props) {
  if (restaurants.length === 0) {
    return (
      <div className="py-4 text-center text-sm text-[var(--color-text-dim)]">
        No restaurants to display.
      </div>
    );
  }

  return (
    <div className="grid gap-3 py-4 sm:grid-cols-1">
      {restaurants.map((r) => (
        <RestaurantCard key={r.id} restaurant={r} />
      ))}
    </div>
  );
}

function RestaurantCard({ restaurant: r }: { restaurant: Restaurant }) {
  return (
    <a
      href={r.url}
      target="_blank"
      rel="noopener noreferrer"
      className="group flex flex-col overflow-hidden rounded-xl border border-[var(--color-border)] bg-[var(--color-surface-2)] transition-all hover:border-[var(--color-accent)]"
    >
      {/* Photo */}
      {r.photo_url && (
        <div className="relative h-36 overflow-hidden bg-[var(--color-bg)]">
          <img
            src={r.photo_url}
            alt={r.name}
            className="h-full w-full object-cover transition-transform group-hover:scale-105"
          />
          {r.genre && (
            <span className="absolute bottom-2 left-2 rounded-full bg-black/60 px-2 py-0.5 text-xs text-white backdrop-blur">
              {r.genre}
            </span>
          )}
        </div>
      )}

      {/* Info */}
      <div className="flex flex-1 flex-col gap-2 p-4">
        <h3 className="font-semibold text-[var(--color-text)] line-clamp-1">
          {r.name}
        </h3>

        <p className="flex items-center gap-1 text-xs text-[var(--color-text-dim)]">
          <MapPin className="h-3 w-3 shrink-0" />
          <span className="line-clamp-1">{r.access || r.address}</span>
        </p>

        {/* Budget */}
        {r.budget && (
          <p className="text-xs font-medium text-[var(--color-accent)]">
            {r.budget}
            {r.budget_average && ` (${r.budget_average})`}
          </p>
        )}

        {/* Open hours */}
        {r.open_hours && (
          <p className="text-xs text-[var(--color-text-dim)] line-clamp-1">
            {r.open_hours}
          </p>
        )}

        {/* Tags */}
        <div className="mt-auto flex flex-wrap gap-1.5 pt-2">
          {r.card_accepted && <Tag icon={<CreditCard className="h-3 w-3" />} label="Card" />}
          {r.wifi && <Tag icon={<Wifi className="h-3 w-3" />} label="WiFi" />}
          {r.child_friendly && <Tag icon={<Baby className="h-3 w-3" />} label="Kids" />}
          {r.pet_friendly && <Tag icon={<Dog className="h-3 w-3" />} label="Pet" />}
        </div>
      </div>
    </a>
  );
}

function Tag({ icon, label }: { icon: React.ReactNode; label: string }) {
  return (
    <span className="flex items-center gap-1 rounded-md bg-[var(--color-bg)] px-1.5 py-0.5 text-[10px] text-[var(--color-text-dim)]">
      {icon}
      {label}
    </span>
  );
}
