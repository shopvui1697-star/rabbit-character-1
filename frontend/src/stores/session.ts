import { create } from "zustand";
import type {
  AgentStatus,
  ChatMessage,
  ConnectionStatus,
  UIAction,
} from "@/lib/types";

interface SessionStore {
  // Connection
  connectionStatus: ConnectionStatus;
  setConnectionStatus: (status: ConnectionStatus) => void;

  // Agent status
  agentStatus: AgentStatus;
  setAgentStatus: (status: AgentStatus) => void;

  // Chat messages
  messages: ChatMessage[];
  addMessage: (msg: ChatMessage) => void;
  updateLastAssistantMessage: (
    update: Partial<Pick<ChatMessage, "uiActions" | "suggestions">>
  ) => void;

  // Active UI
  currentUIActions: UIAction[];
  setCurrentUIActions: (actions: UIAction[]) => void;

  // Suggestions
  currentSuggestions: string[];
  setCurrentSuggestions: (chips: string[]) => void;

  // Reset
  clearSession: () => void;
}

export const useSessionStore = create<SessionStore>((set) => ({
  connectionStatus: "disconnected",
  setConnectionStatus: (status) => set({ connectionStatus: status }),

  agentStatus: "idle",
  setAgentStatus: (status) => set({ agentStatus: status }),

  messages: [],
  addMessage: (msg) =>
    set((state) => ({ messages: [...state.messages, msg] })),
  updateLastAssistantMessage: (update) =>
    set((state) => {
      const msgs = [...state.messages];
      for (let i = msgs.length - 1; i >= 0; i--) {
        if (msgs[i].role === "assistant") {
          msgs[i] = { ...msgs[i], ...update };
          break;
        }
      }
      return { messages: msgs };
    }),

  currentUIActions: [],
  setCurrentUIActions: (actions) => set({ currentUIActions: actions }),

  currentSuggestions: [],
  setCurrentSuggestions: (chips) => set({ currentSuggestions: chips }),

  clearSession: () =>
    set({
      messages: [],
      currentUIActions: [],
      currentSuggestions: [],
      agentStatus: "idle",
    }),
}));
