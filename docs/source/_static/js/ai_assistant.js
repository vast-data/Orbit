/**
 * Astra - VAST Orbit AI Assistant
 * Interactive chat interface for documentation queries
 */

class VAST OrbitAI {
  constructor(config = {}) {
    this.apiUrl = config.apiUrl || 'http://localhost:8010/api/ask';  // Changed to 5001
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
        Ask Astra
      </button>

      <div id="ai-chat-sidebar" class="ai-chat-sidebar">
        <span class="closebtn" onclick="vastOrbitAI.closeChat()">&times;</span>
        
        <div class="ai-chat-header">
          <h2>👩‍🚀 Astra</h2>
          <p>Your VAST Orbit documentation assistant</p>
        </div>

        <div id="ai-chat-container" class="ai-chat-container">
          <div class="welcome-message">
            <div style="font-size: 60px; margin-bottom: 10px;">👩‍🚀</div>
            <h3>Welcome to Astra!</h3>
            <p style="margin: 10px 0;">I'm your AI guide to the VAST Orbit universe.</p>
            <p style="margin: 5px 0; font-size: 0.9em; opacity: 0.8;">Ask me anything about VAST Orbit features, APIs, or examples!</p>
            
            <div style="margin-top: 20px; padding: 15px; background: rgba(41, 184, 255, 0.1); border-radius: 10px; font-size: 0.85em;">
              <strong style="color: #29b8ff;">💡 Try asking:</strong><br>
              • "How do I get started?"<br>
              • "Show me vDataFrame examples"<br>
              • "How do I connect to VAST DataBase?"
            </div>
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
              🚀 Getting Started
            </button>
            <button class="quick-prompt-btn" data-prompt="What are the main features of VAST Orbit?">
              ⭐ Features
            </button>
            <button class="quick-prompt-btn" data-prompt="Show me vDataFrame examples">
              📝 Examples
            </button>
          </div>
          <div class="ai-input-wrapper">
            <textarea 
              id="ai-question-input" 
              placeholder="Ask Astra a question..."
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

    // Hide quick prompts after first message
    const quickPrompts = document.getElementById('quick-prompts');
    if (quickPrompts && this.conversationHistory.length === 0) {
      quickPrompts.style.display = 'none';
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
      this.showError('Sorry, I encountered an error. Please make sure the API server is running on port 5001.');
    } finally {
      // Re-enable send button
      this.sendButton.disabled = false;
      this.inputField.focus();
    }
  }

  addMessage(text, type, sources = null) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `${type}-message`;
    
    // Add icon for AI messages
    if (type === 'ai') {
      const iconSpan = document.createElement('span');
      iconSpan.textContent = '👩‍🚀 ';
      iconSpan.style.marginRight = '5px';
      messageDiv.appendChild(iconSpan);
    }
    
    // Format the message text (simple markdown support)
    let formattedText = this.formatMessage(text);
    
    const contentSpan = document.createElement('span');
    contentSpan.innerHTML = formattedText;
    messageDiv.appendChild(contentSpan);
    
    // Add sources if available
    if (sources && sources.length > 0) {
      const sourcesDiv = document.createElement('div');
      sourcesDiv.className = 'message-sources';
      sourcesDiv.style.marginTop = '10px';
      sourcesDiv.style.fontSize = '0.85em';
      sourcesDiv.style.opacity = '0.8';
      sourcesDiv.innerHTML = '<strong>📚 Sources:</strong> ' + 
        sources.map(s => `<a href="${s.url}" target="_blank" style="color: #29b8ff; text-decoration: none;">${s.title}</a>`).join(', ');
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
      // Only save last 10 exchanges to keep it light
      const recentHistory = this.conversationHistory.slice(-10);
      localStorage.setItem('astra_conversation_history', JSON.stringify(recentHistory));
    } catch (e) {
      console.warn('Could not save conversation history:', e);
    }
  }

  loadConversationHistory() {
    try {
      const saved = localStorage.getItem('astra_conversation_history');
      if (saved) {
        this.conversationHistory = JSON.parse(saved);
        
        // Restore messages (limit to last 5 exchanges for performance)
        const recentHistory = this.conversationHistory.slice(-5);
        if (recentHistory.length > 0) {
          const welcomeMsg = this.messagesContainer.querySelector('.welcome-message');
          if (welcomeMsg) {
            welcomeMsg.style.display = 'none';
          }
          const quickPrompts = document.getElementById('quick-prompts');
          if (quickPrompts) {
            quickPrompts.style.display = 'none';
          }
        }
        
        recentHistory.forEach(exchange => {
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
    localStorage.removeItem('astra_conversation_history');
    
    // Clear messages
    const messages = this.messagesContainer.querySelectorAll('.user-message, .ai-message, .error-message');
    messages.forEach(msg => msg.remove());
    
    // Show welcome message and quick prompts again
    const welcomeMsg = this.messagesContainer.querySelector('.welcome-message');
    if (welcomeMsg) {
      welcomeMsg.style.display = 'block';
    }
    const quickPrompts = document.getElementById('quick-prompts');
    if (quickPrompts) {
      quickPrompts.style.display = 'flex';
    }
  }
}

// Initialize the AI assistant
let vastOrbitAI;
document.addEventListener('DOMContentLoaded', () => {
  vastOrbitAI = new VAST OrbitAI({
    apiUrl: window.VASTORBIT_AI_API_URL || 'http://localhost:8010/api/ask'
  });
});