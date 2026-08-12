/** WebSocket message types — mirrors the backend protocol. */

import type { UIAction } from "./types";

// ─── Messages: Frontend → Backend ──────────────────────────────────

export interface TextInputMessage {
  type: "text_input";
  data: { text: string };
}

export interface ChipSelectedMessage {
  type: "chip_selected";
  data: { chip: string };
}

export interface FeedbackMessage {
  type: "feedback";
  data: { trace_id: string; score: "up" | "down" };
}

export type ClientMessage =
  | TextInputMessage
  | ChipSelectedMessage
  | FeedbackMessage;

// ─── Messages: Backend → Frontend ──────────────────────────────────

export interface VoiceResponseMessage {
  type: "voice_response";
  data: { text: string };
}

export interface UIUpdateMessage {
  type: "ui_update";
  data: { actions: UIAction[] };
}

export interface SuggestionsMessage {
  type: "suggestions";
  data: { chips: string[] };
}

export interface StatusMessage {
  type: "status";
  data: { state: "idle" | "thinking" | "speaking" };
}

export interface ErrorMessage {
  type: "error";
  data: { message: string };
}

export type ServerMessage =
  | VoiceResponseMessage
  | UIUpdateMessage
  | SuggestionsMessage
  | StatusMessage
  | ErrorMessage;
