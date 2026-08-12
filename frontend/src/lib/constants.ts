export const WS_URL =
  process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000/ws";

export const MAX_RECONNECT_ATTEMPTS = 5;
export const RECONNECT_DELAY_MS = 2000;
