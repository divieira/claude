"""
Chat Clone API — FastAPI Backend
Serves REST API + SSE streaming for the React frontend.
Run with: uvicorn app:app --reload --port 8000
"""

import asyncio
import uuid
import markdown
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Chat Clone API")

# CORS for local development (React on :5173, API on :8000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
CANNED_RESPONSES = [
    "That's a great question! Let me think about this...\n\nThe key insight here is that **complex problems** often have surprisingly simple solutions when you break them down into smaller pieces.\n\nHere are a few approaches:\n1. Start with the fundamentals\n2. Build incrementally\n3. Test at each step\n\nWould you like me to elaborate on any of these?",
    "I'd be happy to help with that!\n\nHere's a quick overview:\n\n```python\ndef solve(problem):\n    # Break it down\n    steps = analyze(problem)\n    for step in steps:\n        execute(step)\n    return result\n```\n\nThe important thing is to approach it **systematically**. Let me know if you need more details.",
    "Interesting topic! There are several perspectives to consider:\n\n- **First**, the historical context matters quite a bit\n- **Second**, modern approaches have evolved significantly\n- **Third**, practical applications vary by domain\n\n> \"The best way to predict the future is to invent it.\" — Alan Kay\n\nWhat specific aspect would you like to explore further?",
    "Great question! Let me break this down:\n\n### Overview\nThis is a common challenge that many developers face. The solution involves understanding a few core concepts.\n\n### Key Points\n1. **Simplicity** is usually better than complexity\n2. **Readability** matters more than cleverness\n3. **Testing** catches issues early\n\n### Example\n```javascript\nconst solution = (input) => {\n  return input\n    .filter(item => item.isValid)\n    .map(item => transform(item))\n    .reduce((acc, val) => acc + val, 0);\n};\n```\n\nHope that helps! Feel free to ask follow-up questions.",
    "That's a fascinating area! Let me share some thoughts.\n\nThe fundamental challenge here is balancing **trade-offs**. Every engineering decision involves choosing between:\n\n| Option | Pros | Cons |\n|--------|------|------|\n| Approach A | Simple, fast | Limited flexibility |\n| Approach B | Flexible | More complex |\n| Approach C | Balanced | Moderate on both |\n\nIn my experience, *starting simple and iterating* tends to produce the best outcomes. You can always add complexity later, but removing it is much harder.\n\nWhat constraints are you working with?",
]

THINKING_TRACES = [
    {"reasoning": "The user is asking about problem-solving approaches. I should break this down into fundamental principles and provide actionable steps.", "tools": [{"name": "web_search", "query": "effective problem-solving frameworks"}]},
    {"reasoning": "This looks like a coding question. I need to provide a clear, working example with good structure.", "tools": [{"name": "code_interpreter", "query": "generate solution template"}, {"name": "web_search", "query": "best practices code organization"}]},
    {"reasoning": "The user wants to explore a topic from multiple angles. I should consider historical context, modern developments, and practical applications.", "tools": [{"name": "web_search", "query": "topic historical context"}, {"name": "web_search", "query": "modern approaches and developments"}]},
    {"reasoning": "This is a common developer challenge. I should provide an overview, key principles, and a concrete code example.", "tools": [{"name": "code_interpreter", "query": "analyze code patterns"}, {"name": "file_analysis", "query": "review best practices"}]},
    {"reasoning": "The user is asking about trade-offs in engineering decisions. I should present this in a structured comparison format.", "tools": [{"name": "web_search", "query": "engineering trade-off analysis"}]},
]

MODELS = ["Claude Opus 4", "Claude Sonnet 4", "Claude Haiku", "GPT-4o", "GPT-4o mini"]

TOOLS = [
    {"id": "web_search", "name": "Web Search", "icon": "🔍"},
    {"id": "code_interpreter", "name": "Code Interpreter", "icon": "💻"},
    {"id": "image_gen", "name": "Image Generation", "icon": "🎨"},
    {"id": "file_analysis", "name": "File Analysis", "icon": "📄"},
]

QUICK_ACTIONS = [
    {"label": "✍️ Write code", "text": "Write a Python function that"},
    {"label": "💡 Explain", "text": "Explain the concept of"},
    {"label": "📝 Summarize", "text": "Summarize the following text:"},
    {"label": "🐛 Debug", "text": "Help me debug this code:"},
    {"label": "🔄 Refactor", "text": "Refactor this code to be cleaner:"},
    {"label": "📊 Analyze", "text": "Analyze the following data:"},
]

# In-memory store (in production, use a database)
sessions: dict[str, dict] = {}


def get_session(session_id: str | None) -> tuple[str, dict]:
    """Get or create session."""
    if session_id and session_id in sessions:
        return session_id, sessions[session_id]

    new_id = str(uuid.uuid4())
    conv_id = str(uuid.uuid4())
    sessions[new_id] = {
        "conversations": [{"id": conv_id, "title": "New conversation", "messages": []}],
        "active_id": conv_id,
        "selected_model": "Claude Sonnet 4",
        "enabled_tools": ["web_search", "code_interpreter"],
    }
    return new_id, sessions[new_id]


def pick_response(text: str) -> tuple[str, dict]:
    """Pick a canned response and thinking trace by hashing the user message."""
    idx = sum(ord(c) for c in text) % len(CANNED_RESPONSES)
    return CANNED_RESPONSES[idx], THINKING_TRACES[idx]


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------
class SendMessageRequest(BaseModel):
    message: str
    files: list[str] = []


class UpdateOptionsRequest(BaseModel):
    model: str
    tools: list[str]


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.get("/api/init")
async def init(request: Request):
    """Initialize session and return all data needed to render the UI."""
    session_id = request.cookies.get("session_id")
    session_id, session = get_session(session_id)

    return {
        "session_id": session_id,
        "conversations": session["conversations"],
        "active_id": session["active_id"],
        "selected_model": session["selected_model"],
        "enabled_tools": session["enabled_tools"],
        "models": MODELS,
        "tools": TOOLS,
        "quick_actions": QUICK_ACTIONS,
    }


@app.post("/api/conversations")
async def create_conversation(request: Request):
    """Create a new conversation."""
    session_id = request.cookies.get("session_id")
    session_id, session = get_session(session_id)

    new_conv = {"id": str(uuid.uuid4()), "title": "New conversation", "messages": []}
    session["conversations"].insert(0, new_conv)
    session["active_id"] = new_conv["id"]

    return {"conversation": new_conv, "active_id": new_conv["id"]}


@app.post("/api/conversations/{conv_id}/activate")
async def activate_conversation(conv_id: str, request: Request):
    """Switch to a different conversation."""
    session_id = request.cookies.get("session_id")
    session_id, session = get_session(session_id)

    session["active_id"] = conv_id
    conv = next((c for c in session["conversations"] if c["id"] == conv_id), None)

    return {"conversation": conv, "active_id": conv_id}


@app.post("/api/conversations/{conv_id}/messages")
async def send_message(conv_id: str, body: SendMessageRequest, request: Request):
    """Send a message and stream the response via SSE."""
    session_id = request.cookies.get("session_id")
    session_id, session = get_session(session_id)

    conv = next((c for c in session["conversations"] if c["id"] == conv_id), None)
    if not conv:
        return {"error": "Conversation not found"}, 404

    message = body.message.strip()
    if not message:
        return {"error": "Empty message"}, 400

    # Build user message
    file_prefix = f"📎 {', '.join(body.files)}\n\n" if body.files else ""
    user_content = file_prefix + message

    # Update title if first message
    if not conv["messages"]:
        conv["title"] = message[:40] + ("..." if len(message) > 40 else "")

    # Add user message
    user_msg = {"id": str(uuid.uuid4()), "role": "user", "content": user_content}
    conv["messages"].append(user_msg)

    # Get response
    response_text, trace = pick_response(message)

    async def generate():
        import json

        # Send user message event
        yield f"event: user_message\ndata: {json.dumps(user_msg)}\n\n"

        # Send thinking start
        yield f"event: thinking_start\ndata: {json.dumps(trace)}\n\n"

        await asyncio.sleep(0.8)

        # Stream response token by token
        msg_id = str(uuid.uuid4())
        partial = ""
        for char in response_text:
            partial += char
            yield f"event: token\ndata: {json.dumps({'id': msg_id, 'content': partial})}\n\n"
            await asyncio.sleep(0.02)

        # Send complete message
        assistant_msg = {"id": msg_id, "role": "assistant", "content": response_text, "thinking": trace}
        conv["messages"].append(assistant_msg)
        yield f"event: message_complete\ndata: {json.dumps(assistant_msg)}\n\n"

        # Send updated conversation title
        yield f"event: title_update\ndata: {json.dumps({'title': conv['title']})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


@app.patch("/api/options")
async def update_options(body: UpdateOptionsRequest, request: Request):
    """Update model and tool selections."""
    session_id = request.cookies.get("session_id")
    session_id, session = get_session(session_id)

    session["selected_model"] = body.model
    session["enabled_tools"] = body.tools

    return {"selected_model": body.model, "enabled_tools": body.tools}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
