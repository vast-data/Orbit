#!/usr/bin/env python3
"""
VAST Orbit AI Assistant - Test Script
Verifies that the backend is working correctly
"""

import os
import sys
import requests
import json


def test_health():
    """Test the health endpoint"""
    print("Testing health endpoint...")
    try:
        response = requests.get("http://localhost:5000/api/health", timeout=5)
        response.raise_for_status()
        data = response.json()

        print(f"✓ Health check passed")
        print(f"  - Status: {data.get('status')}")
        print(f"  - Documents loaded: {data.get('documents_loaded')}")
        print(f"  - API key configured: {data.get('api_key_configured')}")
        return True
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to server. Is it running?")
        print("  Start it with: python backend/app.py")
        return False
    except Exception as e:
        print(f"✗ Health check failed: {e}")
        return False


def test_ask():
    """Test the ask endpoint"""
    print("\nTesting ask endpoint...")
    try:
        question = "What is VAST Orbit?"
        payload = {"question": question, "conversation_history": []}

        response = requests.post(
            "http://localhost:5000/api/ask", json=payload, timeout=30
        )
        response.raise_for_status()
        data = response.json()

        print(f"✓ Ask endpoint working")
        print(f"  Question: {question}")
        print(f"  Answer preview: {data.get('answer', '')[:100]}...")
        print(f"  Sources: {len(data.get('sources', []))} references")
        return True
    except requests.exceptions.Timeout:
        print("✗ Request timed out (Claude API might be slow)")
        return False
    except Exception as e:
        print(f"✗ Ask endpoint failed: {e}")
        if hasattr(e, "response"):
            print(f"  Response: {e.response.text}")
        return False


def check_environment():
    """Check environment variables"""
    print("Checking environment variables...")

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    docs_dir = os.environ.get("VASTORBIT_DOCS_DIR")

    if not api_key:
        print("✗ ANTHROPIC_API_KEY not set")
        print("  Set it with: export ANTHROPIC_API_KEY='your_key'")
        return False
    else:
        print(f"✓ ANTHROPIC_API_KEY is set ({api_key[:10]}...)")

    if not docs_dir:
        print("⚠ VASTORBIT_DOCS_DIR not set (will use default)")
    else:
        if os.path.exists(docs_dir):
            print(f"✓ VASTORBIT_DOCS_DIR exists: {docs_dir}")
        else:
            print(f"⚠ VASTORBIT_DOCS_DIR does not exist: {docs_dir}")

    return True


def main():
    print("=" * 60)
    print("VAST Orbit AI Assistant - Test Suite")
    print("=" * 60)
    print()

    # Check environment
    env_ok = check_environment()
    print()

    if not env_ok:
        print("⚠ Environment check failed. Some tests may not work.")
        print()

    # Test health
    health_ok = test_health()

    if not health_ok:
        print("\nTests stopped - server is not running")
        sys.exit(1)

    # Test ask endpoint
    ask_ok = test_ask()

    print("\n" + "=" * 60)
    if health_ok and ask_ok:
        print("✓ All tests passed! The AI assistant is ready.")
    else:
        print("⚠ Some tests failed. Check the output above.")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
        sys.exit(1)
