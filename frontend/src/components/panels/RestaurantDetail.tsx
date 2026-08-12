"use client";

import { MapPin, Clock, CreditCard, Wifi, ParkingCircle, Baby, Dog, DoorOpen, ExternalLink } from "lucide-react";
import type { Restaurant } from "@/lib/types";

interface Props {
  restaurant?: Restaurant;
}

export function RestaurantDetail({ restaurant: r }: Props) {
  if (!r) {
    return (
      <div className="p-6 text-center text-sm text-[var(--color-text-dim)]">
        No restaurant selected.
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-2xl p-6">
      {/* Hero */}
      {r.photo_url && (
        <div className="mb-6 overflow-hidden rounded-2xl">
          <img
            src={r.photo_url}
            alt={r.name}
            className="h-56 w-full object-cover"
          />
        </div>
      )}

      {/* Header */}
      <div className="mb-4">
        <h2 className="text-2xl font-bold text-[var(--color-text)]">
          {r.name}
        </h2>
        {r.genre && (
          <span className="mt-1 inline-block rounded-full bg-[var(--color-accent-soft)] px-3 py-0.5 text-xs font-medium text-[var(--color-accent)]">
            {r.genre}
            {r.sub_genre ? ` / ${r.sub_genre}` : ""}
          </span>
        )}
      </div>

      {/* Info rows */}
      <div className="flex flex-col gap-3 text-sm">
        <InfoRow icon={<MapPin className="h-4 w-4" />} label="Address" value={r.address} />
        <InfoRow icon={<Clock className="h-4 w-4" />} label="Hours" value={r.open_hours} />
        {r.close && <InfoRow icon={<Clock className="h-4 w-4" />} label="Closed" value={r.close} />}
        <InfoRow
          icon={<span className="text-sm">💰</span>}
          label="Budget"
          value={[r.budget, r.budget_average].filter(Boolean).join(" — ")}
        />
        <InfoRow icon={<MapPin className="h-4 w-4" />} label="Access" value={r.access} />
      </div>

      {/* Features grid */}
      <div className="mt-6 grid grid-cols-3 gap-2">
        <FeatureChip icon={<DoorOpen />} label="Private Room" active={r.private_room} />
        <FeatureChip icon={<CreditCard />} label="Card OK" active={r.card_accepted} />
        <FeatureChip icon={<Wifi />} label="WiFi" active={r.wifi} />
        <FeatureChip icon={<ParkingCircle />} label="Parking" active={r.parking} />
        <FeatureChip icon={<Baby />} label="Kids OK" active={r.child_friendly} />
        <FeatureChip icon={<Dog />} label="Pets OK" active={r.pet_friendly} />
      </div>

      {/* Link */}
      {r.url && (
        <a
          href={r.url}
          target="_blank"
          rel="noopener noreferrer"
          className="mt-6 flex items-center justify-center gap-2 rounded-xl bg-[var(--color-accent)] px-6 py-3 text-sm font-medium text-white transition-opacity hover:opacity-90"
        >
          View on HotPepper
          <ExternalLink className="h-4 w-4" />
        </a>
      )}
    </div>
  );
}

function InfoRow({
  icon,
  label,
  value,
}: {
  icon: React.ReactNode;
  label: string;
  value?: string;
}) {
  if (!value) return null;
  return (
    <div className="flex items-start gap-3">
      <span className="mt-0.5 text-[var(--color-text-dim)]">{icon}</span>
      <div>
        <span className="text-xs text-[var(--color-text-dim)]">{label}</span>
        <p className="text-[var(--color-text)]">{value}</p>
      </div>
    </div>
  );
}

function FeatureChip({
  icon,
  label,
  active,
}: {
  icon: React.ReactNode;
  label: string;
  active: boolean;
}) {
  return (
    <div
      className={`flex items-center gap-1.5 rounded-lg px-2 py-1.5 text-xs ${
        active
          ? "bg-[var(--color-accent-soft)] text-[var(--color-accent)]"
          : "bg-[var(--color-bg)] text-[var(--color-text-dim)] opacity-40"
      }`}
    >
      <span className="h-4 w-4">{icon}</span>
      {label}
    </div>
  );
}
