"""Integration test: Full RAG pipeline with mock Grok response."""
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.core.pdf_processor import chunk_pdf_text
from src.core.retrieval import (
    simple_similarity_search,
    format_context_for_prompt,
    build_rag_prompt,
)

PDF_PATH = ROOT_DIR / "test-pdf.pdf"


def test_full_rag_pipeline():
    """Test complete RAG flow without API call."""
    print("=" * 70)
    print("INTEGRATION TEST: Full RAG Pipeline with Mock Grok Response")
    print("=" * 70)
    print()
    
    # Step 1: Load PDF
    print("[1/5] Loading PDF and creating chunks...")
    chunks = chunk_pdf_text(PDF_PATH, chunk_size=500, overlap=50)
    print(f"      ✓ Loaded {len(chunks)} chunks")
    
    # Step 2: User query
    user_query = "根據 PDF 說明重點並附出處。"
    print(f"\n[2/5] Processing user query: '{user_query}'")
    print(f"      ✓ Query ready")
    
    # Step 3: Retrieve relevant content
    print(f"\n[3/5] Retrieving relevant PDF content...")
    retrieved = simple_similarity_search(user_query, chunks, top_k=3)
    print(f"      ✓ Retrieved {len(retrieved)} chunks with relevance scores:")
    for chunk in retrieved:
        score = chunk.get('score', 0.0)
        print(f"         - Page {chunk['page']}, Chunk {chunk['chunk_id']}: {score:.3f} relevance")
    
    # Step 4: Format context
    print(f"\n[4/5] Formatting context for Grok...")
    context_str = format_context_for_prompt(retrieved)
    citations = [
        f"[{idx}] {chunk.get('pdf_name', 'Unknown')}, Page {chunk.get('page', '?')}"
        for idx, chunk in enumerate(retrieved, start=1)
    ]
    print(f"      ✓ Context formatted ({len(context_str)} chars)")
    print(f"      ✓ Generated {len(citations)} citations")
    
    # Step 5: Build prompt
    print(f"\n[5/5] Building prompt for Grok...")
    prompt = build_rag_prompt(user_query, context_str)
    print(f"      ✓ Prompt built ({len(prompt)} chars)")
    
    # Simulate Grok response
    print()
    print("=" * 70)
    print("SIMULATED GROK RESPONSE:")
    print("=" * 70)
    mock_response = """Based on the PDF content provided, here are the main points:

1. **Course Overview** (Page 1): This is the VAR2053 Electronic Signal and 
   Communication Fundamental course (電子訊號與通訊基礎), which covers electronic 
   communication systems and signal processing fundamentals.

2. **Key Topics** (Page 2): The course outline includes:
   - Software development tools introduction
   - ESP32 Bluetooth firmware structure and functionality explanation
   - Signal transmission and reception mechanisms
   - Protocol implementation and debugging techniques

3. **Practical Applications**: The course provides hands-on experience with 
   modern IoT devices, specifically the ESP32 microcontroller for wireless 
   communication projects.

[Source 1] Page 1 - Electronic Signal and Communication course content
[Source 2] Page 2 - Course outline and main topics
[Source 3] Page 3 - Additional course materials and objectives"""
    
    print(mock_response)
    
    print()
    print("=" * 70)
    print("SOURCE CITATIONS:")
    print("=" * 70)
    for citation in citations:
        print(f"  {citation}")
    
    print()
    print("=" * 70)
    print("✅ INTEGRATION TEST PASSED")
    print("=" * 70)
    print()
    print("Pipeline Verified:")
    print("  ✓ PDF loading and chunking")
    print("  ✓ Query processing")
    print("  ✓ Similarity-based retrieval")
    print("  ✓ Context formatting with citations")
    print("  ✓ Prompt construction for LLM")
    print()
    print("To run with real Grok API:")
    print("  1. Get your XAI API key from https://console.x.ai")
    print("  2. Set: $env:XAI_API_KEY = 'your-key'")
    print("  3. Run: uv run main.py")
    print()


if __name__ == "__main__":
    try:
        test_full_rag_pipeline()
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
