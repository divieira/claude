# Chat Clone — Common Spec

A minimal clone of Claude / ChatGPT, implemented in four UI libraries.

## Essential Features

| # | Feature | Description |
|---|---------|-------------|
| 1 | **Message thread** | Scrollable list of user and assistant messages, visually distinct. |
| 2 | **Text input** | Multi-line input area at the bottom with a Send button. Enter sends; Shift+Enter for newlines (where supported). |
| 3 | **Simulated streaming** | Assistant replies appear token-by-token (typewriter effect) to mimic real LLM streaming. |
| 4 | **Markdown rendering** | Assistant messages render basic Markdown (bold, italic, code blocks, lists). |
| 5 | **Conversation list (sidebar)** | Left sidebar listing past conversations, each titled by its first user message. |
| 6 | **New conversation** | Button to start a fresh conversation. |
| 7 | **Auto-scroll** | Chat scrolls to the bottom when new content arrives. |
| 8 | **Loading indicator** | Visual cue while the assistant is "thinking" (pulsing dots or similar). |
| 9 | **Dark theme** | Dark background with light text, styled after Claude's UI. |
| 10 | **Responsive layout** | Usable on both desktop and mobile widths. |

## Additional Features

| # | Feature | Description |
|---|---------|-------------|
| 11 | **Options panel** | Model selector and tool toggles (cosmetic — doesn't affect responses). |
| 12 | **Quick actions** | Suggestion chips below input to prefill common prompts. |
| 13 | **File upload** | Attach files (displayed in user message, no actual processing). |
| 14 | **Thinking trace** | Collapsible reasoning + tool use display before each response. |

## Non-goals

- Real API calls to an LLM — all responses are canned.
- Authentication, accounts, or persistence beyond the session.
- Actual file processing or image generation.

## Visual Reference

- **Colour palette**: Dark sidebar (`#1a1a2e`), slightly lighter chat area (`#252538`), accent colour (`#d4a574` — warm tan, Claude-like).
- **Message bubbles**: User messages right-aligned with accent background; assistant messages left-aligned with subtle dark background.
- **Typography**: System sans-serif, 15-16 px body.
- **Avatar**: Small circle with "U" / "A" initials.

## Canned Responses

Each implementation uses the same pool of canned assistant replies to keep behaviour comparable.
The assistant picks a response by hashing the user message or cycling through the pool.

## Implementations

| Directory | Library | Run command |
|-----------|---------|-------------|
| `react/` | React 18 + Vite | `npm install && npm run dev` |
| `streamlit/` | Streamlit | `pip install -r requirements.txt && streamlit run app.py` |
| `gradio/` | Gradio | `pip install -r requirements.txt && python app.py` |
| `htmx/` | Flask + HTMX | `pip install -r requirements.txt && python app.py` |
