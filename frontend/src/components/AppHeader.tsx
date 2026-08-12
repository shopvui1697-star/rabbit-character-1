"use client";

/** Rabbit V2 style header — logo, title, tagline. */
export function AppHeader() {
  return (
    <header className="flex flex-col items-center pt-8 pb-6">
      {/* Logo: pink circle with white eye */}
      <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-[var(--color-accent)] shadow-lg shadow-[var(--color-accent-soft)]">
        <svg viewBox="0 0 32 32" fill="white" className="h-8 w-8">
          <ellipse cx="16" cy="14" rx="5" ry="7" />
        </svg>
      </div>
      <h1 className="text-3xl font-bold tracking-tight text-[var(--color-accent)]">
        Rabbit3
      </h1>
      <p className="mt-1 text-sm text-[var(--color-text-dim)]">
        Voice-Powered Assistant
      </p>
    </header>
  );
}
