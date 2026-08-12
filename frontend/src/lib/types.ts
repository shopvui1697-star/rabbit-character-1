/** UI action types — mirrors backend UIActionType enum. */
export type UIActionType =
  | "SHOW_MAP"
  | "SHOW_RESTAURANT_LIST"
  | "SHOW_RESTAURANT_DETAIL"
  | "SHOW_MOVIE_LIST"
  | "SHOW_MOVIE_DETAIL"
  | "SHOW_MUSIC_PLAYER"
  | "SHOW_PLAN_EDITOR"
  | "SHOW_CONFIRMATION"
  | "SHOW_REVIEWS"
  | "SHOW_SUGGESTION_CHIPS"
  | "CLEAR_UI"
  | "SPLIT_VIEW";

export type UIPriority = "primary" | "secondary" | "overlay";

export interface UIAction {
  action: UIActionType;
  priority: UIPriority;
  data: Record<string, unknown>;
}

/** Restaurant from the HotPepper API. */
export interface Restaurant {
  id: string;
  name: string;
  address: string;
  lat: number | null;
  lng: number | null;
  genre: string;
  sub_genre: string;
  budget: string;
  budget_average: string;
  open_hours: string;
  close: string;
  access: string;
  photo_url: string;
  url: string;
  private_room: boolean;
  card_accepted: boolean;
  wifi: boolean;
  parking: boolean;
  pet_friendly: boolean;
  child_friendly: boolean;
}

/** Movie from the Lovvit Movie API. */
export interface Movie {
  id: number;
  title: string;
  original_title: string;
  overview: string;
  release_date: string;
  poster_url: string;
  backdrop_url: string;
  source_url: string;
  vote_average: number | null;
  vote_count: number;
  genre_ids: string;
  product_type: string;
  runtime: number | null;
}

/** A single message in the conversation transcript. */
export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  text: string;
  uiActions?: UIAction[];
  suggestions?: string[];
  timestamp: number;
}

/** Connection status. */
export type ConnectionStatus = "connecting" | "connected" | "disconnected";

/** Agent processing status. */
export type AgentStatus = "idle" | "thinking" | "speaking";
