"""
HTMX Chat Clone — A ChatGPT/Claude UI clone with canned responses.
Uses Flask + HTMX for a hypermedia-driven approach with SSE streaming.
Run with: python app.py
"""

import time
import uuid
import markdown
from flask import Flask, render_template, request, Response, session, jsonify

app = Flask(__name__)
app.secret_key = "chat-clone-secret-key-change-in-production"

# ---------------------------------------------------------------------------
# Canned responses and thinking traces
# ---------------------------------------------------------------------------
CANNED_RESPONSES = [
    "That's a great question! Let me think about this...\n\nThe key insight here is that **complex problems** often have surprisingly simple solutions when you break them down into smaller pieces.\n\nHere are a few approaches:\n1. Start with the fundamentals\n2. Build incrementally\n3. Test at each step\n\nWould you like me to elaborate on any of these?",
    "I'd be happy to help with that!\n\nHere's a quick overview:\n\n```python\ndef solve(problem):\n    # Break it down\n    steps = analyze(problem)\n    for step in steps:\n        execute(step)\n    return result\n```\n\nThe important thing is to approach it **systematically**. Let me know if you need more details.",
    "Interesting topic! There are several perspectives to consider:\n\n- **First**, the historical context matters quite a bit\n- **Second**, modern approaches have evolved significantly\n- **Third**, practical applications vary by domain\n\n> \"The best way to predict the future is to invent it.\" — Alan Kay\n\nWhat specific aspect would you like to explore further?",
    "Great question! Let me break this down:\n\n### Overview\nThis is a common challenge that many developers face. The solution involves understanding a few core concepts.\n\n### Key Points\n1. **Simplicity** is usually better than complexity\n2. **Readability** matters more than cleverness\n3. **Testing** catches issues early\n\n### Example\n```javascript\nconst solution = (input) => {\n  return input\n    .filter(item => item.isValid)\n    .map(item => transform(item))\n    .reduce((acc, val) => acc + val, 0);\n};\n```\n\nHope that helps! Feel free to ask follow-up questions.",
    "That's a fascinating area! Let me share some thoughts.\n\nThe fundamental challenge here is balancing **trade-offs**. Every engineering decision involves choosing between:\n\n| Option | Pros | Cons |\n|--------|------|------|\n| Approach A | Simple, fast | Limited flexibility |\n| Approach B | Flexible | More complex |\n| Approach C | Balanced | Moderate on both |\n\nIn my experience, *starting simple and iterating* tends to produce the best outcomes. You can always add complexity later, but removing it is much harder.\n\nWhat constraints are you working with?",
]

THINKING_TRACES = [
    {
        "reasoning": "The user is asking about problem-solving approaches. I should break this down into fundamental principles and provide actionable steps.",
        "tools": [{"name": "web_search", "query": "effective problem-solving frameworks"}],
    },
    {
        "reasoning": "This looks like a coding question. I need to provide a clear, working example with good structure.",
        "tools": [
            {"name": "code_interpreter", "query": "generate solution template"},
            {"name": "web_search", "query": "best practices code organization"},
        ],
    },
    {
        "reasoning": "The user wants to explore a topic from multiple angles. I should consider historical context, modern developments, and practical applications.",
        "tools": [
            {"name": "web_search", "query": "topic historical context"},
            {"name": "web_search", "query": "modern approaches and developments"},
        ],
    },
    {
        "reasoning": "This is a common developer challenge. I should provide an overview, key principles, and a concrete code example.",
        "tools": [
            {"name": "code_interpreter", "query": "analyze code patterns"},
            {"name": "file_analysis", "query": "review best practices"},
        ],
    },
    {
        "reasoning": "The user is asking about trade-offs in engineering decisions. I should present this in a structured comparison format.",
        "tools": [{"name": "web_search", "query": "engineering trade-off analysis"}],
    },
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


def pick_response(text: str) -> tuple[str, dict]:
    """Pick a canned response and thinking trace by hashing the user message."""
    char_sum = sum(ord(c) for c in text)
    idx = char_sum % len(CANNED_RESPONSES)
    return CANNED_RESPONSES[idx], THINKING_TRACES[idx]


def render_markdown(text: str) -> str:
    """Convert markdown to HTML."""
    return markdown.markdown(
        text,
        extensions=["fenced_code", "tables", "nl2br"],
    )


def get_conversations():
    """Get conversations from session, initializing if needed."""
    if "conversations" not in session:
        session["conversations"] = [
            {"id": str(uuid.uuid4()), "title": "New conversation", "messages": []}
        ]
    if "active_id" not in session:
        session["active_id"] = session["conversations"][0]["id"]
    if "selected_model" not in session:
        session["selected_model"] = "Claude Sonnet 4"
    if "enabled_tools" not in session:
        session["enabled_tools"] = ["web_search", "code_interpreter"]
    return session["conversations"]


def get_active_conversation():
    """Get the currently active conversation."""
    convos = get_conversations()
    active_id = session.get("active_id")
    for conv in convos:
        if conv["id"] == active_id:
            return conv
    return convos[0]


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    """Render the main chat page."""
    convos = get_conversations()
    active = get_active_conversation()
    return render_template(
        "index.html",
        conversations=convos,
        active_conversation=active,
        active_id=session.get("active_id"),
        models=MODELS,
        selected_model=session.get("selected_model", "Claude Sonnet 4"),
        tools=TOOLS,
        enabled_tools=session.get("enabled_tools", []),
        quick_actions=QUICK_ACTIONS,
        render_markdown=render_markdown,
    )


@app.route("/send", methods=["POST"])
def send_message():
    """Handle sending a message and stream the response via SSE."""
    message = request.form.get("message", "").strip()
    files = request.form.get("files", "")

    if not message:
        return "", 204

    conv = get_active_conversation()

    # Build user message with file prefix
    file_prefix = ""
    if files:
        file_prefix = f"📎 {files}\n\n"
    user_content = file_prefix + message

    # Update title if first message
    if not conv["messages"]:
        conv["title"] = message[:40] + ("..." if len(message) > 40 else "")

    # Add user message
    user_msg = {"id": str(uuid.uuid4()), "role": "user", "content": user_content}
    conv["messages"].append(user_msg)
    session.modified = True

    # Get response and trace
    response_text, trace = pick_response(message)

    def generate():
        # Send user message HTML first
        user_html = render_message_html(user_msg)
        yield f"data: {user_html}\n\n"

        # Send thinking indicator
        yield f'data: <div id="thinking" class="message-row message-row-assistant"><div class="avatar avatar-assistant">C</div><div class="message-bubble bubble-assistant"><div class="thinking-indicator"><div class="thinking-dot"></div><div class="thinking-dot"></div><div class="thinking-dot"></div></div></div></div>\n\n'

        time.sleep(0.8)  # Thinking delay

        # Build thinking trace HTML
        trace_html = render_thinking_trace_html(trace)

        # Stream the response character by character
        partial = ""
        msg_id = str(uuid.uuid4())
        for i, char in enumerate(response_text):
            partial += char
            content_html = render_markdown(partial)
            msg_html = f'''<div id="msg-{msg_id}" class="message-row message-row-assistant" hx-swap-oob="true">
                <div class="avatar avatar-assistant">C</div>
                <div class="message-bubble bubble-assistant">
                    {trace_html}
                    <div class="message-text markdown-body">{content_html}</div>
                </div>
            </div>'''
            # Replace thinking indicator on first char
            if i == 0:
                msg_html = f'<div id="thinking" hx-swap-oob="true" style="display:none;"></div>' + msg_html
            yield f"data: {msg_html}\n\n"
            time.sleep(0.02)

        # Save assistant message to session
        assistant_msg = {
            "id": msg_id,
            "role": "assistant",
            "content": response_text,
            "thinking": trace,
        }
        conv["messages"].append(assistant_msg)
        session.modified = True

        # Signal end of stream
        yield "data: <div id=\"stream-end\"></div>\n\n"

    return Response(generate(), mimetype="text/event-stream")


def render_message_html(msg):
    """Render a single message as HTML."""
    if msg["role"] == "user":
        content = msg["content"].replace("\n", "<br>")
        return f'''<div class="message-row message-row-user">
            <div class="message-bubble bubble-user">
                <div class="message-text">{content}</div>
            </div>
            <div class="avatar avatar-user">U</div>
        </div>'''
    else:
        trace_html = ""
        if msg.get("thinking"):
            trace_html = render_thinking_trace_html(msg["thinking"])
        content_html = render_markdown(msg["content"])
        return f'''<div class="message-row message-row-assistant">
            <div class="avatar avatar-assistant">C</div>
            <div class="message-bubble bubble-assistant">
                {trace_html}
                <div class="message-text markdown-body">{content_html}</div>
            </div>
        </div>'''


def render_thinking_trace_html(trace):
    """Render thinking trace as collapsible HTML."""
    tools_html = ""
    if trace.get("tools"):
        tools_html = '<div class="thinking-trace-section"><div class="thinking-trace-section-title">Tool Use</div>'
        for tool in trace["tools"]:
            tools_html += f'''<div class="thinking-trace-tool">
                <span class="tool-call-icon">⚡</span>
                <span class="tool-call-name">{tool["name"]}</span>
                <span class="tool-call-query">("{tool["query"]}")</span>
            </div>'''
        tools_html += '</div>'

    return f'''<details class="thinking-trace">
        <summary class="thinking-trace-toggle">
            <span class="thinking-trace-icon">💭</span>
            <span class="thinking-trace-label">Thinking...</span>
        </summary>
        <div class="thinking-trace-content">
            <div class="thinking-trace-section">
                <div class="thinking-trace-section-title">Reasoning</div>
                <p class="thinking-trace-reasoning">{trace["reasoning"]}</p>
            </div>
            {tools_html}
        </div>
    </details>'''


@app.route("/new-conversation", methods=["POST"])
def new_conversation():
    """Create a new conversation and return updated sidebar + chat area."""
    convos = get_conversations()
    new_conv = {"id": str(uuid.uuid4()), "title": "New conversation", "messages": []}
    convos.insert(0, new_conv)
    session["active_id"] = new_conv["id"]
    session.modified = True

    return render_template(
        "partials/layout.html",
        conversations=convos,
        active_conversation=new_conv,
        active_id=new_conv["id"],
        models=MODELS,
        selected_model=session.get("selected_model"),
        tools=TOOLS,
        enabled_tools=session.get("enabled_tools", []),
        quick_actions=QUICK_ACTIONS,
        render_markdown=render_markdown,
    )


@app.route("/switch-conversation/<conv_id>", methods=["POST"])
def switch_conversation(conv_id):
    """Switch to a different conversation."""
    convos = get_conversations()
    session["active_id"] = conv_id
    session.modified = True

    active = None
    for conv in convos:
        if conv["id"] == conv_id:
            active = conv
            break
    if not active:
        active = convos[0]

    return render_template(
        "partials/layout.html",
        conversations=convos,
        active_conversation=active,
        active_id=conv_id,
        models=MODELS,
        selected_model=session.get("selected_model"),
        tools=TOOLS,
        enabled_tools=session.get("enabled_tools", []),
        quick_actions=QUICK_ACTIONS,
        render_markdown=render_markdown,
    )


@app.route("/update-options", methods=["POST"])
def update_options():
    """Update model and tool selections."""
    session["selected_model"] = request.form.get("model", "Claude Sonnet 4")
    session["enabled_tools"] = request.form.getlist("tools")
    session.modified = True
    return f'<span class="model-badge">{session["selected_model"]}</span>'


@app.route("/quick-action", methods=["POST"])
def quick_action():
    """Return prefill text for quick action."""
    text = request.form.get("text", "")
    return f'<input type="hidden" id="prefill-value" value="{text} " />'


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
