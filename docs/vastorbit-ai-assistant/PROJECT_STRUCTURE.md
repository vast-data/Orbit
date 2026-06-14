# VAST Orbit AI Assistant - Project Structure

```
vastorbit-ai-assistant/
│
├── README.md                    # Main documentation and overview
├── INTEGRATION_GUIDE.md         # Detailed integration instructions
├── quickstart.sh               # Quick setup and run script
├── test_api.py                 # Test script to verify setup
│
├── frontend/                   # Frontend files (add to your Sphinx docs)
│   ├── ai_assistant.css       # Chat interface styles
│   └── ai_assistant.js        # Chat functionality and API calls
│
└── backend/                    # Backend API server
    ├── app.py                 # Flask server + RAG implementation
    ├── requirements.txt       # Python dependencies
    └── .env.example          # Environment configuration template

```

## File Descriptions

### Root Files

**README.md**
- Main project documentation
- Features overview
- Quick start guide
- Architecture diagram
- Configuration options
- Troubleshooting

**INTEGRATION_GUIDE.md**
- Step-by-step integration with Sphinx
- Configuration details
- Deployment options
- Advanced customization
- Production setup

**quickstart.sh**
- Automated setup script
- Checks Python version
- Installs dependencies
- Prompts for API key and docs directory
- Starts the server

**test_api.py**
- Automated testing script
- Verifies environment variables
- Tests health endpoint
- Tests ask endpoint
- Provides diagnostic output

### Frontend Files (To be added to your Sphinx docs)

**frontend/ai_assistant.css** (~ 400 lines)
- Complete styling for the chat interface
- VAST Orbit brand colors (#29b8ff)
- Dark mode support
- Responsive design
- Animations and transitions

**frontend/ai_assistant.js** (~ 250 lines)
- Chat interface logic
- API communication
- Message formatting
- Conversation history management
- Quick prompts functionality
- Error handling

### Backend Files

**backend/app.py** (~ 300 lines)
- Flask API server
- RAG (Retrieval Augmented Generation) system
- Document loading and chunking
- Keyword-based search
- Claude API integration
- CORS configuration

**backend/requirements.txt**
```
flask==3.0.0
flask-cors==4.0.0
anthropic==0.40.0
python-dotenv==1.0.0
```

**backend/.env.example**
- Template for environment variables
- API key configuration
- Documentation directory path
- Optional Flask settings

## Integration Points

### In Your Sphinx Documentation

Add these to your `conf.py`:

```python
html_css_files = [
    # ... your existing CSS files ...
    "css/ai_assistant.css",  # Add this
]

html_js_files = [
    "js/ai_assistant.js",    # Add this
]
```

Copy files:
```bash
cp frontend/ai_assistant.css YOUR_DOCS/source/_static/css/
cp frontend/ai_assistant.js YOUR_DOCS/source/_static/js/
```

## Data Flow

```
User Browser (Sphinx Docs)
         ↓
   ai_assistant.js (Frontend)
         ↓ HTTP POST /api/ask
   Flask Server (Backend)
         ↓
   RAG System (Document Search)
         ↓
   Claude API (Anthropic)
         ↓
   Response → User
```

## Quick Reference

### Start the Backend
```bash
cd backend
export ANTHROPIC_API_KEY="your_key"
export VASTORBIT_DOCS_DIR="/path/to/docs"
python app.py
```

### Test the Setup
```bash
python test_api.py
```

### Integrate with Docs
```bash
./quickstart.sh  # Follow prompts
```

## Configuration Files

### Backend (.env)
```bash
ANTHROPIC_API_KEY=sk-ant-...
VASTORBIT_DOCS_DIR=/home/user/vastorbit/docs/build/html
```

### Frontend (conf.py)
```python
html_css_files = ["css/custom_styling.css", "css/ai_assistant.css"]
html_js_files = ["js/ai_assistant.js"]
```

## Size Summary

- Frontend CSS: ~15 KB
- Frontend JS: ~10 KB
- Backend: ~25 KB
- Total: ~50 KB

## Dependencies

### Frontend
- jQuery (already included in your Sphinx docs)
- No additional dependencies

### Backend
- Python 3.8+
- Flask (web framework)
- Anthropic SDK (Claude API)
- Flask-CORS (cross-origin requests)

## Next Steps

1. Read README.md for overview
2. Follow INTEGRATION_GUIDE.md for setup
3. Run quickstart.sh for automated setup
4. Test with test_api.py
5. Customize as needed

## Support

Each file contains detailed comments and documentation. Check:
- Inline comments in code files
- README.md troubleshooting section
- INTEGRATION_GUIDE.md for detailed steps
