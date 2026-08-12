"use client";

interface Props {
  chips: string[];
  onSelect: (chip: string) => void;
}

export function SuggestionChips({ chips, onSelect }: Props) {
  if (chips.length === 0) return null;

  return (
    <div className="flex flex-wrap gap-2 px-4 py-2">
      {chips.map((chip) => (
        <button
          key={chip}
          onClick={() => onSelect(chip)}
          className="rounded-full border border-[var(--color-accent)] bg-[var(--color-accent-soft)] px-3 py-1.5 text-xs font-medium text-[var(--color-accent)] transition-colors hover:bg-[var(--color-accent)] hover:text-white"
        >
          {chip}
        </button>
      ))}
    </div>
  );
}
