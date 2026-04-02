"""
HTMX Chat Clone — FastAPI Backend
A ChatGPT/Claude UI clone with canned responses.
Run with: uvicorn app:app --reload --port 5001
"""

import asyncio
import uuid
import markdown
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

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
    ("✍️ Write code", "Write a Python function that"),
    ("💡 Explain", "Explain the concept of"),
    ("📝 Summarize", "Summarize the following text:"),
    ("🐛 Debug", "Help me debug this code:"),
    ("🔄 Refactor", "Refactor this code to be cleaner:"),
    ("📊 Analyze", "Analyze the following data:"),
]

# In-memory session store
sessions: dict[str, dict] = {}


def get_session(request: Request) -> dict:
    """Get or create session from cookie."""
    session_id = request.cookies.get("session_id")
    if session_id and session_id in sessions:
        return sessions[session_id]
    session_id = str(uuid.uuid4())
    sessions[session_id] = {
        "id": session_id,
        "conversations": [{"id": str(uuid.uuid4()), "title": "New conversation", "messages": []}],
        "active_id": None,
        "selected_model": "Claude Sonnet 4",
        "enabled_tools": ["web_search", "code_interpreter"],
    }
    sessions[session_id]["active_id"] = sessions[session_id]["conversations"][0]["id"]
    return sessions[session_id]


def get_active_conversation(session: dict) -> dict:
    """Get the active conversation from session."""
    for conv in session["conversations"]:
        if conv["id"] == session["active_id"]:
            return conv
    return session["conversations"][0]


def pick_response(text: str) -> tuple[str, dict]:
    """Pick a canned response and thinking trace by hashing the user message."""
    idx = sum(ord(c) for c in text) % len(CANNED_RESPONSES)
    return CANNED_RESPONSES[idx], THINKING_TRACES[idx]


def render_markdown(text: str) -> str:
    """Convert markdown to HTML."""
    return markdown.markdown(text, extensions=["fenced_code", "tables", "nl2br"])


def render_component(name: str, **kwargs) -> str:
    """Render a component template and return HTML string."""
    template = templates.get_template(f"components/{name}.html")
    return template.module


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Render the main chat page."""
    session = get_session(request)
    active = get_active_conversation(session)
    response = templates.TemplateResponse("index.html", {
        "request": request,
        "conversations": session["conversations"],
        "active_conversation": active,
        "active_id": session["active_id"],
        "models": MODELS,
        "selected_model": session["selected_model"],
        "tools": TOOLS,
        "enabled_tools": session["enabled_tools"],
        "quick_actions": QUICK_ACTIONS,
        "render_markdown": render_markdown,
    })
    response.set_cookie("session_id", session["id"], httponly=True)
    return response


@app.post("/send")
async def send_message(request: Request, message: str = Form(""), files: str = Form("")):
    """Handle sending a message and stream the response via SSE."""
    message = message.strip()
    if not message:
        return HTMLResponse("", status_code=204)

    session = get_session(request)
    conv = get_active_conversation(session)

    # Build user message
    file_prefix = f"📎 {files}\n\n" if files else ""
    user_content = file_prefix + message

    if not conv["messages"]:
        conv["title"] = message[:40] + ("..." if len(message) > 40 else "")

    user_msg = {"id": str(uuid.uuid4()), "role": "user", "content": user_content}
    conv["messages"].append(user_msg)

    response_text, trace = pick_response(message)

    # Get component templates
    msg_tpl = templates.get_template("components/message.html")
    thinking_tpl = templates.get_template("components/thinking.html")

    async def generate():
        # User message
        user_html = msg_tpl.module.user_message(user_msg)
        yield f"data: {user_html}\n\n"

        # Thinking indicator
        thinking_html = msg_tpl.module.thinking_indicator()
        yield f"data: {thinking_html}\n\n"

        await asyncio.sleep(0.8)

        # Render thinking trace once
        trace_html = thinking_tpl.module.thinking_trace(trace)

        # Stream response
        partial = ""
        msg_id = str(uuid.uuid4())
        for i, char in enumerate(response_text):
            partial += char
            content_html = render_markdown(partial)

            msg = {"id": msg_id, "oob": True}
            assistant_html = msg_tpl.module.assistant_message(msg, content_html, trace_html)

            if i == 0:
                hide_html = msg_tpl.module.hide_thinking()
                yield f"data: {hide_html}{assistant_html}\n\n"
            else:
                yield f"data: {assistant_html}\n\n"

            await asyncio.sleep(0.02)

        # Save to session
        assistant_msg = {"id": msg_id, "role": "assistant", "content": response_text, "thinking": trace}
        conv["messages"].append(assistant_msg)

        yield 'data: <div id="stream-end"></div>\n\n'

    return StreamingResponse(generate(), media_type="text/event-stream")


@app.post("/new-conversation", response_class=HTMLResponse)
async def new_conversation(request: Request):
    """Create a new conversation."""
    session = get_session(request)
    new_conv = {"id": str(uuid.uuid4()), "title": "New conversation", "messages": []}
    session["conversations"].insert(0, new_conv)
    session["active_id"] = new_conv["id"]

    return templates.TemplateResponse("partials/layout.html", {
        "request": request,
        "conversations": session["conversations"],
        "active_conversation": new_conv,
        "active_id": new_conv["id"],
        "models": MODELS,
        "selected_model": session["selected_model"],
        "tools": TOOLS,
        "enabled_tools": session["enabled_tools"],
        "quick_actions": QUICK_ACTIONS,
        "render_markdown": render_markdown,
    })


@app.post("/switch-conversation/{conv_id}", response_class=HTMLResponse)
async def switch_conversation(request: Request, conv_id: str):
    """Switch to a different conversation."""
    session = get_session(request)
    session["active_id"] = conv_id
    active = get_active_conversation(session)

    return templates.TemplateResponse("partials/layout.html", {
        "request": request,
        "conversations": session["conversations"],
        "active_conversation": active,
        "active_id": conv_id,
        "models": MODELS,
        "selected_model": session["selected_model"],
        "tools": TOOLS,
        "enabled_tools": session["enabled_tools"],
        "quick_actions": QUICK_ACTIONS,
        "render_markdown": render_markdown,
    })


@app.post("/update-options", response_class=HTMLResponse)
async def update_options(request: Request):
    """Update model and tool selections."""
    form = await request.form()
    session = get_session(request)
    session["selected_model"] = form.get("model", "Claude Sonnet 4")
    session["enabled_tools"] = form.getlist("tools")

    tpl = templates.get_template("components/options.html")
    return HTMLResponse(tpl.module.model_badge(session["selected_model"]))


@app.post("/quick-action", response_class=HTMLResponse)
async def quick_action(request: Request):
    """Return prefill text for quick action."""
    form = await request.form()
    text = form.get("text", "")

    tpl = templates.get_template("components/options.html")
    return HTMLResponse(tpl.module.prefill_input(text))


if __name__ == "__main__":
    import os
    import uvicorn
    port = int(os.environ.get("PORT", 5001))
    uvicorn.run(app, host="0.0.0.0", port=port)
