import { useState, useRef, useEffect, useCallback } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { nanoid } from 'nanoid';

// ---------------------------------------------------------------------------
// Canned responses
// ---------------------------------------------------------------------------
const CANNED_RESPONSES = [
  "That's a great question! Let me think about this...\n\nThe key insight here is that **complex problems** often have surprisingly simple solutions when you break them down into smaller pieces.\n\nHere are a few approaches:\n1. Start with the fundamentals\n2. Build incrementally\n3. Test at each step\n\nWould you like me to elaborate on any of these?",
  "I'd be happy to help with that!\n\nHere's a quick overview:\n\n```python\ndef solve(problem):\n    # Break it down\n    steps = analyze(problem)\n    for step in steps:\n        execute(step)\n    return result\n```\n\nThe important thing is to approach it **systematically**. Let me know if you need more details.",
  "Interesting topic! There are several perspectives to consider:\n\n- **First**, the historical context matters quite a bit\n- **Second**, modern approaches have evolved significantly\n- **Third**, practical applications vary by domain\n\n> \"The best way to predict the future is to invent it.\" — Alan Kay\n\nWhat specific aspect would you like to explore further?",
  "Great question! Let me break this down:\n\n### Overview\nThis is a common challenge that many developers face. The solution involves understanding a few core concepts.\n\n### Key Points\n1. **Simplicity** is usually better than complexity\n2. **Readability** matters more than cleverness\n3. **Testing** catches issues early\n\n### Example\n```javascript\nconst solution = (input) => {\n  return input\n    .filter(item => item.isValid)\n    .map(item => transform(item))\n    .reduce((acc, val) => acc + val, 0);\n};\n```\n\nHope that helps! Feel free to ask follow-up questions.",
  "That's a fascinating area! Let me share some thoughts.\n\nThe fundamental challenge here is balancing **trade-offs**. Every engineering decision involves choosing between:\n\n| Option | Pros | Cons |\n|--------|------|------|\n| Approach A | Simple, fast | Limited flexibility |\n| Approach B | Flexible | More complex |\n| Approach C | Balanced | Moderate on both |\n\nIn my experience, *starting simple and iterating* tends to produce the best outcomes. You can always add complexity later, but removing it is much harder.\n\nWhat constraints are you working with?"
];

const MODELS = [
  { id: 'opus', name: 'Claude Opus 4' },
  { id: 'sonnet', name: 'Claude Sonnet 4' },
  { id: 'haiku', name: 'Claude Haiku' },
  { id: 'gpt4o', name: 'GPT-4o' },
  { id: 'gpt4o-mini', name: 'GPT-4o mini' },
];

const TOOLS = [
  { id: 'web_search', name: 'Web Search', icon: '🔍' },
  { id: 'code_interpreter', name: 'Code Interpreter', icon: '💻' },
  { id: 'image_gen', name: 'Image Generation', icon: '🎨' },
  { id: 'file_analysis', name: 'File Analysis', icon: '📄' },
];

const QUICK_ACTIONS = [
  { label: '✍️ Write code', prompt: 'Write a Python function that' },
  { label: '💡 Explain concept', prompt: 'Explain the concept of' },
  { label: '📝 Summarize', prompt: 'Summarize the following text:' },
  { label: '🐛 Debug', prompt: 'Help me debug this code:' },
  { label: '🔄 Refactor', prompt: 'Refactor this code to be cleaner:' },
  { label: '📊 Analyze', prompt: 'Analyze the following data:' },
];

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------
function hashMessage(text) {
  let sum = 0;
  for (let i = 0; i < text.length; i++) {
    sum += text.charCodeAt(i);
  }
  return sum % CANNED_RESPONSES.length;
}

function createConversation() {
  return {
    id: nanoid(),
    title: 'New conversation',
    messages: [],
  };
}

// ---------------------------------------------------------------------------
// Icons (inline SVG components)
// ---------------------------------------------------------------------------
function SendIcon() {
  return (
    <svg
      width="20"
      height="20"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <line x1="22" y1="2" x2="11" y2="13" />
      <polygon points="22 2 15 22 11 13 2 9 22 2" />
    </svg>
  );
}

function PlusIcon() {
  return (
    <svg
      width="18"
      height="18"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <line x1="12" y1="5" x2="12" y2="19" />
      <line x1="5" y1="12" x2="19" y2="12" />
    </svg>
  );
}

function MenuIcon() {
  return (
    <svg
      width="22"
      height="22"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <line x1="3" y1="6" x2="21" y2="6" />
      <line x1="3" y1="12" x2="21" y2="12" />
      <line x1="3" y1="18" x2="21" y2="18" />
    </svg>
  );
}

function GearIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="3" />
      <path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42" />
    </svg>
  );
}

function PaperclipIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M21.44 11.05l-9.19 9.19a6 6 0 01-8.49-8.49l9.19-9.19a4 4 0 015.66 5.66l-9.2 9.19a2 2 0 01-2.83-2.83l8.49-8.48" />
    </svg>
  );
}

function CloseSmallIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
      <line x1="18" y1="6" x2="6" y2="18" />
      <line x1="6" y1="6" x2="18" y2="18" />
    </svg>
  );
}

function OptionsPanel({ selectedModel, onModelChange, enabledTools, onToolToggle, onClose }) {
  return (
    <div className="options-panel">
      <div className="options-header">
        <span className="options-title">Options</span>
        <button className="options-close" onClick={onClose}>&times;</button>
      </div>
      <div className="options-section">
        <div className="options-section-title">Model</div>
        {MODELS.map((model) => (
          <label key={model.id} className={`model-option ${selectedModel === model.id ? 'model-option-active' : ''}`}>
            <input
              type="radio"
              name="model"
              value={model.id}
              checked={selectedModel === model.id}
              onChange={() => onModelChange(model.id)}
            />
            <span>{model.name}</span>
          </label>
        ))}
      </div>
      <div className="options-section">
        <div className="options-section-title">Tools</div>
        {TOOLS.map((tool) => (
          <label key={tool.id} className="tool-toggle">
            <span className="tool-info">
              <span className="tool-icon">{tool.icon}</span>
              <span>{tool.name}</span>
            </span>
            <div
              className={`toggle-switch ${enabledTools.includes(tool.id) ? 'toggle-on' : ''}`}
              onClick={(e) => { e.preventDefault(); onToolToggle(tool.id); }}
            >
              <div className="toggle-knob" />
            </div>
          </label>
        ))}
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// ThinkingIndicator
// ---------------------------------------------------------------------------
function ThinkingIndicator() {
  return (
    <div className="thinking-indicator">
      <div className="thinking-dot" />
      <div className="thinking-dot" />
      <div className="thinking-dot" />
    </div>
  );
}

// ---------------------------------------------------------------------------
// MessageBubble
// ---------------------------------------------------------------------------
function MessageBubble({ message }) {
  const isUser = message.role === 'user';

  return (
    <div className={`message-row ${isUser ? 'message-row-user' : 'message-row-assistant'}`}>
      {!isUser && (
        <div className="avatar avatar-assistant">C</div>
      )}
      <div className={`message-bubble ${isUser ? 'bubble-user' : 'bubble-assistant'}`}>
        {isUser ? (
          <div className="message-text">{message.content}</div>
        ) : (
          <div className="message-text markdown-body">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {message.content}
            </ReactMarkdown>
          </div>
        )}
      </div>
      {isUser && (
        <div className="avatar avatar-user">U</div>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// WelcomeScreen
// ---------------------------------------------------------------------------
function WelcomeScreen() {
  return (
    <div className="welcome-screen">
      <div className="welcome-logo">C</div>
      <h1 className="welcome-title">Claude</h1>
      <p className="welcome-tagline">
        Your AI assistant for thoughtful conversation. Ask me anything to get started.
      </p>
    </div>
  );
}

// ---------------------------------------------------------------------------
// App
// ---------------------------------------------------------------------------
export default function App() {
  const [conversations, setConversations] = useState(() => {
    const first = createConversation();
    return [first];
  });
  const [activeId, setActiveId] = useState(() => conversations[0]?.id);
  const [inputValue, setInputValue] = useState('');
  const [isThinking, setIsThinking] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [selectedModel, setSelectedModel] = useState('sonnet');
  const [enabledTools, setEnabledTools] = useState(['web_search', 'code_interpreter']);
  const [showOptions, setShowOptions] = useState(false);
  const [attachedFiles, setAttachedFiles] = useState([]);

  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);
  const optionsPanelRef = useRef(null);
  const fileInputRef = useRef(null);
  const streamIntervalRef = useRef(null);

  const activeConversation = conversations.find((c) => c.id === activeId);

  // ---- Auto-scroll ----
  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [activeConversation?.messages, isThinking, scrollToBottom]);

  // ---- Cleanup streaming on unmount ----
  useEffect(() => {
    return () => {
      if (streamIntervalRef.current) clearInterval(streamIntervalRef.current);
    };
  }, []);

  // ---- Auto-resize textarea ----
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height =
        Math.min(textareaRef.current.scrollHeight, 200) + 'px';
    }
  }, [inputValue]);

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (showOptions && optionsPanelRef.current && !optionsPanelRef.current.contains(e.target)) {
        setShowOptions(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [showOptions]);

  // ---- Update a conversation in state ----
  const updateConversation = useCallback((convId, updater) => {
    setConversations((prev) =>
      prev.map((c) => (c.id === convId ? updater(c) : c))
    );
  }, []);

  // ---- Send message ----
  const handleSend = useCallback(() => {
    const text = inputValue.trim();
    if (!text || isThinking || isStreaming) return;

    const filePrefix = attachedFiles.length > 0
      ? `📎 ${attachedFiles.map(f => f.name).join(', ')}\n\n`
      : '';
    const userMsg = { id: nanoid(), role: 'user', content: filePrefix + text };
    const convId = activeId;

    // Add user message & update title if this is the first message
    updateConversation(convId, (conv) => {
      const isFirst = conv.messages.length === 0;
      return {
        ...conv,
        title: isFirst ? text.slice(0, 40) + (text.length > 40 ? '...' : '') : conv.title,
        messages: [...conv.messages, userMsg],
      };
    });

    setInputValue('');
    setAttachedFiles([]);
    setIsThinking(true);

    // Pick a canned response
    const responseIndex = hashMessage(text);
    const fullResponse = CANNED_RESPONSES[responseIndex];

    // After "thinking" delay, begin streaming
    const thinkingTimeout = setTimeout(() => {
      setIsThinking(false);
      setIsStreaming(true);

      const assistantMsg = { id: nanoid(), role: 'assistant', content: '' };

      updateConversation(convId, (conv) => ({
        ...conv,
        messages: [...conv.messages, assistantMsg],
      }));

      let charIndex = 0;

      streamIntervalRef.current = setInterval(() => {
        charIndex++;
        const partial = fullResponse.slice(0, charIndex);

        setConversations((prev) =>
          prev.map((c) => {
            if (c.id !== convId) return c;
            const msgs = [...c.messages];
            const lastIdx = msgs.length - 1;
            if (lastIdx >= 0 && msgs[lastIdx].role === 'assistant') {
              msgs[lastIdx] = { ...msgs[lastIdx], content: partial };
            }
            return { ...c, messages: msgs };
          })
        );

        if (charIndex >= fullResponse.length) {
          clearInterval(streamIntervalRef.current);
          streamIntervalRef.current = null;
          setIsStreaming(false);
        }
      }, 30);
    }, 800);

    // Store timeout ref for potential cleanup
    return () => clearTimeout(thinkingTimeout);
  }, [inputValue, isThinking, isStreaming, activeId, updateConversation]);

  // ---- Keyboard handler for textarea ----
  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  // ---- New conversation ----
  const handleNewConversation = () => {
    // Stop any active streaming
    if (streamIntervalRef.current) {
      clearInterval(streamIntervalRef.current);
      streamIntervalRef.current = null;
    }
    setIsThinking(false);
    setIsStreaming(false);

    const newConv = createConversation();
    setConversations((prev) => [newConv, ...prev]);
    setActiveId(newConv.id);
    setInputValue('');
    setSidebarOpen(false);
  };

  // ---- Switch conversation ----
  const handleSwitchConversation = (id) => {
    if (isStreaming || isThinking) return; // prevent switching during streaming
    setActiveId(id);
    setInputValue('');
    setSidebarOpen(false);
  };

  const handleToolToggle = (toolId) => {
    setEnabledTools((prev) =>
      prev.includes(toolId) ? prev.filter((t) => t !== toolId) : [...prev, toolId]
    );
  };

  const handleQuickAction = (prompt) => {
    setInputValue(prompt + ' ');
    textareaRef.current?.focus();
  };

  const handleFileSelect = (e) => {
    const files = Array.from(e.target.files);
    const newFiles = files.map((f) => ({
      id: nanoid(),
      name: f.name,
      size: f.size,
      type: f.type,
    }));
    setAttachedFiles((prev) => [...prev, ...newFiles]);
    e.target.value = '';
  };

  const removeFile = (fileId) => {
    setAttachedFiles((prev) => prev.filter((f) => f.id !== fileId));
  };

  const formatFileSize = (bytes) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / 1048576).toFixed(1) + ' MB';
  };

  // ---- Toggle sidebar (mobile) ----
  const toggleSidebar = () => {
    setSidebarOpen((prev) => !prev);
  };

  const canSend = inputValue.trim().length > 0 && !isThinking && !isStreaming;

  return (
    <div className="app-container">
      {/* Overlay for mobile sidebar */}
      {sidebarOpen && (
        <div className="sidebar-overlay" onClick={() => setSidebarOpen(false)} />
      )}

      {/* Sidebar */}
      <aside className={`sidebar ${sidebarOpen ? 'sidebar-open' : ''}`}>
        <div className="sidebar-header">
          <button className="new-chat-btn" onClick={handleNewConversation}>
            <PlusIcon />
            <span>New conversation</span>
          </button>
        </div>
        <nav className="conversation-list">
          {conversations.map((conv) => (
            <button
              key={conv.id}
              className={`conversation-item ${conv.id === activeId ? 'conversation-active' : ''}`}
              onClick={() => handleSwitchConversation(conv.id)}
              title={conv.title}
            >
              <span className="conversation-title">{conv.title}</span>
            </button>
          ))}
        </nav>
      </aside>

      {/* Main chat area */}
      <main className="chat-main">
        {/* Top bar */}
        <header className="chat-header">
          <button className="menu-btn" onClick={toggleSidebar}>
            <MenuIcon />
          </button>
          <span className="header-title">Claude</span>
          <span className="model-badge">{MODELS.find(m => m.id === selectedModel)?.name}</span>
          <div className="header-spacer" />
        </header>

        {/* Messages */}
        <div className="messages-container">
          {activeConversation && activeConversation.messages.length === 0 && !isThinking ? (
            <WelcomeScreen />
          ) : (
            <div className="messages-list">
              {activeConversation?.messages.map((msg) => (
                <MessageBubble key={msg.id} message={msg} />
              ))}
              {isThinking && (
                <div className="message-row message-row-assistant">
                  <div className="avatar avatar-assistant">C</div>
                  <div className="message-bubble bubble-assistant">
                    <ThinkingIndicator />
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Input area */}
        <div className="input-area">
          {attachedFiles.length > 0 && (
            <div className="attached-files">
              {attachedFiles.map((file) => (
                <div key={file.id} className="file-pill">
                  <span className="file-pill-icon">📄</span>
                  <span className="file-pill-name">{file.name}</span>
                  <span className="file-pill-size">{formatFileSize(file.size)}</span>
                  <button className="file-pill-remove" onClick={() => removeFile(file.id)}>
                    <CloseSmallIcon />
                  </button>
                </div>
              ))}
            </div>
          )}
          <div className="input-wrapper">
            <input
              ref={fileInputRef}
              type="file"
              multiple
              onChange={handleFileSelect}
              style={{ display: 'none' }}
              accept=".txt,.pdf,.js,.jsx,.ts,.tsx,.py,.md,.csv,.json,.html,.css,.png,.jpg,.jpeg,.gif,.svg"
            />
            <button
              className="attach-btn"
              onClick={() => fileInputRef.current?.click()}
              aria-label="Attach file"
              disabled={isThinking || isStreaming}
            >
              <PaperclipIcon />
            </button>
            <button
              className="options-btn"
              onClick={() => setShowOptions((prev) => !prev)}
              aria-label="Options"
            >
              <GearIcon />
            </button>
            {showOptions && (
              <div ref={optionsPanelRef} className="options-panel-anchor">
                <OptionsPanel
                  selectedModel={selectedModel}
                  onModelChange={setSelectedModel}
                  enabledTools={enabledTools}
                  onToolToggle={handleToolToggle}
                  onClose={() => setShowOptions(false)}
                />
              </div>
            )}
            <textarea
              ref={textareaRef}
              className="message-input"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Message Claude..."
              rows={1}
              disabled={isThinking || isStreaming}
            />
            <button
              className={`send-btn ${canSend ? 'send-btn-active' : ''}`}
              onClick={handleSend}
              disabled={!canSend}
              aria-label="Send message"
            >
              <SendIcon />
            </button>
          </div>
          <div className="quick-actions">
            {QUICK_ACTIONS.map((action) => (
              <button
                key={action.label}
                className="quick-action-btn"
                onClick={() => handleQuickAction(action.prompt)}
                disabled={isThinking || isStreaming}
              >
                {action.label}
              </button>
            ))}
          </div>
          <p className="input-disclaimer">
            This is a demo clone with canned responses. No real AI is used.
          </p>
        </div>
      </main>
    </div>
  );
}
