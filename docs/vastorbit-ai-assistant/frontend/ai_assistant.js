/**
 * VAST Orbit AI Assistant
 * Interactive chat interface for documentation queries
 */

class VAST OrbitAI {
  constructor(config = {}) {
    this.apiUrl = config.apiUrl || 'http://localhost:5000/api/ask';
    this.chatContainer = null;
    this.messagesContainer = null;
    this.inputField = null;
    this.sendButton = null;
    this.conversationHistory = [];
    
    this.init();
  }

  init() {
    // Wait for DOM to be ready
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', () => this.setup());
    } else {
      this.setup();
    }
  }

  setup() {
    this.injectHTML();
    this.setupEventListeners();
    this.loadConversationHistory();
  }

  injectHTML() {
    // Create the AI chat interface
    const chatHTML = `
      <button class="ask-ai-btn" onclick="vastOrbitAI.openChat()">
        Ask AI
      </button>

      <div id="ai-chat-sidebar" class="ai-chat-sidebar">
        <span class="closebtn" onclick="vastOrbitAI.closeChat()">&times;</span>
        
        <div class="ai-chat-header">
          <h2>🤖 VAST Orbit Assistant</h2>
          <p>Ask me anything about VAST Orbit documentation</p>
        </div>

        <div id="ai-chat-container" class="ai-chat-container">
          <div class="welcome-message">
            <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm-1-13h2v6h-2zm0 8h2v2h-2z"/>
            </svg>
            <h3>Welcome!</h3>
            <p>I'm here to help you with VAST Orbit documentation.</p>
            <p>Ask me about features, APIs, examples, or anything else!</p>
          </div>
          
          <div class="typing-indicator">
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
          </div>
        </div>

        <div class="ai-input-container">
          <div class="quick-prompts" id="quick-prompts">
            <button class="quick-prompt-btn" data-prompt="How do I get started with VAST Orbit?">
              Getting Started
            </button>
            <button class="quick-prompt-btn" data-prompt="What are the main features?">
              Main Features
            </button>
            <button class="quick-prompt-btn" data-prompt="Show me examples">
              Examples
            </button>
          </div>
          <div class="ai-input-wrapper">
            <textarea 
              id="ai-question-input" 
              placeholder="Ask a question about VAST Orbit..."
              rows="1"
            ></textarea>
            <button id="ai-send-btn">Send</button>
          </div>
        </div>
      </div>
    `;

    // Append to body
    document.body.insertAdjacentHTML('beforeend', chatHTML);
    
    // Get references
    this.chatContainer = document.getElementById('ai-chat-sidebar');
    this.messagesContainer = document.getElementById('ai-chat-container');
    this.inputField = document.getElementById('ai-question-input');
    this.sendButton = document.getElementById('ai-send-btn');
  }

  setupEventListeners() {
    // Send button click
    this.sendButton.addEventListener('click', () => this.sendMessage());
    
    // Enter key to send (Shift+Enter for new line)
    this.inputField.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        this.sendMessage();
      }
    });

    // Auto-resize textarea
    this.inputField.addEventListener('input', () => {
      this.inputField.style.height = 'auto';
      this.inputField.style.height = this.inputField.scrollHeight + 'px';
    });

    // Quick prompts
    document.querySelectorAll('.quick-prompt-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const prompt = e.target.getAttribute('data-prompt');
        this.inputField.value = prompt;
        this.sendMessage();
      });
    });

    // Close on escape key
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && this.chatContainer.classList.contains('open')) {
        this.closeChat();
      }
    });
  }

  openChat() {
    this.chatContainer.classList.add('open');
    this.inputField.focus();
  }

  closeChat() {
    this.chatContainer.classList.remove('open');
  }

  async sendMessage() {
    const question = this.inputField.value.trim();
    
    if (!question) return;

    // Hide welcome message if present
    const welcomeMsg = this.messagesContainer.querySelector('.welcome-message');
    if (welcomeMsg) {
      welcomeMsg.style.display = 'none';
    }

    // Add user message
    this.addMessage(question, 'user');
    
    // Clear input
    this.inputField.value = '';
    this.inputField.style.height = 'auto';
    
    // Show typing indicator
    this.showTypingIndicator();
    
    // Disable send button
    this.sendButton.disabled = true;

    try {
      // Call API
      const response = await fetch(this.apiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question: question,
          conversation_history: this.conversationHistory
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      // Hide typing indicator
      this.hideTypingIndicator();
      
      // Add AI response
      this.addMessage(data.answer, 'ai', data.sources);
      
      // Update conversation history
      this.conversationHistory.push({
        question: question,
        answer: data.answer
      });
      
      // Save to localStorage
      this.saveConversationHistory();

    } catch (error) {
      console.error('Error:', error);
      this.hideTypingIndicator();
      this.showError('Sorry, I encountered an error. Please try again or check if the API server is running.');
    } finally {
      // Re-enable send button
      this.sendButton.disabled = false;
      this.inputField.focus();
    }
  }

  addMessage(text, type, sources = null) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `${type}-message`;
    
    // Format the message text (simple markdown support)
    let formattedText = this.formatMessage(text);
    messageDiv.innerHTML = formattedText;
    
    // Add sources if available
    if (sources && sources.length > 0) {
      const sourcesDiv = document.createElement('div');
      sourcesDiv.className = 'message-sources';
      sourcesDiv.style.marginTop = '10px';
      sourcesDiv.style.fontSize = '0.85em';
      sourcesDiv.style.opacity = '0.8';
      sourcesDiv.innerHTML = '<strong>Sources:</strong> ' + 
        sources.map(s => `<a href="${s.url}" target="_blank">${s.title}</a>`).join(', ');
      messageDiv.appendChild(sourcesDiv);
    }
    
    // Insert before typing indicator
    const typingIndicator = this.messagesContainer.querySelector('.typing-indicator');
    this.messagesContainer.insertBefore(messageDiv, typingIndicator);
    
    // Scroll to bottom
    this.scrollToBottom();
  }

  formatMessage(text) {
    // Basic markdown-like formatting
    text = text.replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>');
    text = text.replace(/`([^`]+)`/g, '<code>$1</code>');
    text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    text = text.replace(/\*(.*?)\*/g, '<em>$1</em>');
    text = text.replace(/\n/g, '<br>');
    
    return text;
  }

  showTypingIndicator() {
    const indicator = this.messagesContainer.querySelector('.typing-indicator');
    indicator.classList.add('active');
    this.scrollToBottom();
  }

  hideTypingIndicator() {
    const indicator = this.messagesContainer.querySelector('.typing-indicator');
    indicator.classList.remove('active');
  }

  showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message;
    
    const typingIndicator = this.messagesContainer.querySelector('.typing-indicator');
    this.messagesContainer.insertBefore(errorDiv, typingIndicator);
    
    this.scrollToBottom();
    
    // Remove error after 5 seconds
    setTimeout(() => {
      errorDiv.remove();
    }, 5000);
  }

  scrollToBottom() {
    this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
  }

  saveConversationHistory() {
    try {
      localStorage.setItem('vastorbit_ai_history', JSON.stringify(this.conversationHistory));
    } catch (e) {
      console.warn('Could not save conversation history:', e);
    }
  }

  loadConversationHistory() {
    try {
      const saved = localStorage.getItem('vastorbit_ai_history');
      if (saved) {
        this.conversationHistory = JSON.parse(saved);
        
        // Restore messages (limit to last 10 exchanges)
        const recentHistory = this.conversationHistory.slice(-10);
        recentHistory.forEach(exchange => {
          const welcomeMsg = this.messagesContainer.querySelector('.welcome-message');
          if (welcomeMsg) {
            welcomeMsg.style.display = 'none';
          }
          this.addMessage(exchange.question, 'user');
          this.addMessage(exchange.answer, 'ai');
        });
      }
    } catch (e) {
      console.warn('Could not load conversation history:', e);
    }
  }

  clearHistory() {
    this.conversationHistory = [];
    localStorage.removeItem('vastorbit_ai_history');
    
    // Clear messages
    const messages = this.messagesContainer.querySelectorAll('.user-message, .ai-message, .error-message');
    messages.forEach(msg => msg.remove());
    
    // Show welcome message again
    const welcomeMsg = this.messagesContainer.querySelector('.welcome-message');
    if (welcomeMsg) {
      welcomeMsg.style.display = 'block';
    }
  }
}

// Initialize the AI assistant
let vastOrbitAI;
document.addEventListener('DOMContentLoaded', () => {
  vastOrbitAI = new VAST OrbitAI({
    apiUrl: window.VASTORBIT_AI_API_URL || 'http://localhost:5000/api/ask'
  });
});
