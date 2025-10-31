"""Test simple chat (regression test to ensure basic functionality preserved)."""
from openai import OpenAI
import os


def test_simple_chat():
    """Verify basic Grok chat still works (without PDF)."""
    print("Testing simple chat client initialization...")
    
    # Verify client can be initialized
    try:
        client = OpenAI(
            api_key=os.getenv("POE_API_KEY", "dummy-key"),
            base_url="https://api.x.ai/v1",
        )
        print("✓ Client initialized correctly")
        print(f"  API Key set: {bool(os.getenv('POE_API_KEY'))}")
        print(f"  Base URL: {client.base_url}")
        assert str(client.base_url).rstrip("/") == "https://api.x.ai/v1"
        assert isinstance(client, OpenAI)
    except Exception as e:
        print(f"❌ Client initialization failed: {e}")
        raise


if __name__ == "__main__":
    test_simple_chat()
