# React + FastAPI Chat Clone

Production-style architecture with React frontend and FastAPI backend communicating via REST API and SSE streaming.

## Running

**Terminal 1 — Backend:**
```bash
cd backend
pip install -r requirements.txt
uvicorn app:app --reload --port 8000
```

**Terminal 2 — Frontend:**
```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

## Architecture

```
┌─────────────────┐     REST/SSE      ┌─────────────────┐
│  React (Vite)   │ ◄───────────────► │    FastAPI      │
│  localhost:5173 │                   │  localhost:8000 │
└─────────────────┘                   └─────────────────┘
        │                                     │
        │ Vite proxy /api → :8000             │ In-memory session store
        │                                     │ SSE streaming responses
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/init` | Initialize session, return UI data |
| POST | `/api/conversations` | Create new conversation |
| POST | `/api/conversations/:id/activate` | Switch conversation |
| POST | `/api/conversations/:id/messages` | Send message (SSE response) |
| PATCH | `/api/options` | Update model/tools |

## SSE Events

The `/messages` endpoint streams these events:

- `user_message` — User message added
- `thinking_start` — Thinking trace data
- `token` — Streaming token (partial content)
- `message_complete` — Full assistant message
- `title_update` — Conversation title changed
