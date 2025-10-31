"""Test suite for advanced RAG pipeline with embeddings, reranking, and caching."""
import sys
import os

def test_embeddings():
    """Test embedding generation and caching."""
    print("=" * 70)
    print("TEST 1: Embedding Generation & Caching")
    print("=" * 70)
    
    from utils.embeddings import EmbeddingCache
    from utils.pdf_processor import chunk_pdf_text
    
    # Load PDF and create chunks
    pdf_path = "test-pdf.pdf"
    print(f"Loading {pdf_path}...")
    chunks = chunk_pdf_text(pdf_path)
    print(f"✓ Created {len(chunks)} chunks")
    
    # Initialize embedding cache
    print("\nGenerating embeddings...")
    cache = EmbeddingCache()
    embeddings = cache.get_embeddings(chunks)
    print(f"✓ Generated {len(embeddings)} embeddings")
    
    # Verify shape
    for key, emb in list(embeddings.items())[:1]:
        print(f"✓ Embedding shape: {emb.shape} (expected: (384,))")
        assert emb.shape == (384,), f"Expected shape (384,), got {emb.shape}"
    
    print("✓ Embedding caching works!")
    print()


def test_semantic_search():
    """Test semantic search with embeddings."""
    print("=" * 70)
    print("TEST 2: Semantic Search with Embeddings")
    print("=" * 70)
    
    from utils.embeddings import EmbeddingCache
    from utils.pdf_processor import chunk_pdf_text
    from utils.retrieval import semantic_search
    import config
    
    # Setup
    chunks = chunk_pdf_text("test-pdf.pdf")
    cache = EmbeddingCache()
    embeddings = cache.get_embeddings(chunks)
    query_embedding = cache.embed_text("What is the course about?")
    
    # Test semantic search
    query = "What is the course about?"
    print(f"Query: '{query}'")
    results = semantic_search(query, chunks, embeddings, query_embedding, top_k=3)
    
    print(f"✓ Retrieved {len(results)} results")
    for i, chunk in enumerate(results, 1):
        score = chunk.get('score', 0.0)
        print(f"  [{i}] Page {chunk['page']}, Score: {score:.4f}")
    
    print("✓ Semantic search works!")
    print()


def test_reranking():
    """Test reranking with cross-encoder."""
    print("=" * 70)
    print("TEST 3: Reranking with Cross-Encoder")
    print("=" * 70)
    
    from utils.reranker import Reranker
    from utils.pdf_processor import chunk_pdf_text
    
    chunks = chunk_pdf_text("test-pdf.pdf")[:5]  # First 5 chunks
    reranker = Reranker()
    
    query = "Electronic signals and communication"
    print(f"Query: '{query}'")
    print(f"Reranking {len(chunks)} chunks...")
    
    reranked = reranker.rerank(query, chunks, top_k=3)
    print(f"✓ Reranked to top-3:")
    for i, chunk in enumerate(reranked, 1):
        score = chunk.get('score', 0.0)
        print(f"  [{i}] Page {chunk['page']}, Score: {score:.4f}")
    
    print("✓ Reranking works!")
    print()

def test_multi_pdf():
    """Test multi-PDF support."""
    print("=" * 70)
    print("TEST 4: Multi-PDF Support")
    print("=" * 70)
    
    from utils.pdf_processor import chunk_multiple_pdfs, get_pdf_id
    
    pdf_paths = ["test-pdf.pdf"]  # Add more PDFs as needed
    print(f"Loading {len(pdf_paths)} PDF(s)...")
    
    chunks = chunk_multiple_pdfs(pdf_paths)
    print(f"✓ Extracted {len(chunks)} total chunks")
    
    # Verify document IDs
    pdf_ids = set(c['pdf_id'] for c in chunks)
    print(f"✓ Found {len(pdf_ids)} unique PDF(s)")
    
    for chunk in chunks[:2]:
        print(f"  - {chunk['pdf_name']} (ID: {chunk['pdf_id']}), Page {chunk['page']}")
    
    print("✓ Multi-PDF support works!")
    print()


def test_full_pipeline():
    """Test complete RAG pipeline (without API)."""
    print("=" * 70)
    print("TEST 5: Full RAG Pipeline (without API)")
    print("=" * 70)
    
    from utils.embeddings import EmbeddingCache
    from utils.reranker import Reranker
    from utils.pdf_processor import chunk_pdf_text
    from utils.retrieval import retrieve_with_reranking, format_context_for_prompt, build_rag_prompt
    
    # Load and chunk
    chunks = chunk_pdf_text("test-pdf.pdf")
    print(f"Loaded {len(chunks)} chunks")
    
    # Initialize ML components
    cache = EmbeddingCache()
    reranker = Reranker()
    
    # Retrieve
    query = "What are the main topics?"
    print(f"Query: '{query}'")
    
    retrieved = retrieve_with_reranking(query, chunks, cache, reranker)
    print(f"✓ Retrieved {len(retrieved)} results")
    
    # Format context
    context_str = format_context_for_prompt(retrieved)
    print(f"✓ Formatted context ({len(context_str)} chars)")
    
    # Build prompt
    prompt = build_rag_prompt(query, retrieved)
    print(f"✓ Built prompt ({len(prompt)} chars)")
    
    print("\nPrompt preview:")
    print(prompt[:300] + "...\n")
    
    print("✓ Full pipeline works!")
    print()


def main():
    """Run all tests."""
    print("\n🧪 Running Advanced RAG Pipeline Tests\n")
    
    try:
        test_embeddings()
        test_semantic_search()
        test_reranking()
        test_multi_pdf()
        test_full_pipeline()
        
        print("=" * 70)
        print("✅ ALL TESTS PASSED!")
        print("=" * 70)
        print("\nNext steps:")
        print("1. Set your Poe API key: $env:POE_API_KEY = 'your-key'")
        print("2. Run: uv run main.py")
        print("3. For custom PDFs: uv run main.py --pdf=file1.pdf,file2.pdf")
        print()
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
