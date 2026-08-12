"use client";

import { CheckCircle2, XCircle, AlertCircle } from "lucide-react";

interface Props {
  status?: "success" | "error" | "pending";
  title?: string;
  message?: string;
  details?: Record<string, string>;
}

export function Confirmation({
  status = "success",
  title,
  message,
  details,
}: Props) {
  const icons = {
    success: <CheckCircle2 className="h-12 w-12 text-[var(--color-success)]" />,
    error: <XCircle className="h-12 w-12 text-[var(--color-error)]" />,
    pending: <AlertCircle className="h-12 w-12 text-yellow-400" />,
  };

  return (
    <div className="flex flex-col items-center justify-center p-12 text-center">
      {icons[status]}

      {title && (
        <h3 className="mt-4 text-xl font-semibold text-[var(--color-text)]">
          {title}
        </h3>
      )}

      {message && (
        <p className="mt-2 max-w-md text-sm text-[var(--color-text-dim)]">
          {message}
        </p>
      )}

      {details && Object.keys(details).length > 0 && (
        <div className="mt-6 w-full max-w-sm rounded-xl border border-[var(--color-border)] bg-[var(--color-surface-2)] p-4">
          {Object.entries(details).map(([key, val]) => (
            <div key={key} className="flex justify-between py-1.5 text-sm">
              <span className="text-[var(--color-text-dim)]">{key}</span>
              <span className="font-medium text-[var(--color-text)]">
                {val}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
