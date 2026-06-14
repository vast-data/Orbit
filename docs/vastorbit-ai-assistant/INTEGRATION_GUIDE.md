# VAST Orbit AI Assistant - Integration Guide

This guide shows you how to integrate the AI assistant into your VAST Orbit Sphinx documentation.

## Overview

The AI assistant consists of:
1. **Frontend**: CSS + JavaScript for the chat interface
2. **Backend**: Flask API server with Claude-powered RAG
3. **Integration**: Simple updates to your Sphinx configuration

## Prerequisites

- Python 3.8+
- Anthropic API key ([get one here](https://console.anthropic.com/))
- Your built Sphinx documentation

## Step 1: Add Frontend Files to Your Docs

Copy the frontend files to your documentation's static directory:

```bash
# From your VAST Orbit project root
cp ai_assistant.css docs/source/_static/css/
cp ai_assistant.js docs/source/_static/js/
```

## Step 2: Update conf.py

Add the CSS and JS files to your Sphinx configuration:

### Add to `html_css_files` list (around line 294):

```python
html_css_files = [
    "css/custom_styling.css",
    "css/ai_assistant.css",  # Add this line
    "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap",
    # ... rest of your CSS files
]
```

### Add `html_js_files` configuration:

```python
html_js_files = [
    "js/ai_assistant.js",
]
```

Add this after your `html_css_files` configuration (around line 302).

### Optional: Configure API URL

If you want to use a custom API URL (not localhost), add this to your conf.py:

```python
# In the rst_prolog section, after the existing JavaScript (around line 120)
    <script>
    window.VASTORBIT_AI_API_URL = 'http://your-api-server:5000/api/ask';
    </script>
```

## Step 3: Set Up the Backend

### Install Dependencies

```bash
cd backend/
pip install -r requirements.txt
```

### Configure Environment Variables

Create a `.env` file in the backend directory:

```bash
# backend/.env
ANTHROPIC_API_KEY=your_anthropic_api_key_here
VASTORBIT_DOCS_DIR=/path/to/your/docs/build/html
```

Or export them directly:

```bash
export ANTHROPIC_API_KEY="your_anthropic_api_key_here"
export VASTORBIT_DOCS_DIR="/path/to/your/docs/build/html"
```

### Run the Backend Server

```bash
python app.py
```

The server will start on `http://localhost:5000`

## Step 4: Rebuild Your Documentation

```bash
cd docs/
make html
```

## Step 5: Test the Integration

1. Open your documentation in a browser
2. You should see an "Ask AI" button on the right side of the screen
3. Click it to open the chat interface
4. Try asking: "How do I get started with VAST Orbit?"

## Configuration Options

### Backend Configuration

Edit `backend/app.py` to customize:

```python
# Number of document chunks to retrieve
top_k=5  # in search_relevant_chunks()

# Chunk size for documents
CHUNK_SIZE = 3000  # Characters per chunk

# Claude model
model="claude-sonnet-4-20250514"  # in generate_answer()
```

### Frontend Configuration

Edit `frontend/ai_assistant.js` to customize:

```javascript
// API endpoint
apiUrl: 'http://localhost:5000/api/ask'

// Quick prompts (around line 35)
const quickPrompts = [
  { text: "Getting Started", prompt: "How do I get started with VAST Orbit?" },
  { text: "Main Features", prompt: "What are the main features?" },
  // Add your own prompts here
];
```

## Deployment Options

### Option 1: Local Development (Current Setup)
- Frontend: Served with your Sphinx docs
- Backend: Run locally with `python app.py`
- Best for: Development and testing

### Option 2: Production Deployment

#### Backend Deployment (Choose one):

**A. Docker Container:**

Create `backend/Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app.py .

ENV ANTHROPIC_API_KEY=""
ENV VASTORBIT_DOCS_DIR="/docs"

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "app:app"]
```

Build and run:
```bash
docker build -t vastorbit-ai-backend .
docker run -p 5000:5000 \
  -e ANTHROPIC_API_KEY="your_key" \
  -v /path/to/docs:/docs \
  vastorbit-ai-backend
```

**B. Cloud Platform (AWS, GCP, Azure):**
- Deploy the Flask app as a container or serverless function
- Set environment variables in your cloud platform
- Update the API URL in your frontend

#### Frontend Update:

Update the API URL in your `conf.py`:

```python
    <script>
    window.VASTORBIT_AI_API_URL = 'https://your-production-api.com/api/ask';
    </script>
```

### Option 3: Serverless (AWS Lambda + API Gateway)

The backend can be adapted for serverless:
1. Wrap the Flask app with a serverless adapter (e.g., Mangum)
2. Deploy to AWS Lambda
3. Set up API Gateway
4. Update the frontend API URL

## Advanced: Using Vector Embeddings

For better search accuracy, you can upgrade the RAG system to use embeddings:

```python
# Install additional dependencies
pip install sentence-transformers chromadb

# Update app.py to use vector search instead of keyword search
# This requires more setup but provides better retrieval
```

## Troubleshooting

### Issue: "API key not configured"
**Solution**: Make sure `ANTHROPIC_API_KEY` is set in your environment or `.env` file

### Issue: "No documents loaded"
**Solution**: Check that `VASTORBIT_DOCS_DIR` points to your built documentation (`docs/build/html`)

### Issue: Chat interface doesn't appear
**Solution**: 
1. Check browser console for JavaScript errors
2. Ensure `ai_assistant.js` and `ai_assistant.css` are in your `_static` directory
3. Verify they're added to `conf.py`
4. Rebuild your docs with `make html`

### Issue: CORS errors
**Solution**: Make sure `flask-cors` is installed and enabled in `app.py`

### Issue: Slow responses
**Solution**: 
1. Reduce the number of chunks retrieved (`top_k=3` instead of 5)
2. Decrease `CHUNK_SIZE` for faster processing
3. Use a faster Claude model (though Sonnet 4 is recommended)

## Security Considerations

For production deployments:

1. **API Key Security**: Never commit API keys to git. Use environment variables or secret managers
2. **Rate Limiting**: Add rate limiting to prevent abuse
3. **CORS**: Configure CORS properly for your domain only
4. **HTTPS**: Always use HTTPS in production
5. **Authentication**: Consider adding user authentication for the AI endpoint

## Cost Considerations

- Claude API calls are charged per token
- Typical question: ~$0.01-0.03 per query
- Monitor usage in the Anthropic Console
- Consider caching common questions

## Next Steps

1. Customize the quick prompts for your use case
2. Adjust the system prompt in `app.py` to match your documentation style
3. Add rate limiting for production use
4. Implement conversation persistence (currently stored in browser)
5. Add feedback buttons to improve responses

## Support

For issues or questions:
- Check the troubleshooting section above
- Review the code comments in `app.py` and `ai_assistant.js`
- Test with the `/api/health` endpoint

Enjoy your AI-powered documentation! 🚀
