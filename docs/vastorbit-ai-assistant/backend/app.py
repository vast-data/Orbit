"""
VAST Orbit AI Assistant Backend - IMPROVED VERSION
Enhanced performance and better response phrasing
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import anthropic
import os
import json
from pathlib import Path
import re
from typing import List, Dict, Tuple
import hashlib
from functools import lru_cache

app = Flask(__name__)
CORS(app)

# Configuration
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
DOCS_DIR = os.environ.get("VASTORBIT_DOCS_DIR", "./docs_content")
MAX_CONTEXT_LENGTH = 100000
CHUNK_SIZE = 2000  # REDUCED from 3000 for better performance
MAX_CHUNKS = 3  # REDUCED from 5 for faster responses


class DocumentationRAG:
    """Retrieval Augmented Generation for VAST Orbit documentation"""

    def __init__(self, docs_dir: str):
        self.docs_dir = Path(docs_dir)
        self.documents = []
        self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        self.load_documents()
        self.response_cache = {}  # Simple cache for common questions

    def load_documents(self):
        """Load and chunk documentation files"""
        print(f"Loading documents from {self.docs_dir}...")

        if not self.docs_dir.exists():
            print(f"Warning: Documentation directory {self.docs_dir} does not exist!")
            return

        # Find all HTML files (skip RST and MD for faster loading)
        html_files = list(self.docs_dir.rglob("*.html"))

        # Filter out non-content files
        content_files = [
            f
            for f in html_files
            if not any(
                skip in str(f)
                for skip in ["search.html", "genindex.html", "_static", "_sources"]
            )
        ]

        for file_path in content_files:
            try:
                content = file_path.read_text(encoding="utf-8")

                # Clean the content
                content = self.clean_html(content)

                # Skip if too short (likely not real content)
                if len(content) < 200:
                    continue

                # Create chunks
                chunks = self.chunk_text(content, file_path)
                self.documents.extend(chunks)

            except Exception as e:
                print(f"Error loading {file_path}: {e}")

        print(
            f"Loaded {len(self.documents)} document chunks from {len(content_files)} files"
        )

    def clean_html(self, html_content: str) -> str:
        """Remove HTML tags and extract text - OPTIMIZED"""
        # Remove script and style elements
        html_content = re.sub(
            r"<script[^>]*>.*?</script>",
            "",
            html_content,
            flags=re.DOTALL | re.IGNORECASE,
        )
        html_content = re.sub(
            r"<style[^>]*>.*?</style>",
            "",
            html_content,
            flags=re.DOTALL | re.IGNORECASE,
        )

        # Remove navigation and header elements
        html_content = re.sub(
            r"<nav[^>]*>.*?</nav>", "", html_content, flags=re.DOTALL | re.IGNORECASE
        )
        html_content = re.sub(
            r"<header[^>]*>.*?</header>",
            "",
            html_content,
            flags=re.DOTALL | re.IGNORECASE,
        )

        # Remove HTML tags but keep content
        text = re.sub(r"<[^>]+>", " ", html_content)

        # Clean up whitespace
        text = re.sub(r"\s+", " ", text)
        text = text.strip()

        return text

    def chunk_text(self, text: str, file_path: Path) -> List[Dict]:
        """Split text into chunks with metadata - OPTIMIZED"""
        chunks = []

        # Split by paragraphs/sections
        sections = text.split("\n\n")
        current_chunk = ""

        for section in sections:
            if len(current_chunk) + len(section) < CHUNK_SIZE:
                current_chunk += section + "\n\n"
            else:
                if current_chunk:
                    chunks.append(
                        {
                            "content": current_chunk.strip(),
                            "source": str(file_path.relative_to(self.docs_dir)),
                            "file_path": str(file_path),
                            "chunk_id": hashlib.md5(current_chunk.encode()).hexdigest()[
                                :8
                            ],
                        }
                    )
                current_chunk = section + "\n\n"

        # Add the last chunk
        if current_chunk:
            chunks.append(
                {
                    "content": current_chunk.strip(),
                    "source": str(file_path.relative_to(self.docs_dir)),
                    "file_path": str(file_path),
                    "chunk_id": hashlib.md5(current_chunk.encode()).hexdigest()[:8],
                }
            )

        return chunks

    @lru_cache(maxsize=100)
    def _cached_search(self, query: str, top_k: int) -> tuple:
        """Cached search for common queries"""
        results = self.search_relevant_chunks(query, top_k)
        return tuple((r["content"], r["source"]) for r in results)

    def search_relevant_chunks(self, query: str, top_k: int = MAX_CHUNKS) -> List[Dict]:
        """OPTIMIZED keyword-based search for relevant document chunks"""
        # Tokenize query
        query_terms = set(re.findall(r"\w+", query.lower()))

        # Remove common words for better matching
        stop_words = {
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "is",
            "are",
            "how",
            "what",
            "i",
            "do",
        }
        query_terms = query_terms - stop_words

        if not query_terms:
            return []

        # Score each document
        scored_docs = []
        for doc in self.documents:
            content_lower = doc["content"].lower()

            # Count matching terms with position weighting
            matches = 0
            for term in query_terms:
                if term in content_lower:
                    # Give extra weight if term appears in first 100 chars
                    if term in content_lower[:100]:
                        matches += 2
                    else:
                        matches += 1

            if matches > 0:
                # Calculate score
                score = (matches / len(query_terms)) * 100
                scored_docs.append((score, doc))

        # Sort by score and return top_k
        scored_docs.sort(key=lambda x: x[0], reverse=True)
        return [doc for _, doc in scored_docs[:top_k]]

    def generate_answer(
        self, question: str, conversation_history: List[Dict] = None
    ) -> Tuple[str, List[Dict]]:
        """Generate answer using Claude with relevant documentation context"""

        # Check cache first
        cache_key = hashlib.md5(question.lower().encode()).hexdigest()
        if cache_key in self.response_cache:
            print("Cache hit!")
            return self.response_cache[cache_key]

        # Find relevant documentation
        relevant_chunks = self.search_relevant_chunks(question, top_k=MAX_CHUNKS)

        # Build context
        context = "\n\n---\n\n".join(
            [
                f"Source: {chunk['source']}\n\n{chunk['content']}"
                for chunk in relevant_chunks
            ]
        )

        # Build conversation history (keep it short for performance)
        messages = []
        if conversation_history:
            for exchange in conversation_history[-2:]:  # Only last 2 exchanges
                messages.append(
                    {"role": "user", "content": exchange.get("question", "")}
                )
                messages.append(
                    {"role": "assistant", "content": exchange.get("answer", "")}
                )

        # Add current question
        messages.append({"role": "user", "content": question})

        # IMPROVED System prompt - VAST-focused, emphasizes data prep and exploration
        system_prompt = f"""You are Astra, VAST Orbit's AI documentation assistant. VAST Orbit is a Python library that brings data science to VAST Database with in-database execution.

Your role is to help users prepare data, explore it interactively, and build ML workflows - all directly in VAST Database.

Key Messaging:
- Emphasize "data preparation" - cleaning, transforming, feature engineering in VAST
- Highlight "interactive exploration" - charts, visualizations, statistical analysis
- Focus on "in-database processing" - all operations execute in VAST, not Python
- VAST Orbit has embedded ML models - no sklearn import needed
- Models are in vastorbit.machine_learning.vast (same import path as VerticaPy)

Important Syntax:
- Charts: vdf["column"].hist(nbins=20) NOT vdf.hist("column", bins=20)
- groupby: result.groupby(['col1'], ['sum(col2)', 'avg(col3)'])
- fillna with dict or value: vdf.fillna({{'col': 0}}) or vdf.fillna(0)
- Models: from vastorbit.machine_learning.vast import RandomForestClassifier
- Version 0.1.0 is BETA, production ready is 1.0.0

Response Guidelines:
- Answer directly and naturally
- Be conversational and helpful
- Emphasize data prep and exploration
- Use correct VAST Orbit syntax
- Show embedded models, not sklearn imports
- Keep responses concise

Here is the relevant documentation context:

<documentation>
{context}
</documentation>

Answer naturally, focusing on data preparation, exploration, and analytics in VAST."""

        try:
            # Call Claude API
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1500,  # Reduced from 2000 for faster responses
                system=system_prompt,
                messages=messages,
            )

            answer = response.content[0].text

            # Prepare sources - format for Sphinx URLs
            sources = []
            for chunk in relevant_chunks[:2]:  # Only show top 2 sources
                source_path = chunk["source"]
                # Remove .html extension and convert to page name
                page_name = source_path.replace(".html", "").replace("\\", "/")
                # Create user-friendly title
                title = page_name.split("/")[-1].replace("_", " ").title()
                sources.append(
                    {
                        "title": title,
                        "url": f"{page_name}.html",  # Relative path works in Sphinx
                    }
                )

            # Cache the result
            result = (answer, sources)
            self.response_cache[cache_key] = result

            return result

        except Exception as e:
            print(f"Error calling Claude API: {e}")
            return f"I encountered an error processing your question: {str(e)}", []


# Initialize RAG system
rag_system = None


@app.before_request
def initialize_rag():
    """Initialize RAG system on first request"""
    global rag_system
    if rag_system is None:
        if not ANTHROPIC_API_KEY:
            print(
                "WARNING: ANTHROPIC_API_KEY not set! Please set it as an environment variable."
            )
        rag_system = DocumentationRAG(DOCS_DIR)


@app.route("/api/ask", methods=["POST"])
def ask():
    """Handle AI assistant questions"""
    try:
        data = request.json
        question = data.get("question", "")
        conversation_history = data.get("conversation_history", [])

        if not question:
            return jsonify({"error": "Question is required"}), 400

        if not ANTHROPIC_API_KEY:
            return (
                jsonify(
                    {
                        "error": "API key not configured",
                        "answer": "Sorry, Astra is not properly configured. Please set the ANTHROPIC_API_KEY environment variable.",
                    }
                ),
                500,
            )

        # Generate answer
        answer, sources = rag_system.generate_answer(question, conversation_history)

        return jsonify({"answer": answer, "sources": sources, "question": question})

    except Exception as e:
        print(f"Error in /api/ask: {e}")
        return (
            jsonify(
                {
                    "error": str(e),
                    "answer": "I encountered an error processing your question. Please try again.",
                }
            ),
            500,
        )


@app.route("/api/health", methods=["GET"])
def health():
    """Health check endpoint"""
    return jsonify(
        {
            "status": "healthy",
            "documents_loaded": len(rag_system.documents) if rag_system else 0,
            "api_key_configured": bool(ANTHROPIC_API_KEY),
            "cache_size": len(rag_system.response_cache) if rag_system else 0,
        }
    )


@app.route("/api/clear-cache", methods=["POST"])
def clear_cache():
    """Clear the response cache"""
    if rag_system:
        rag_system.response_cache.clear()
        return jsonify({"message": "Cache cleared"})
    return jsonify({"error": "RAG system not initialized"}), 500


@app.route("/", methods=["GET"])
def index():
    """Root endpoint"""
    return jsonify(
        {
            "message": "Astra - VAST Orbit AI Assistant API",
            "version": "1.1.0",
            "endpoints": {
                "/api/ask": "POST - Ask a question",
                "/api/health": "GET - Health check",
                "/api/clear-cache": "POST - Clear response cache",
            },
        }
    )


if __name__ == "__main__":
    print("=" * 60)
    print("Astra - VAST Orbit AI Assistant API Server")
    print("=" * 60)
    print(f"Documentation directory: {DOCS_DIR}")
    print(f"API Key configured: {bool(ANTHROPIC_API_KEY)}")
    print(f"Chunk size: {CHUNK_SIZE} chars")
    print(f"Max chunks per query: {MAX_CHUNKS}")
    print()
    print("Starting server on http://localhost:8010")
    print("=" * 60)

    # Use port 5001 to avoid macOS AirPlay conflict
    app.run(debug=True, host="0.0.0.0", port=8010)
