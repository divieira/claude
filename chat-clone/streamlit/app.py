"""
Streamlit Chat Clone — A ChatGPT/Claude UI clone with canned responses.
Run with: streamlit run app.py
"""

import time
import streamlit as st

# ---------------------------------------------------------------------------
# Canned responses
# ---------------------------------------------------------------------------
CANNED_RESPONSES = [
    "That's a great question! Let me think about this...\n\nThe key insight here is that **complex problems** often have surprisingly simple solutions when you break them down into smaller pieces.\n\nHere are a few approaches:\n1. Start with the fundamentals\n2. Build incrementally\n3. Test at each step\n\nWould you like me to elaborate on any of these?",
    "I'd be happy to help with that!\n\nHere's a quick overview:\n\n```python\ndef solve(problem):\n    # Break it down\n    steps = analyze(problem)\n    for step in steps:\n        execute(step)\n    return result\n```\n\nThe important thing is to approach it **systematically**. Let me know if you need more details.",
    "Interesting topic! There are several perspectives to consider:\n\n- **First**, the historical context matters quite a bit\n- **Second**, modern approaches have evolved significantly\n- **Third**, practical applications vary by domain\n\n> \"The best way to predict the future is to invent it.\" — Alan Kay\n\nWhat specific aspect would you like to explore further?",
    "Great question! Let me break this down:\n\n### Overview\nThis is a common challenge that many developers face. The solution involves understanding a few core concepts.\n\n### Key Points\n1. **Simplicity** is usually better than complexity\n2. **Readability** matters more than cleverness\n3. **Testing** catches issues early\n\n### Example\n```javascript\nconst solution = (input) => {\n  return input\n    .filter(item => item.isValid)\n    .map(item => transform(item))\n    .reduce((acc, val) => acc + val, 0);\n};\n```\n\nHope that helps! Feel free to ask follow-up questions.",
    "That's a fascinating area! Let me share some thoughts.\n\nThe fundamental challenge here is balancing **trade-offs**. Every engineering decision involves choosing between:\n\n| Option | Pros | Cons |\n|--------|------|------|\n| Approach A | Simple, fast | Limited flexibility |\n| Approach B | Flexible | More complex |\n| Approach C | Balanced | Moderate on both |\n\nIn my experience, *starting simple and iterating* tends to produce the best outcomes. You can always add complexity later, but removing it is much harder.\n\nWhat constraints are you working with?",
]


def pick_response(text: str) -> str:
    """Pick a canned response by hashing the user message (char-code sum % length)."""
    char_sum = sum(ord(c) for c in text)
    return CANNED_RESPONSES[char_sum % len(CANNED_RESPONSES)]


MODELS = ["Claude Opus 4", "Claude Sonnet 4", "Claude Haiku", "GPT-4o", "GPT-4o mini"]

TOOLS = [
    {"id": "web_search", "name": "Web Search", "icon": "🔍"},
    {"id": "code_interpreter", "name": "Code Interpreter", "icon": "💻"},
    {"id": "image_gen", "name": "Image Generation", "icon": "🎨"},
    {"id": "file_analysis", "name": "File Analysis", "icon": "📄"},
]

QUICK_ACTIONS = [
    ("✍️ Write code", "Write a Python function that"),
    ("💡 Explain concept", "Explain the concept of"),
    ("📝 Summarize", "Summarize the following text:"),
    ("🐛 Debug", "Help me debug this code:"),
    ("🔄 Refactor", "Refactor this code to be cleaner:"),
    ("📊 Analyze", "Analyze the following data:"),
]


def stream_tokens(text: str):
    """Generator that yields words one at a time with small delays for streaming."""
    words = text.split(" ")
    for i, word in enumerate(words):
        # Yield the word with a trailing space (except for the last word)
        if i < len(words) - 1:
            yield word + " "
        else:
            yield word
        time.sleep(0.03)


# ---------------------------------------------------------------------------
# Custom CSS
# ---------------------------------------------------------------------------
CUSTOM_CSS = """
<style>
/* ---- Sidebar styling ---- */
section[data-testid="stSidebar"] {
    background-color: #1a1a2e !important;
}
section[data-testid="stSidebar"] .stMarkdown h1,
section[data-testid="stSidebar"] .stMarkdown h2,
section[data-testid="stSidebar"] .stMarkdown h3 {
    color: #d4a574 !important;
}

/* ---- Main chat area ---- */
.stApp, .main .block-container {
    background-color: #252538 !important;
}

/* ---- User message bubble ---- */
div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-user"]) {
    background-color: #d4a574 !important;
    color: #1a1a2e !important;
    border-radius: 12px;
    padding: 0.75rem 1rem;
    margin-bottom: 0.5rem;
}
div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-user"]) p,
div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-user"]) span,
div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-user"]) li {
    color: #1a1a2e !important;
}

/* ---- Assistant message bubble ---- */
div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-assistant"]) {
    background-color: #2d2d44 !important;
    color: #e0e0e0 !important;
    border-radius: 12px;
    padding: 0.75rem 1rem;
    margin-bottom: 0.5rem;
}

/* ---- Avatar circles ---- */
div[data-testid="chatAvatarIcon-user"],
div[data-testid="chatAvatarIcon-assistant"] {
    border-radius: 50% !important;
    width: 2rem !important;
    height: 2rem !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    font-weight: 700 !important;
    font-size: 0.85rem !important;
}
div[data-testid="chatAvatarIcon-user"] {
    background-color: #c4955e !important;
    color: #1a1a2e !important;
}
div[data-testid="chatAvatarIcon-assistant"] {
    background-color: #3d3d5c !important;
    color: #d4a574 !important;
}

/* ---- Chat input styling ---- */
div[data-testid="stChatInput"] {
    background-color: #2d2d44 !important;
    border-color: #3d3d5c !important;
}
div[data-testid="stChatInput"] textarea {
    color: #e0e0e0 !important;
}

/* ---- Sidebar conversation buttons ---- */
section[data-testid="stSidebar"] button[kind="secondary"] {
    background-color: transparent !important;
    color: #b0b0c0 !important;
    border: 1px solid #2d2d44 !important;
    text-align: left !important;
    border-radius: 8px !important;
    transition: background 0.15s ease;
    width: 100% !important;
}
section[data-testid="stSidebar"] button[kind="secondary"]:hover {
    background-color: #2d2d44 !important;
    color: #d4a574 !important;
    border-color: #d4a574 !important;
}

/* ---- Active conversation highlight ---- */
section[data-testid="stSidebar"] button[kind="primary"] {
    background-color: #2d2d44 !important;
    color: #d4a574 !important;
    border: 1px solid #d4a574 !important;
    text-align: left !important;
    border-radius: 8px !important;
    width: 100% !important;
}

/* ---- Welcome card ---- */
.welcome-card {
    text-align: center;
    padding: 3rem 2rem;
    color: #b0b0c0;
}
.welcome-card h2 {
    color: #d4a574 !important;
    margin-bottom: 0.5rem;
}
.welcome-card p {
    font-size: 1.05rem;
}

/* ---- Scrollbar ---- */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #1a1a2e; }
::-webkit-scrollbar-thumb { background: #3d3d5c; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #d4a574; }

/* ---- General typography ---- */
html, body, [class*="css"] {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
                 "Helvetica Neue", Arial, sans-serif;
}

/* ---- Divider in sidebar ---- */
section[data-testid="stSidebar"] hr {
    border-color: #2d2d44 !important;
}

/* ---- Options bar ---- */
.options-bar {
    background: #1a1a2e;
    border: 1px solid #2d2d44;
    border-radius: 12px;
    padding: 0.5rem 1rem;
    margin-bottom: 0.5rem;
}
.model-badge {
    display: inline-block;
    background: #2d2d44;
    color: #8080a0;
    padding: 2px 10px;
    border-radius: 12px;
    font-size: 0.8rem;
    margin-left: 8px;
}

/* ---- Quick action buttons ---- */
div[data-testid="stHorizontalBlock"] .stButton > button[kind="secondary"] {
    font-size: 0.78rem !important;
    padding: 0.2rem 0.8rem !important;
    border-radius: 18px !important;
}
</style>
"""


# ---------------------------------------------------------------------------
# Session state initialization
# ---------------------------------------------------------------------------
def init_state():
    """Ensure all session-state keys exist."""
    if "next_id" not in st.session_state:
        st.session_state.next_id = 1
    if "conversations" not in st.session_state:
        # Start with one empty conversation
        st.session_state.conversations = [
            {"id": 0, "title": "New conversation", "messages": []}
        ]
    if "active_id" not in st.session_state:
        st.session_state.active_id = 0
    if "selected_model" not in st.session_state:
        st.session_state.selected_model = "Claude Sonnet 4"
    if "enabled_tools" not in st.session_state:
        st.session_state.enabled_tools = ["web_search", "code_interpreter"]
    if "prefill" not in st.session_state:
        st.session_state.prefill = ""


def get_active_conversation() -> dict:
    """Return the currently active conversation dict."""
    for conv in st.session_state.conversations:
        if conv["id"] == st.session_state.active_id:
            return conv
    # Fallback: return first conversation
    return st.session_state.conversations[0]


def create_new_conversation():
    """Create a new empty conversation and switch to it."""
    new_id = st.session_state.next_id
    st.session_state.next_id += 1
    st.session_state.conversations.insert(
        0, {"id": new_id, "title": "New conversation", "messages": []}
    )
    st.session_state.active_id = new_id


def switch_conversation(conv_id: int):
    """Switch to a different conversation."""
    st.session_state.active_id = conv_id


# ---------------------------------------------------------------------------
# App layout
# ---------------------------------------------------------------------------
def main():
    st.set_page_config(
        page_title="Claude Chat",
        page_icon="💬",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Inject custom CSS
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

    # Initialize session state
    init_state()

    # ------ Sidebar ------
    with st.sidebar:
        st.markdown("## Claude Chat")
        st.caption(f"Model: {st.session_state.selected_model}")
        if st.button("➕  New Conversation", use_container_width=True, type="primary"):
            create_new_conversation()
            st.rerun()

        st.divider()

        # List conversations (most recent first — order is preserved from inserts)
        for conv in st.session_state.conversations:
            is_active = conv["id"] == st.session_state.active_id
            label = conv["title"]
            # Truncate long titles
            if len(label) > 34:
                label = label[:31] + "..."
            btn_type = "primary" if is_active else "secondary"
            if st.button(
                label,
                key=f"conv_{conv['id']}",
                use_container_width=True,
                type=btn_type,
            ):
                switch_conversation(conv["id"])
                st.rerun()

    # ------ Main chat area ------
    conversation = get_active_conversation()
    messages = conversation["messages"]

    # Show welcome message if conversation is empty
    if not messages:
        st.markdown(
            """
            <div class="welcome-card">
                <h2>Welcome to Claude Chat</h2>
                <p>Start a conversation by typing a message below.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Render existing messages
    for msg in messages:
        avatar = "👤" if msg["role"] == "user" else "🤖"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])

    # Options bar
    with st.expander("⚙️ Options", expanded=False):
        opt_cols = st.columns([2, 3])
        with opt_cols[0]:
            st.session_state.selected_model = st.selectbox(
                "Model",
                MODELS,
                index=MODELS.index(st.session_state.selected_model),
                key="model_select",
            )
        with opt_cols[1]:
            st.markdown("**Tools**")
            tool_cols = st.columns(2)
            new_tools = []
            for i, tool in enumerate(TOOLS):
                with tool_cols[i % 2]:
                    enabled = st.checkbox(
                        f"{tool['icon']} {tool['name']}",
                        value=tool["id"] in st.session_state.enabled_tools,
                        key=f"tool_{tool['id']}",
                    )
                    if enabled:
                        new_tools.append(tool["id"])
            st.session_state.enabled_tools = new_tools

    # Quick action buttons
    qa_cols = st.columns(len(QUICK_ACTIONS))
    for i, (label, prefill_text) in enumerate(QUICK_ACTIONS):
        with qa_cols[i]:
            if st.button(label, key=f"qa_{i}", use_container_width=True):
                st.session_state.prefill = prefill_text
                st.rerun()

    # Chat input
    prefill = st.session_state.pop("prefill", "")
    if prefill:
        prompt = prefill
    else:
        prompt = st.chat_input("Message Claude...")
    if prompt:
        # --- User message ---
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)
        messages.append({"role": "user", "content": prompt})

        # Update conversation title from first user message
        if len(messages) == 1:
            title = prompt if len(prompt) <= 40 else prompt[:37] + "..."
            conversation["title"] = title

        # --- Assistant response (streamed) ---
        response_text = pick_response(prompt)
        with st.chat_message("assistant", avatar="🤖"):
            with st.status("Claude is thinking...", expanded=False):
                time.sleep(0.4)  # brief "thinking" pause
            full_response = st.write_stream(stream_tokens(response_text))

        messages.append({"role": "assistant", "content": full_response})
        st.rerun()


if __name__ == "__main__":
    main()
