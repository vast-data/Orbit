# 🤖 VAST Orbit AI Assistant

An intelligent documentation assistant powered by Claude that integrates seamlessly with your VAST Orbit Sphinx documentation.

![VAST Orbit AI Assistant](https://img.shields.io/badge/Powered%20by-Claude-blue)
![Python](https://img.shields.io/badge/Python-3.8%2B-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

## ✨ Features

- **💬 Interactive Chat Interface**: Floating button with slide-in chat sidebar
- **🔍 Smart Documentation Search**: RAG-powered responses using your actual documentation
- **🎨 Seamless Design Integration**: Matches your existing VAST Orbit theme and branding
- **📱 Responsive**: Works on desktop and mobile
- **🌙 Dark Mode Support**: Automatically adapts to your documentation's theme
- **💾 Conversation History**: Maintains context across questions (stored in browser)
- **⚡ Quick Prompts**: Pre-configured questions for common queries
- **🔗 Source Attribution**: Links to relevant documentation pages

## 📸 Preview

The AI assistant appears as a floating "Ask AI" button on the right side of your documentation. When clicked, it opens a chat interface where users can ask questions about VAST Orbit.

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│   Sphinx Documentation (Frontend)       │
│                                          │
│  ┌────────────────────────────────┐    │
│  │  AI Chat Interface             │    │
│  │  - CSS: ai_assistant.css       │    │
│  │  - JS: ai_assistant.js         │    │
│  └────────────────────────────────┘    │
└─────────────┬───────────────────────────┘
              │ HTTP/JSON
              │
┌─────────────▼───────────────────────────┐
│   Flask API Server (Backend)            │
│                                          │
│  ┌────────────────────────────────┐    │
│  │  RAG System                    │    │
│  │  - Document loading            │    │
│  │  - Keyword search              │    │
│  │  - Claude API integration      │    │
│  └────────────────────────────────┘    │
└─────────────┬───────────────────────────┘
              │ Anthropic API
              │
┌─────────────▼───────────────────────────┐
│   Claude (Sonnet 4)                     │
│   - Understands documentation           │
│   - Generates helpful responses         │
│   - Provides code examples              │
└─────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Anthropic API key ([Get one here](https://console.anthropic.com/))
- Built Sphinx documentation for VAST Orbit

### 1. Get Your Files

You should have received:
- `frontend/ai_assistant.css`
- `frontend/ai_assistant.js`
- `backend/app.py`
- `backend/requirements.txt`
- `INTEGRATION_GUIDE.md`
- `quickstart.sh`

### 2. Run Quick Start Script

```bash
chmod +x quickstart.sh
./quickstart.sh
```

The script will:
1. Check Python version
2. Install dependencies
3. Ask for your Anthropic API key
4. Ask for your documentation directory
5. Start the API server

### 3. Manual Setup (Alternative)

If you prefer manual setup:

```bash
# Install backend dependencies
cd backend
pip install -r requirements.txt

# Set environment variables
export ANTHROPIC_API_KEY="your_api_key_here"
export VASTORBIT_DOCS_DIR="/path/to/your/docs/build/html"

# Run the server
python app.py
```

### 4. Integrate with Your Documentation

See [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md) for detailed steps to add the frontend to your Sphinx docs.

Quick version:
```bash
# Copy files
cp frontend/ai_assistant.css YOUR_DOCS/source/_static/css/
cp frontend/ai_assistant.js YOUR_DOCS/source/_static/js/

# Update conf.py (add to existing lists)
html_css_files = [..., "css/ai_assistant.css"]
html_js_files = ["js/ai_assistant.js"]

# Rebuild docs
cd YOUR_DOCS && make html
```

## 📖 Usage

### For End Users

1. Open your VAST Orbit documentation in a browser
2. Click the "Ask AI" button on the right side
3. Type your question or click a quick prompt
4. Get instant, context-aware answers

### Example Questions

- "How do I get started with VAST Orbit?"
- "What's the syntax for creating a vDataFrame?"
- "Show me examples of machine learning with VAST Orbit"
- "How do I connect to VAST Database?"

## ⚙️ Configuration

### Backend Configuration

Edit `backend/app.py`:

```python
# Document chunk size
CHUNK_SIZE = 3000  # Increase for longer context

# Number of relevant chunks to retrieve
top_k=5  # in search_relevant_chunks()

# Claude model selection
model="claude-sonnet-4-20250514"  # Latest Sonnet model
```

### Frontend Configuration

Edit `frontend/ai_assistant.js`:

```javascript
// API endpoint
apiUrl: 'http://localhost:5000/api/ask'

// Customize quick prompts (line 35)
const quickPrompts = [
  { text: "Custom Prompt 1", prompt: "Your custom question here" },
  // Add more...
];
```

## 🎨 Customization

The AI assistant is designed to match VAST Orbit's branding:

- **Primary Color**: `#29b8ff` (VAST Orbit blue)
- **Dark Theme**: Automatic detection and adaptation
- **Font**: Inherits from your documentation
- **Position**: Fixed right side (configurable in CSS)

To customize colors, edit `frontend/ai_assistant.css`:

```css
.ask-ai-btn {
  background-color: #29b8ff; /* Change this */
}

.user-message {
  background-color: #29b8ff; /* And this */
}
```

## 🔐 Security

**Important security considerations:**

1. **API Key**: Never commit your `ANTHROPIC_API_KEY` to version control
2. **CORS**: Configure `flask-cors` for your specific domain in production
3. **Rate Limiting**: Add rate limiting to prevent abuse
4. **HTTPS**: Always use HTTPS in production
5. **Authentication**: Consider adding user authentication for the API endpoint

## 💰 Cost Estimation

Using Claude Sonnet 4:
- **Input tokens**: ~$3 per million tokens
- **Output tokens**: ~$15 per million tokens

Typical question costs:
- Simple query: $0.01 - $0.02
- Complex query with history: $0.03 - $0.05

For 1000 queries/month: ~$20-30

Monitor usage at: https://console.anthropic.com/

## 🚢 Deployment Options

### Local Development
✅ Current setup - perfect for testing

### Production (Cloud)
- Deploy backend on AWS/GCP/Azure
- Use environment variables for configuration
- Enable HTTPS and CORS for your domain
- Consider using a CDN for static assets

### Serverless
- Convert Flask app to AWS Lambda
- Use API Gateway for HTTP endpoint
- Deploy frontend with your static site

See [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md) for detailed deployment instructions.

## 🧪 Testing

### Test the Backend

```bash
# Start the server
python backend/app.py

# Test health endpoint
curl http://localhost:5000/api/health

# Test a question
curl -X POST http://localhost:5000/api/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is VAST Orbit?"}'
```

### Test the Frontend

1. Open your documentation with browser dev tools
2. Check for JavaScript errors in console
3. Verify network requests to the API
4. Test the chat interface functionality

## 📊 Monitoring

The backend includes:
- Health check endpoint: `/api/health`
- Console logging for debugging
- Error handling and user-friendly messages

For production, consider adding:
- Application monitoring (e.g., Sentry)
- API usage tracking
- Performance metrics

## 🛠️ Troubleshooting

### Common Issues

**Issue**: "API key not configured"
- **Solution**: Set `ANTHROPIC_API_KEY` environment variable

**Issue**: "No documents loaded"
- **Solution**: Verify `VASTORBIT_DOCS_DIR` points to built HTML docs

**Issue**: Chat interface doesn't appear
- **Solution**: Check that CSS/JS files are in `_static/` and referenced in `conf.py`

**Issue**: CORS errors
- **Solution**: Install `flask-cors`: `pip install flask-cors`

See [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md) for more troubleshooting tips.

## 🔄 Upgrade Path

### Current: Keyword-based Search
The current implementation uses simple keyword matching.

### Future: Vector Embeddings
For better accuracy, upgrade to vector search:

```bash
pip install sentence-transformers chromadb
```

Then modify `app.py` to use embeddings for document retrieval. This provides semantic search but requires more setup.

## 📝 Files Overview

```
vastorbit-ai-assistant/
├── frontend/
│   ├── ai_assistant.css      # Chat interface styles
│   └── ai_assistant.js        # Chat functionality
├── backend/
│   ├── app.py                 # Flask API + RAG system
│   └── requirements.txt       # Python dependencies
├── INTEGRATION_GUIDE.md       # Detailed setup instructions
├── README.md                  # This file
└── quickstart.sh              # Quick setup script
```

## 🤝 Contributing

Suggestions for improvements:
- Vector embeddings for better search
- Conversation threading
- User feedback collection
- Response caching
- Multi-language support
- Voice input

## 📄 License

This project is part of VAST Orbit documentation tools.

## 🙏 Acknowledgments

- Built with [Anthropic Claude](https://www.anthropic.com/)
- Designed to complement [Sphinx](https://www.sphinx-doc.org/) documentation
- Inspired by modern documentation AI assistants

## 📧 Support

For issues or questions:
1. Check the [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md)
2. Review this README
3. Check the troubleshooting sections
4. Test with `/api/health` endpoint

---

**Ready to make your VAST Orbit documentation more interactive?**

Start with `./quickstart.sh` and follow the integration guide! 🚀
