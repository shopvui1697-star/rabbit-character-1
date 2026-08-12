# Rabbit3 Frontend

> Next.js + React frontend for the Rabbit3 agentic voice assistant — declarative UI rendering from structured LLM output.

---

## Quick Start

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build
npm start
```

The app will be available at `http://localhost:3000`.

---

## Structure

```
frontend/
├── src/
│   ├── app/
│   │   ├── layout.tsx              # Root layout (dark theme, metadata)
│   │   ├── page.tsx                # Main page: split-panel UI
│   │   └── globals.css             # Dark theme CSS variables
│   │
│   ├── components/
│   │   ├── ChatPanel.tsx           # Chat area (messages + input)
│   │   ├── ChatInput.tsx           # Text input with Enter-to-send
│   │   ├── TranscriptBubble.tsx    # User/assistant message bubbles
│   │   ├── ThinkingIndicator.tsx   # Animated thinking dots
│   │   ├── SuggestionChips.tsx     # Clickable follow-up suggestions
│   │   ├── StatusBar.tsx           # Connection + agent status
│   │   ├── DynamicContent.tsx      # UIAction → component router
│   │   └── panels/
│   │       ├── RestaurantList.tsx      # Card grid with photos
│   │       ├── RestaurantDetail.tsx    # Full restaurant view
│   │       ├── MapView.tsx             # Location list (map placeholder)
│   │       ├── ReviewsPanel.tsx        # Star ratings + reviews
│   │       ├── Confirmation.tsx        # Success/error states
│   │       ├── PlanEditor.tsx          # Timeline plan editor
│   │       ├── MusicPlayer.tsx         # Music player UI
│   │       └── SplitView.tsx           # Side-by-side panels
│   │
│   ├── hooks/
│   │   └── useWebSocket.ts         # WS connection + auto-reconnect
│   │
│   ├── lib/
│   │   ├── types.ts                # TypeScript types (UIAction, Restaurant)
│   │   ├── ws-protocol.ts          # WS message type definitions
│   │   └── constants.ts            # WS_URL, reconnect config
│   │
│   └── stores/
│       └── session.ts              # Zustand store (messages, UI state)
│
├── docs/
│   └── SuggestionChips.md         # SuggestionChips: how it works, cost, performance
├── package.json
├── tsconfig.json
├── next.config.ts
└── postcss.config.mjs
```

---

## Environment Variables

| Variable | Default | Description |
|:---------|:--------|:------------|
| `NEXT_PUBLIC_WS_URL` | `ws://localhost:8000/ws` | WebSocket endpoint for backend |

Create a `.env.local` file if you need to override:

```bash
NEXT_PUBLIC_WS_URL=ws://your-backend.com/ws
```

---

## Architecture

### Declarative UI Rendering

The frontend is a **pure renderer** — it contains **no business logic**. All decisions (what to show, when, why) are made by the backend agent. The frontend simply maps `UIAction` types to React components.

```typescript
// Backend sends:
{
  "type": "ui_update",
  "data": {
    "actions": [
      {
        "action": "SHOW_RESTAURANT_LIST",
        "priority": "primary",
        "data": { "restaurants": [...] }
      }
    ]
  }
}

// Frontend renders:
<RestaurantList restaurants={data.restaurants} />
```

### WebSocket Protocol

**Frontend → Backend:**

```typescript
{ type: "text_input",    data: { text: "Find sushi in Shibuya" } }
{ type: "chip_selected", data: { chip: "Show reviews" } }
{ type: "feedback",      data: { trace_id: "...", score: "up" } }
```

**Backend → Frontend:**

```typescript
{ type: "voice_response", data: { text: "I found 5 sushi places..." } }
{ type: "ui_update",      data: { actions: [...] } }
{ type: "suggestions",    data: { chips: ["Show map", "Private rooms"] } }
{ type: "status",         data: { state: "thinking" | "idle" } }
{ type: "error",          data: { message: "..." } }
```

### State Management

Uses **Zustand** for global state:

- `connectionStatus`: `"connecting" | "connected" | "disconnected"`
- `agentStatus`: `"idle" | "thinking" | "speaking"`
- `messages`: Chat transcript (user + assistant)
- `currentUIActions`: Active UI panels to render
- `currentSuggestions`: Suggestion chips to display

### UI Action Types

| Action | Component | Description |
|:-------|:----------|:------------|
| `SHOW_RESTAURANT_LIST` | `RestaurantList` | Grid of restaurant cards |
| `SHOW_RESTAURANT_DETAIL` | `RestaurantDetail` | Full restaurant view |
| `SHOW_MAP` | `MapView` | Location markers (placeholder) |
| `SHOW_REVIEWS` | `ReviewsPanel` | Star ratings + reviews |
| `SHOW_CONFIRMATION` | `Confirmation` | Success/error/pending state |
| `SHOW_PLAN_EDITOR` | `PlanEditor` | Timeline plan editor |
| `SHOW_MUSIC_PLAYER` | `MusicPlayer` | Music player UI |
| `SPLIT_VIEW` | `SplitView` | Side-by-side panels |
| `CLEAR_UI` | — | Clears all panels |

---

## Development

### Commands

| Command | Description |
|:--------|:------------|
| `npm run dev` | Start dev server (hot reload) |
| `npm run build` | Build for production |
| `npm start` | Start production server |
| `npm run lint` | Run ESLint |

### Adding a New Panel

1. Create component in `src/components/panels/YourPanel.tsx`
2. Add case in `src/components/DynamicContent.tsx`:

```typescript
case "SHOW_YOUR_PANEL":
  return <YourPanel {...action.data} />;
```

3. Update `src/lib/types.ts` to add the action type to `UIActionType`

### Styling

Uses **Tailwind CSS v4** with custom CSS variables defined in `globals.css`:

```css
--color-bg: #0a0a0f
--color-surface: #131320
--color-accent: #6c5ce7
--color-text: #e8e6f0
```

All components use these variables for consistent theming.

---

## Testing the UI

1. Start the backend:

```bash
cd ../backend
uvicorn src.main:app --reload --port 8000
```

2. Start the frontend:

```bash
npm run dev
```

3. Open `http://localhost:3000` and type a query:

```
"Find Italian restaurants in Shibuya"
"渋谷でイタリアンを探して"
"個室のある居酒屋"
```

The agent will respond with structured output that renders as restaurant cards, maps, and suggestion chips.

---

## Phase 2 Enhancements

- **Voice input:** Integrate LiveKit for real-time STT
- **Voice output:** TTS playback with waveform visualization
- **Interactive map:** Replace placeholder with Leaflet or Google Maps
- **Animations:** Framer Motion for smooth transitions
- **Mobile:** Responsive design + PWA support

See [../docs/PHASED_ROADMAP.md](../docs/PHASED_ROADMAP.md) for full roadmap.
