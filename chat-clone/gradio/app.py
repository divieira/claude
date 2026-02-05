"""
Gradio Chat Clone - A ChatGPT/Claude UI clone with canned responses.
No real API calls; assistant replies are streamed token-by-token from a
predefined list of markdown-rich responses.
"""

import time
import gradio as gr

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


def pick_response(user_message: str) -> str:
    """Pick a canned response by hashing the user message (char-code sum % length)."""
    char_sum = sum(ord(c) for c in user_message)
    return CANNED_RESPONSES[char_sum % len(CANNED_RESPONSES)]


MODELS = ["Claude Opus 4", "Claude Sonnet 4", "Claude Haiku", "GPT-4o", "GPT-4o mini"]

TOOLS = [
    ("web_search", "🔍 Web Search"),
    ("code_interpreter", "💻 Code Interpreter"),
    ("image_gen", "🎨 Image Generation"),
    ("file_analysis", "📄 File Analysis"),
]

QUICK_ACTIONS = [
    ("✍️ Write code", "Write a Python function that"),
    ("💡 Explain", "Explain the concept of"),
    ("📝 Summarize", "Summarize the following text:"),
    ("🐛 Debug", "Help me debug this code:"),
    ("🔄 Refactor", "Refactor this code to be cleaner:"),
    ("📊 Analyze", "Analyze the following data:"),
]


# ---------------------------------------------------------------------------
# Custom CSS -- dark Claude-like theme
# ---------------------------------------------------------------------------
CUSTOM_CSS = """
/* ── Global ────────────────────────────────────────────────────────────── */
body, .gradio-container {
    background-color: #252538 !important;
    color: #e0e0e0 !important;
    font-family: 'Inter', 'Segoe UI', system-ui, -apple-system, sans-serif !important;
}
.gradio-container {
    max-width: 1400px !important;
}

/* ── Sidebar ───────────────────────────────────────────────────────────── */
#sidebar {
    background-color: #1a1a2e !important;
    border-right: 1px solid #333355 !important;
    border-radius: 12px !important;
    padding: 16px !important;
    min-height: 85vh !important;
}
#sidebar .block {
    background: transparent !important;
    border: none !important;
}
#new-convo-btn {
    background-color: #d4a574 !important;
    color: #1a1a2e !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    padding: 10px 16px !important;
    font-size: 0.95rem !important;
    cursor: pointer !important;
    transition: opacity 0.2s !important;
}
#new-convo-btn:hover {
    opacity: 0.85 !important;
}

/* Sidebar radio / conversation list */
#convo-list {
    background: transparent !important;
}
#convo-list .block {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}
#convo-list label {
    background-color: #252538 !important;
    border: 1px solid #333355 !important;
    border-radius: 8px !important;
    color: #ccc !important;
    margin-bottom: 4px !important;
    padding: 10px 12px !important;
    cursor: pointer !important;
    transition: background-color 0.2s, border-color 0.2s !important;
    font-size: 0.9rem !important;
}
#convo-list label:hover {
    background-color: #2d2d44 !important;
    border-color: #d4a574 !important;
}
#convo-list label.selected {
    background-color: #2d2d44 !important;
    border-color: #d4a574 !important;
    color: #d4a574 !important;
}
#convo-list .wrap {
    gap: 4px !important;
}

/* Hide radio circles */
#convo-list input[type="radio"] {
    display: none !important;
}

/* Sidebar heading */
#sidebar-title {
    color: #d4a574 !important;
    font-size: 1.2rem !important;
    font-weight: 700 !important;
    margin-bottom: 12px !important;
    text-align: center !important;
}
#sidebar-title .block {
    background: transparent !important;
    border: none !important;
}

/* ── Chat area ─────────────────────────────────────────────────────────── */
#chat-area {
    background-color: #252538 !important;
    border-radius: 12px !important;
    padding: 8px !important;
}

/* Chatbot container */
#chatbot {
    background-color: #252538 !important;
    border: none !important;
    border-radius: 12px !important;
    height: 72vh !important;
}
#chatbot .wrapper {
    background-color: #252538 !important;
}
#chatbot .message-wrap {
    background-color: #252538 !important;
}

/* User messages */
#chatbot .message.user {
    background-color: rgba(212, 165, 116, 0.15) !important;
    border: 1px solid rgba(212, 165, 116, 0.3) !important;
    border-radius: 12px !important;
    color: #e0e0e0 !important;
}

/* Assistant messages */
#chatbot .message.bot,
#chatbot .message.assistant {
    background-color: #2d2d44 !important;
    border: 1px solid #3d3d5c !important;
    border-radius: 12px !important;
    color: #e0e0e0 !important;
}

/* Code blocks inside chat */
#chatbot pre {
    background-color: #1a1a2e !important;
    border: 1px solid #333355 !important;
    border-radius: 8px !important;
    color: #e0e0e0 !important;
}
#chatbot code {
    color: #d4a574 !important;
}
#chatbot pre code {
    color: #e0e0e0 !important;
}

/* Tables */
#chatbot table {
    border-collapse: collapse !important;
}
#chatbot th {
    background-color: #1a1a2e !important;
    color: #d4a574 !important;
    border: 1px solid #333355 !important;
    padding: 8px !important;
}
#chatbot td {
    border: 1px solid #333355 !important;
    padding: 8px !important;
}

/* Blockquotes */
#chatbot blockquote {
    border-left: 3px solid #d4a574 !important;
    color: #bbb !important;
    padding-left: 12px !important;
}

/* ── Input area ────────────────────────────────────────────────────────── */
#msg-input textarea {
    background-color: #2d2d44 !important;
    border: 1px solid #3d3d5c !important;
    border-radius: 12px !important;
    color: #e0e0e0 !important;
    padding: 12px 16px !important;
    font-size: 0.95rem !important;
}
#msg-input textarea:focus {
    border-color: #d4a574 !important;
    box-shadow: 0 0 0 2px rgba(212, 165, 116, 0.2) !important;
}
#msg-input textarea::placeholder {
    color: #888 !important;
}

#send-btn {
    background-color: #d4a574 !important;
    color: #1a1a2e !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    min-width: 80px !important;
    cursor: pointer !important;
    transition: opacity 0.2s !important;
}
#send-btn:hover {
    opacity: 0.85 !important;
}

/* ── Misc ──────────────────────────────────────────────────────────────── */
/* Remove default borders from Gradio blocks */
.block {
    border: none !important;
    box-shadow: none !important;
}
#chat-area .block {
    background: transparent !important;
}

/* Label styles */
label, .label-wrap {
    color: #999 !important;
}

/* Scrollbar */
::-webkit-scrollbar {
    width: 6px;
}
::-webkit-scrollbar-track {
    background: #1a1a2e;
}
::-webkit-scrollbar-thumb {
    background: #3d3d5c;
    border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover {
    background: #d4a574;
}

/* Footer hide */
footer {
    display: none !important;
}

/* ── Options area ──────────────────────────────────────────────────────── */
#options-row {
    margin-top: 4px !important;
}
#options-row .block {
    background: transparent !important;
}
#model-select {
    background: transparent !important;
}
#model-select select,
#model-select input {
    background-color: #2d2d44 !important;
    border: 1px solid #3d3d5c !important;
    border-radius: 8px !important;
    color: #e0e0e0 !important;
    font-size: 0.85rem !important;
}
#tool-toggles {
    background: transparent !important;
}
#tool-toggles .wrap {
    gap: 6px !important;
}
#tool-toggles label {
    background-color: #2d2d44 !important;
    border: 1px solid #3d3d5c !important;
    border-radius: 8px !important;
    color: #b0b0c0 !important;
    padding: 4px 10px !important;
    font-size: 0.82rem !important;
    cursor: pointer !important;
    transition: border-color 0.2s, color 0.2s !important;
}
#tool-toggles label.selected {
    border-color: #d4a574 !important;
    color: #d4a574 !important;
}
#tool-toggles input[type="checkbox"] {
    display: none !important;
}
#options-accordion {
    background: transparent !important;
    border: 1px solid #3d3d5c !important;
    border-radius: 10px !important;
    margin-top: 8px !important;
}
#options-accordion .label-wrap {
    color: #8080a0 !important;
    font-size: 0.85rem !important;
    padding: 6px 12px !important;
}
#options-accordion .label-wrap:hover {
    color: #d4a574 !important;
}

/* ── Quick actions ─────────────────────────────────────────────────────── */
#quick-actions {
    margin-top: 4px !important;
    gap: 6px !important;
}
#quick-actions .block {
    background: transparent !important;
}
.quick-action-btn {
    background-color: #2d2d44 !important;
    border: 1px solid #3d3d5c !important;
    border-radius: 18px !important;
    color: #b0b0c0 !important;
    font-size: 0.8rem !important;
    padding: 4px 14px !important;
    cursor: pointer !important;
    transition: border-color 0.2s, color 0.2s !important;
    min-width: auto !important;
}
.quick-action-btn:hover {
    border-color: #d4a574 !important;
    color: #d4a574 !important;
}
"""

# ---------------------------------------------------------------------------
# Helper: build Radio choices from conversation state
# ---------------------------------------------------------------------------

def _convo_choices(conversations):
    """Return a list of display titles for the Radio widget."""
    choices = []
    for i, c in enumerate(conversations):
        title = c["title"] or f"Conversation {i + 1}"
        choices.append(title)
    return choices


def _default_conversations():
    """Return the initial conversation state."""
    return [{"id": 0, "title": "New chat", "messages": []}]


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

def create_app():
    with gr.Blocks(title="Claude Chat Clone") as app:

        # -- State -----------------------------------------------------------
        conversations = gr.State(_default_conversations())
        active_idx = gr.State(0)

        # -- Layout ----------------------------------------------------------
        with gr.Row():
            # ---- Sidebar ---------------------------------------------------
            with gr.Column(scale=1, min_width=220, elem_id="sidebar"):
                gr.Markdown("### Claude", elem_id="sidebar-title")
                new_convo_btn = gr.Button(
                    "  + New Conversation",
                    elem_id="new-convo-btn",
                    size="sm",
                )
                convo_radio = gr.Radio(
                    choices=["New chat"],
                    value="New chat",
                    label="Conversations",
                    elem_id="convo-list",
                    interactive=True,
                )

            # ---- Chat area -------------------------------------------------
            with gr.Column(scale=4, elem_id="chat-area"):
                chatbot = gr.Chatbot(
                    value=[],
                    elem_id="chatbot",
                    label="",
                    show_label=False,
                    avatar_images=(None, None),
                    height=520,
                )
                with gr.Row():
                    msg_input = gr.Textbox(
                        placeholder="Send a message...",
                        show_label=False,
                        elem_id="msg-input",
                        scale=9,
                        container=False,
                        lines=1,
                        max_lines=5,
                    )
                    send_btn = gr.Button(
                        "Send",
                        elem_id="send-btn",
                        scale=1,
                        min_width=80,
                    )
                with gr.Accordion("⚙️ Options", open=False, elem_id="options-accordion"):
                    with gr.Row(elem_id="options-row"):
                        model_select = gr.Dropdown(
                            choices=MODELS,
                            value="Claude Sonnet 4",
                            label="Model",
                            elem_id="model-select",
                            scale=1,
                            interactive=True,
                        )
                        tool_toggles = gr.CheckboxGroup(
                            choices=[t[1] for t in TOOLS],
                            value=["🔍 Web Search", "💻 Code Interpreter"],
                            label="Tools",
                            elem_id="tool-toggles",
                            scale=2,
                            interactive=True,
                        )
                with gr.Row(elem_id="quick-actions"):
                    qa_buttons = []
                    for label, _ in QUICK_ACTIONS:
                        qa_buttons.append(
                            gr.Button(label, size="sm", elem_classes=["quick-action-btn"])
                        )

        # -- Callbacks -------------------------------------------------------

        def _set_title_from_message(convos, idx, user_msg):
            """Set conversation title from first user message (truncated)."""
            if convos[idx]["title"] == "New chat" and user_msg.strip():
                title = user_msg.strip()[:40]
                if len(user_msg.strip()) > 40:
                    title += "..."
                convos[idx]["title"] = title

        def user_submit(user_message, convos, idx):
            """Handle user submitting a message. Returns updated state immediately
            so the UI shows the user message before streaming starts."""
            if not user_message or not user_message.strip():
                # Return current state unchanged
                messages_display = [
                    {"role": m["role"], "content": m["content"]}
                    for m in convos[idx]["messages"]
                ]
                choices = _convo_choices(convos)
                current = choices[idx] if idx < len(choices) else choices[0]
                return (
                    messages_display,
                    "",
                    convos,
                    idx,
                    gr.update(choices=choices, value=current),
                )

            # Add user message to conversation
            convos[idx]["messages"].append(
                {"role": "user", "content": user_message.strip()}
            )
            _set_title_from_message(convos, idx, user_message)

            # Prepare display messages
            messages_display = [
                {"role": m["role"], "content": m["content"]}
                for m in convos[idx]["messages"]
            ]

            choices = _convo_choices(convos)
            current = choices[idx] if idx < len(choices) else choices[0]

            return (
                messages_display,
                "",
                convos,
                idx,
                gr.update(choices=choices, value=current),
            )

        def bot_stream(convos, idx):
            """Generator that streams the assistant response token by token."""
            if not convos[idx]["messages"]:
                return

            last_msg = convos[idx]["messages"][-1]
            if last_msg["role"] != "user":
                # Already responded or empty
                messages_display = [
                    {"role": m["role"], "content": m["content"]}
                    for m in convos[idx]["messages"]
                ]
                yield messages_display, convos
                return

            user_text = last_msg["content"]
            response = pick_response(user_text)

            # Build the display list from existing messages
            base_messages = [
                {"role": m["role"], "content": m["content"]}
                for m in convos[idx]["messages"]
            ]

            # Stream character by character
            partial = ""
            for char in response:
                partial += char
                display = base_messages + [{"role": "assistant", "content": partial}]
                yield display, convos
                time.sleep(0.02)

            # Store final assistant message in state
            convos[idx]["messages"].append(
                {"role": "assistant", "content": response}
            )

            final_display = [
                {"role": m["role"], "content": m["content"]}
                for m in convos[idx]["messages"]
            ]
            yield final_display, convos

        def new_conversation(convos, idx):
            """Create a new empty conversation and switch to it."""
            new_id = max(c["id"] for c in convos) + 1
            convos.append({"id": new_id, "title": "New chat", "messages": []})
            new_idx = len(convos) - 1

            choices = _convo_choices(convos)
            current = choices[new_idx]

            return (
                [],
                convos,
                new_idx,
                gr.update(choices=choices, value=current),
            )

        def switch_conversation(selected_title, convos, idx):
            """Switch to the conversation matching the selected radio title."""
            choices = _convo_choices(convos)
            if selected_title in choices:
                new_idx = choices.index(selected_title)
            else:
                new_idx = idx

            messages_display = [
                {"role": m["role"], "content": m["content"]}
                for m in convos[new_idx]["messages"]
            ]

            return messages_display, convos, new_idx

        # -- Wire events ----------------------------------------------------

        # Submit via button or Enter key
        submit_event_args = dict(
            fn=user_submit,
            inputs=[msg_input, conversations, active_idx],
            outputs=[chatbot, msg_input, conversations, active_idx, convo_radio],
        )
        stream_event_args = dict(
            fn=bot_stream,
            inputs=[conversations, active_idx],
            outputs=[chatbot, conversations],
        )

        send_btn.click(**submit_event_args).then(**stream_event_args)
        msg_input.submit(**submit_event_args).then(**stream_event_args)

        # New conversation
        new_convo_btn.click(
            fn=new_conversation,
            inputs=[conversations, active_idx],
            outputs=[chatbot, conversations, active_idx, convo_radio],
        )

        # Switch conversation via sidebar
        convo_radio.change(
            fn=switch_conversation,
            inputs=[convo_radio, conversations, active_idx],
            outputs=[chatbot, conversations, active_idx],
        )

        # Quick action buttons — prefill the text input
        def fill_prompt(prefill_text):
            return prefill_text + " "

        for i, btn in enumerate(qa_buttons):
            btn.click(
                fn=lambda _, text=QUICK_ACTIONS[i][1]: text + " ",
                inputs=[],
                outputs=[msg_input],
            )

    return app


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    app = create_app()
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        css=CUSTOM_CSS,
        theme=gr.themes.Base(),
    )
