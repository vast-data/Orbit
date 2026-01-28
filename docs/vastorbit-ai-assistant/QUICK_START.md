# 🚀 VastOrbit AI Assistant - Quick Reference Card

## What You Got

A complete AI-powered documentation assistant for VastOrbit with:
- ✅ Chat interface matching your design
- ✅ Claude-powered intelligent responses
- ✅ RAG system for accurate answers
- ✅ Ready-to-integrate with your Sphinx docs

## 3-Step Setup

### 1️⃣ Set Up Backend
```bash
cd vastorbit-ai-assistant
./quickstart.sh
```

### 2️⃣ Integrate Frontend
```bash
# Copy files to your Sphinx docs
cp frontend/ai_assistant.css YOUR_DOCS/source/_static/css/
cp frontend/ai_assistant.js YOUR_DOCS/source/_static/js/

# Update conf.py - add these lines:
html_css_files = [
    "css/custom_styling.css",
    "css/ai_assistant.css",  # ← Add this
    # ... rest of your files
]

html_js_files = [
    "js/ai_assistant.js",  # ← Add this entire section if not present
]

# Rebuild docs
cd YOUR_DOCS && make html
```

### 3️⃣ Test It
```bash
# Open your docs in browser
# Click the "Ask AI" button on the right side
# Try: "How do I get started with VastOrbit?"
```

## Required Environment Variables

```bash
export ANTHROPIC_API_KEY="sk-ant-..." # Get from console.anthropic.com
export VASTORBIT_DOCS_DIR="/path/to/docs/build/html"
```

Or create `backend/.env`:
```
ANTHROPIC_API_KEY=sk-ant-...
VASTORBIT_DOCS_DIR=/path/to/docs/build/html
```

## Files Overview

```
📁 vastorbit-ai-assistant/
├── 📄 README.md                  ← Start here
├── 📄 INTEGRATION_GUIDE.md       ← Detailed setup
├── 🔧 quickstart.sh              ← Run this first
├── 🧪 test_api.py                ← Test your setup
│
├── 📁 frontend/
│   ├── 🎨 ai_assistant.css       ← Copy to _static/css/
│   └── ⚡ ai_assistant.js        ← Copy to _static/js/
│
└── 📁 backend/
    ├── 🐍 app.py                 ← Flask API server
    ├── 📋 requirements.txt       ← Dependencies
    └── 📝 .env.example          ← Config template
```

## Quick Commands

```bash
# Start backend server
cd backend && python app.py

# Test the setup
python test_api.py

# Check server health
curl http://localhost:5000/api/health
```

## Customization Hot Spots

### Change Colors
Edit `frontend/ai_assistant.css`:
```css
.ask-ai-btn {
  background-color: #YOUR_COLOR;
}
```

### Change Quick Prompts
Edit `frontend/ai_assistant.js` (line ~35):
```javascript
data-prompt="Your custom question here"
```

### Change Model
Edit `backend/app.py` (line ~145):
```python
model="claude-sonnet-4-20250514"  # or another model
```

## Troubleshooting Checklist

- [ ] API key set in environment
- [ ] Docs directory exists and has .html files
- [ ] Backend server is running (localhost:5000)
- [ ] CSS/JS files copied to _static/
- [ ] conf.py updated with new files
- [ ] Docs rebuilt with `make html`

## Cost Estimate

- Simple questions: $0.01-0.02 per query
- Complex questions: $0.03-0.05 per query
- 1000 queries/month: ~$20-30

Monitor at: https://console.anthropic.com/

## Get Help

1. Check README.md (overview & troubleshooting)
2. Check INTEGRATION_GUIDE.md (detailed steps)
3. Run `python test_api.py` (diagnostic)
4. Check backend logs (in terminal running app.py)
5. Check browser console (F12) for frontend errors

## Next Steps

✅ Run `./quickstart.sh` to get started
✅ Read INTEGRATION_GUIDE.md for detailed instructions
✅ Customize the quick prompts for your users
✅ Test with real documentation questions
✅ Deploy to production (see deployment guide)

## Production Checklist

- [ ] Use HTTPS for API endpoint
- [ ] Set up proper CORS for your domain
- [ ] Add rate limiting to API
- [ ] Monitor API usage and costs
- [ ] Set up error tracking (e.g., Sentry)
- [ ] Consider caching common questions

---

**Ready to go? Start with:** `./quickstart.sh`

For questions, check the README.md or INTEGRATION_GUIDE.md!
