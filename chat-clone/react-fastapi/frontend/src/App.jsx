import { useState, useEffect, useRef } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

const API_BASE = '/api'

// ---------------------------------------------------------------------------
// Icons
// ---------------------------------------------------------------------------
const SendIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <line x1="22" y1="2" x2="11" y2="13" />
    <polygon points="22 2 15 22 11 13 2 9 22 2" />
  </svg>
)

const PlusIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <line x1="12" y1="5" x2="12" y2="19" />
    <line x1="5" y1="12" x2="19" y2="12" />
  </svg>
)

const MenuIcon = () => (
  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <line x1="3" y1="6" x2="21" y2="6" />
    <line x1="3" y1="12" x2="21" y2="12" />
    <line x1="3" y1="18" x2="21" y2="18" />
  </svg>
)

const GearIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <circle cx="12" cy="12" r="3" />
    <path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42" />
  </svg>
)

const PaperclipIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M21.44 11.05l-9.19 9.19a6 6 0 01-8.49-8.49l9.19-9.19a4 4 0 015.66 5.66l-9.2 9.19a2 2 0 01-2.83-2.83l8.49-8.48" />
  </svg>
)

// ---------------------------------------------------------------------------
// Components
// ---------------------------------------------------------------------------
function ThinkingTrace({ trace }) {
  const [isOpen, setIsOpen] = useState(false)
  if (!trace) return null

  return (
    <div className={`thinking-trace ${isOpen ? 'thinking-trace-open' : ''}`}>
      <button className="thinking-trace-toggle" onClick={() => setIsOpen(!isOpen)}>
        <span className="thinking-trace-icon">💭</span>
        <span className="thinking-trace-label">Thinking...</span>
        <span className={`thinking-trace-chevron ${isOpen ? 'chevron-open' : ''}`}>▶</span>
      </button>
      {isOpen && (
        <div className="thinking-trace-content">
          <div className="thinking-trace-section">
            <div className="thinking-trace-section-title">Reasoning</div>
            <p className="thinking-trace-reasoning">{trace.reasoning}</p>
          </div>
          {trace.tools?.length > 0 && (
            <div className="thinking-trace-section">
              <div className="thinking-trace-section-title">Tool Use</div>
              {trace.tools.map((tool, i) => (
                <div key={i} className="thinking-trace-tool">
                  <span className="tool-call-icon">⚡</span>
                  <span className="tool-call-name">{tool.name}</span>
                  <span className="tool-call-query">("{tool.query}")</span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

function ThinkingIndicator() {
  return (
    <div className="thinking-indicator">
      <div className="thinking-dot" />
      <div className="thinking-dot" />
      <div className="thinking-dot" />
    </div>
  )
}

function MessageBubble({ message, isStreaming }) {
  const isUser = message.role === 'user'

  return (
    <div className={`message-row ${isUser ? 'message-row-user' : 'message-row-assistant'}`}>
      {!isUser && <div className="avatar avatar-assistant">C</div>}
      <div className={`message-bubble ${isUser ? 'bubble-user' : 'bubble-assistant'}`}>
        {!isUser && message.thinking && <ThinkingTrace trace={message.thinking} />}
        {isUser ? (
          <div className="message-text">{message.content}</div>
        ) : (
          <div className="message-text markdown-body">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{message.content}</ReactMarkdown>
          </div>
        )}
      </div>
      {isUser && <div className="avatar avatar-user">U</div>}
    </div>
  )
}

function WelcomeScreen() {
  return (
    <div className="welcome-screen">
      <div className="welcome-logo">C</div>
      <h1 className="welcome-title">Claude</h1>
      <p className="welcome-tagline">Your AI assistant for thoughtful conversation. Ask me anything to get started.</p>
    </div>
  )
}

function OptionsPanel({ models, tools, selectedModel, enabledTools, onModelChange, onToolToggle }) {
  return (
    <div className="options-panel">
      <div className="options-section">
        <div className="options-section-title">Model</div>
        {models.map((model) => (
          <label key={model} className={`model-option ${model === selectedModel ? 'model-option-active' : ''}`}>
            <input
              type="radio"
              name="model"
              value={model}
              checked={model === selectedModel}
              onChange={() => onModelChange(model)}
            />
            <span>{model}</span>
          </label>
        ))}
      </div>
      <div className="options-section">
        <div className="options-section-title">Tools</div>
        {tools.map((tool) => (
          <label key={tool.id} className="tool-toggle">
            <span className="tool-info">
              <span className="tool-icon">{tool.icon}</span>
              <span>{tool.name}</span>
            </span>
            <input
              type="checkbox"
              checked={enabledTools.includes(tool.id)}
              onChange={() => onToolToggle(tool.id)}
            />
          </label>
        ))}
      </div>
    </div>
  )
}

// ---------------------------------------------------------------------------
// Main App
// ---------------------------------------------------------------------------
export default function App() {
  // State from server
  const [conversations, setConversations] = useState([])
  const [activeId, setActiveId] = useState(null)
  const [models, setModels] = useState([])
  const [tools, setTools] = useState([])
  const [quickActions, setQuickActions] = useState([])
  const [selectedModel, setSelectedModel] = useState('')
  const [enabledTools, setEnabledTools] = useState([])

  // Local UI state
  const [inputValue, setInputValue] = useState('')
  const [isThinking, setIsThinking] = useState(false)
  const [isStreaming, setIsStreaming] = useState(false)
  const [streamingMessage, setStreamingMessage] = useState(null)
  const [currentThinking, setCurrentThinking] = useState(null)
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [showOptions, setShowOptions] = useState(false)
  const [attachedFiles, setAttachedFiles] = useState([])
  const [loading, setLoading] = useState(true)

  const messagesEndRef = useRef(null)
  const textareaRef = useRef(null)
  const fileInputRef = useRef(null)

  // Initialize from API
  useEffect(() => {
    fetch(`${API_BASE}/init`, { credentials: 'include' })
      .then((r) => r.json())
      .then((data) => {
        setConversations(data.conversations)
        setActiveId(data.active_id)
        setModels(data.models)
        setTools(data.tools)
        setQuickActions(data.quick_actions)
        setSelectedModel(data.selected_model)
        setEnabledTools(data.enabled_tools)
        setLoading(false)
      })
  }, [])

  // Auto-scroll
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [conversations, streamingMessage])

  const activeConversation = conversations.find((c) => c.id === activeId)

  // Create new conversation
  const handleNewConversation = async () => {
    const res = await fetch(`${API_BASE}/conversations`, {
      method: 'POST',
      credentials: 'include',
    })
    const data = await res.json()
    setConversations((prev) => [data.conversation, ...prev])
    setActiveId(data.active_id)
    setSidebarOpen(false)
  }

  // Switch conversation
  const handleSwitchConversation = async (convId) => {
    const res = await fetch(`${API_BASE}/conversations/${convId}/activate`, {
      method: 'POST',
      credentials: 'include',
    })
    const data = await res.json()
    setActiveId(data.active_id)
    setSidebarOpen(false)
  }

  // Send message with SSE streaming
  const handleSend = async () => {
    const text = inputValue.trim()
    if (!text || isStreaming) return

    setInputValue('')
    setIsThinking(true)
    setIsStreaming(true)
    setStreamingMessage(null)
    setCurrentThinking(null)

    const eventSource = new EventSource(
      `${API_BASE}/conversations/${activeId}/messages?` +
        new URLSearchParams({
          _body: JSON.stringify({ message: text, files: attachedFiles.map((f) => f.name) }),
        })
    )

    // Use fetch with streaming instead for POST
    const response = await fetch(`${API_BASE}/conversations/${activeId}/messages`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: text, files: attachedFiles.map((f) => f.name) }),
      credentials: 'include',
    })

    setAttachedFiles([])

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() // Keep incomplete line in buffer

      for (const line of lines) {
        if (line.startsWith('event: ')) {
          const eventType = line.slice(7)
          continue
        }
        if (line.startsWith('data: ')) {
          const data = JSON.parse(line.slice(6))
          const prevLine = lines[lines.indexOf(line) - 1]
          const eventType = prevLine?.startsWith('event: ') ? prevLine.slice(7) : null

          if (eventType === 'user_message') {
            setConversations((prev) =>
              prev.map((c) =>
                c.id === activeId ? { ...c, messages: [...c.messages, data] } : c
              )
            )
          } else if (eventType === 'thinking_start') {
            setIsThinking(false)
            setCurrentThinking(data)
          } else if (eventType === 'token') {
            setStreamingMessage({ id: data.id, content: data.content, thinking: currentThinking })
          } else if (eventType === 'message_complete') {
            setConversations((prev) =>
              prev.map((c) =>
                c.id === activeId ? { ...c, messages: [...c.messages, data] } : c
              )
            )
            setStreamingMessage(null)
            setIsStreaming(false)
          } else if (eventType === 'title_update') {
            setConversations((prev) =>
              prev.map((c) => (c.id === activeId ? { ...c, title: data.title } : c))
            )
          }
        }
      }
    }
  }

  // Update options
  const handleModelChange = async (model) => {
    setSelectedModel(model)
    await fetch(`${API_BASE}/options`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ model, tools: enabledTools }),
      credentials: 'include',
    })
  }

  const handleToolToggle = async (toolId) => {
    const newTools = enabledTools.includes(toolId)
      ? enabledTools.filter((t) => t !== toolId)
      : [...enabledTools, toolId]
    setEnabledTools(newTools)
    await fetch(`${API_BASE}/options`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ model: selectedModel, tools: newTools }),
      credentials: 'include',
    })
  }

  // File handling
  const handleFileSelect = (e) => {
    const files = Array.from(e.target.files).map((f) => ({
      name: f.name,
      size: f.size < 1024 ? `${f.size} B` : f.size < 1048576 ? `${(f.size / 1024).toFixed(1)} KB` : `${(f.size / 1048576).toFixed(1)} MB`,
    }))
    setAttachedFiles((prev) => [...prev, ...files])
    e.target.value = ''
  }

  // Quick action
  const handleQuickAction = (text) => {
    setInputValue(text + ' ')
    textareaRef.current?.focus()
  }

  // Keyboard
  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  if (loading) {
    return (
      <div className="app-container">
        <div className="loading">Loading...</div>
      </div>
    )
  }

  return (
    <div className="app-container">
      {/* Sidebar overlay */}
      {sidebarOpen && <div className="sidebar-overlay" onClick={() => setSidebarOpen(false)} />}

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
            >
              <span className="conversation-title">{conv.title}</span>
            </button>
          ))}
        </nav>
      </aside>

      {/* Main */}
      <main className="chat-main">
        <header className="chat-header">
          <button className="menu-btn" onClick={() => setSidebarOpen(true)}>
            <MenuIcon />
          </button>
          <span className="header-title">Claude</span>
          <span className="model-badge">{selectedModel}</span>
        </header>

        <div className="messages-container">
          {!activeConversation?.messages?.length && !isStreaming ? (
            <WelcomeScreen />
          ) : (
            <div className="messages-list">
              {activeConversation?.messages?.map((msg) => (
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
              {streamingMessage && (
                <MessageBubble message={{ ...streamingMessage, role: 'assistant' }} isStreaming />
              )}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Input area */}
        <div className="input-area">
          {attachedFiles.length > 0 && (
            <div className="attached-files">
              {attachedFiles.map((file, i) => (
                <div key={i} className="file-pill">
                  <span className="file-pill-icon">📄</span>
                  <span className="file-pill-name">{file.name}</span>
                  <span className="file-pill-size">{file.size}</span>
                  <button className="file-pill-remove" onClick={() => setAttachedFiles((f) => f.filter((_, j) => j !== i))}>
                    ×
                  </button>
                </div>
              ))}
            </div>
          )}

          <div className="input-wrapper">
            <input type="file" ref={fileInputRef} onChange={handleFileSelect} multiple hidden />
            <button className="attach-btn" onClick={() => fileInputRef.current?.click()}>
              <PaperclipIcon />
            </button>
            <button className="options-btn" onClick={() => setShowOptions(!showOptions)}>
              <GearIcon />
            </button>
            <textarea
              ref={textareaRef}
              className="message-input"
              placeholder="Message Claude..."
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleKeyDown}
              rows={1}
            />
            <button className="send-btn" onClick={handleSend} disabled={!inputValue.trim() || isStreaming}>
              <SendIcon />
            </button>
          </div>

          {showOptions && (
            <OptionsPanel
              models={models}
              tools={tools}
              selectedModel={selectedModel}
              enabledTools={enabledTools}
              onModelChange={handleModelChange}
              onToolToggle={handleToolToggle}
            />
          )}

          <div className="quick-actions">
            {quickActions.map((action, i) => (
              <button key={i} className="quick-action-btn" onClick={() => handleQuickAction(action.text)}>
                {action.label}
              </button>
            ))}
          </div>

          <p className="input-disclaimer">Demo clone with canned responses. (React + FastAPI)</p>
        </div>
      </main>
    </div>
  )
}
