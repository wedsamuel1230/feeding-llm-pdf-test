"""Test script for RAG pipeline (without API call)."""
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.core.pdf_processor import chunk_pdf_text
from src.core.retrieval import simple_similarity_search, format_context_for_prompt


def test_pdf_loading():
    """Test PDF loading and chunking."""
    print("=" * 60)
    print("TEST 1: PDF Loading & Chunking")
    print("=" * 60)
    
    pdf_path = ROOT_DIR / "test-pdf.pdf"
    chunks = chunk_pdf_text(pdf_path, chunk_size=500, overlap=50)
    
    print(f"✓ Successfully loaded PDF")
    print(f"  Total chunks: {len(chunks)}")
    assert len(chunks) > 0, "No chunks extracted from PDF"
    
    # Verify chunk structure
    sample_chunk = chunks[0]
    assert 'text' in sample_chunk, "Chunk missing 'text' field"
    assert 'page' in sample_chunk, "Chunk missing 'page' field"
    assert 'chunk_id' in sample_chunk, "Chunk missing 'chunk_id' field"
    print(f"✓ Chunk structure verified")
    print(f"  Sample chunk (ID {sample_chunk['chunk_id']}, Page {sample_chunk['page']}):")
    print(f"    Preview: {sample_chunk['text'][:100]}...\n")
    
    return chunks


def test_retrieval(chunks):
    """Test retrieval and context formatting."""
    print("=" * 60)
    print("TEST 2: Retrieval & Context Formatting")
    print("=" * 60)
    
    queries = [
        "根據 PDF 說明重點並附出處。",
        "What are the main topics?",
        "PDF content overview"
    ]
    
    for query in queries:
        print(f"Query: '{query}'")
        retrieved = simple_similarity_search(query, chunks, top_k=3)
        print(f"  ✓ Found {len(retrieved)} relevant chunks")
        
        if retrieved:
            context_str = format_context_for_prompt(retrieved)
            print(f"  ✓ Formatted context with {len(retrieved)} citations")
            print(f"  ✓ Context length: {len(context_str)} chars")
            
            # Show sample citations
            for idx, chunk in enumerate(retrieved[:2], start=1):
                pdf_name = chunk.get('pdf_name', 'Unknown')
                page = chunk.get('page', '?')
                text_preview = chunk['text'][:80]
                print(f"    Citation {idx}: [{idx}] {pdf_name}, Page {page} - {text_preview}...")
        print()


def test_prompt_building(chunks):
    """Test prompt construction for Grok."""
    print("=" * 60)
    print("TEST 3: Prompt Construction")
    print("=" * 60)
    
    from src.core.retrieval import build_rag_prompt
    
    query = "What is this PDF about?"
    retrieved = simple_similarity_search(query, chunks, top_k=2)
    context_str = format_context_for_prompt(retrieved)
    prompt = build_rag_prompt(query, retrieved)
    
    print(f"✓ Built prompt for Poe")
    print(f"  Prompt length: {len(prompt)} chars")
    print(f"  Sample (first 300 chars):")
    print(f"    {prompt[:300]}...\n")
    
    assert len(prompt) > 100, "Prompt too short"
    assert "User Question:" in prompt, "Prompt missing user question marker"
    print(f"✓ Prompt structure verified\n")


def main():
    """Run all tests."""
    print("\n🧪 Running RAG Pipeline Tests\n")
    
    try:
        chunks = test_pdf_loading()
        test_retrieval(chunks)
        test_prompt_building(chunks)
        
        print("=" * 60)
        print("✅ ALL TESTS PASSED")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Set your POE_API_KEY: $env:POE_API_KEY = 'your-key'")
        print("2. Run: uv run main.py")
        print()
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
