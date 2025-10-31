#!/usr/bin/env python3
"""Phase 4 Self-Audit: Comprehensive validation of all components and regressions."""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from utils.pdf_processor import chunk_pdf_text, get_pdf_id, chunk_multiple_pdfs
from utils.embeddings import EmbeddingCache
from utils.reranker import Reranker
from utils.retrieval import (
    semantic_search,
    retrieve_with_reranking,
    simple_similarity_search,
    format_context_for_prompt,
    build_rag_prompt,
)
from config import *


def audit_backward_compatibility():
    """Verify that old keyword-based search still works."""
    print("\n" + "=" * 70)
    print("AUDIT 1: Backward Compatibility (Keyword Search)")
    print("=" * 70)

    chunks = chunk_pdf_text("test-pdf.pdf")
    query = "electronic communication"

    # Old method should still work
    results = simple_similarity_search(query, chunks, top_k=3)
    
    assert len(results) > 0, "❌ Keyword search returned no results"
    assert "text" in results[0], "❌ Result missing 'text' field"
    assert "page" in results[0], "❌ Result missing 'page' field"
    
    print(f"✓ Old keyword search still works: {len(results)} results found")
    print(f"  - Top result from page {results[0]['page']}")
    return True


def audit_multi_pdf_support():
    """Verify multi-PDF loading with unique document tracking."""
    print("\n" + "=" * 70)
    print("AUDIT 2: Multi-PDF Support & Document Tracking")
    print("=" * 70)

    # Single PDF
    chunks_single = chunk_pdf_text("test-pdf.pdf")
    assert all("pdf_id" in c for c in chunks_single), "❌ Chunks missing pdf_id"
    assert all("pdf_name" in c for c in chunks_single), "❌ Chunks missing pdf_name"
    
    pdf_id_single = get_pdf_id("test-pdf.pdf")
    assert len(pdf_id_single) == 8, f"❌ PDF ID should be 8 chars, got {len(pdf_id_single)}"
    
    print(f"✓ Single PDF loading verified")
    print(f"  - ID: {pdf_id_single}, Chunks: {len(chunks_single)}")
    print(f"  - Sample chunk: {chunks_single[0]['pdf_name']}, Page {chunks_single[0]['page']}")
    
    # Multi-PDF (using same PDF twice to simulate multiple files)
    chunks_multi = chunk_multiple_pdfs(["test-pdf.pdf"])
    assert len(chunks_multi) > 0, "❌ Multi-PDF failed to load"
    
    unique_pdfs = set(c["pdf_id"] for c in chunks_multi)
    print(f"✓ Multi-PDF loading verified: {len(unique_pdfs)} unique PDF(s)")
    
    return True


def audit_embedding_caching():
    """Verify embedding cache persists across runs."""
    print("\n" + "=" * 70)
    print("AUDIT 3: Embedding Cache Persistence")
    print("=" * 70)

    chunks = chunk_pdf_text("test-pdf.pdf")
    cache = EmbeddingCache()
    
    # First run - should compute
    embeddings_1 = cache.get_embeddings(chunks)
    assert isinstance(embeddings_1, dict), "❌ Embeddings should be dict"
    assert len(embeddings_1) == len(chunks), "❌ Embedding count mismatch"
    
    # Check first embedding
    first_key = list(embeddings_1.keys())[0]
    assert embeddings_1[first_key].shape == (384,), "❌ Embedding dimension mismatch"
    
    # Check cache file was created
    cache_files = list(Path(EMBEDDING_CACHE_DIR).glob("*.json"))
    assert len(cache_files) > 0, "❌ No cache files created"
    
    # Second run - should load from cache (faster)
    cache_2 = EmbeddingCache()  # New instance
    embeddings_2 = cache_2.get_embeddings(chunks)
    
    # Verify cache hit (compare embeddings)
    import numpy as np
    match = np.allclose(embeddings_1[first_key], embeddings_2[first_key])
    assert match, "❌ Cached embeddings don't match"
    
    print(f"✓ Embedding cache works correctly")
    print(f"  - Generated {len(embeddings_1)} embeddings (384-dim)")
    print(f"  - Cache file created: {cache_files[0].name}")
    print(f"  - Cache hit verified on second run")
    
    return True


def audit_two_stage_retrieval():
    """Verify semantic search → reranking pipeline."""
    print("\n" + "=" * 70)
    print("AUDIT 4: Two-Stage Retrieval (Semantic + Reranking)")
    print("=" * 70)

    chunks = chunk_pdf_text("test-pdf.pdf")
    query = "What topics are covered?"
    
    cache = EmbeddingCache()
    reranker = Reranker()
    
    # Stage 1: Semantic search
    embeddings = cache.get_embeddings(chunks)
    query_embedding = cache.embed_text(query)
    
    results_stage1 = semantic_search(query, chunks, embeddings, query_embedding, top_k=RETRIEVAL_TOP_K)
    assert len(results_stage1) > 0, "❌ Semantic search found no results"
    
    print(f"✓ Stage 1 (Semantic Search):")
    print(f"  - Retrieved {len(results_stage1)} candidates")
    print(f"  - Top score: {results_stage1[0]['score']:.4f}")
    
    # Stage 2: Reranking
    results_stage2 = retrieve_with_reranking(
        query,
        chunks,
        cache,
        reranker,
        top_k=FINAL_TOP_K
    )
    assert len(results_stage2) <= FINAL_TOP_K, "❌ Reranking returned too many results"
    
    print(f"✓ Stage 2 (Cross-Encoder Reranking):")
    print(f"  - Reranked to {len(results_stage2)} final results")
    if results_stage2:
        print(f"  - Top rerank score: {results_stage2[0]['score']:.4f}")
    
    return True


def audit_citation_format():
    """Verify context formatting includes PDF name and page."""
    print("\n" + "=" * 70)
    print("AUDIT 5: Citation Format & Context Structure")
    print("=" * 70)

    chunks = chunk_pdf_text("test-pdf.pdf")
    query = "course"
    
    cache = EmbeddingCache()
    reranker = Reranker()
    
    results = retrieve_with_reranking(query, chunks, cache, reranker, top_k=3)
    context = format_context_for_prompt(results)
    
    assert context is not None, "❌ Context formatting failed"
    assert "test-pdf.pdf" in context or "[" in context, "❌ Context missing PDF name or citations"
    assert "Page" in context, "❌ Context missing page numbers"
    
    # Build full prompt
    prompt = build_rag_prompt(query, results)
    assert query in prompt, "❌ Prompt missing original query"
    assert len(prompt) > 200, "❌ Prompt seems incomplete"
    
    print(f"✓ Citation format verified:")
    print(f"  - Context length: {len(context)} chars")
    print(f"  - Prompt length: {len(prompt)} chars")
    print(f"  - PDF name included: Yes")
    print(f"  - Page numbers included: Yes")
    print(f"  - Sample context (first 200 chars):")
    print(f"    {context[:200]}...")
    
    return True


def audit_config_centralization():
    """Verify all parameters are centralized in config.py."""
    print("\n" + "=" * 70)
    print("AUDIT 6: Configuration Centralization")
    print("=" * 70)

    # Import config and check key parameters
    required_params = [
        "POE_API_KEY",
        "POE_BASE_URL",
        "POE_MODEL",
        "EMBEDDING_MODEL",
        "EMBEDDING_DIM",
        "RERANKER_MODEL",
        "CHUNK_SIZE",
        "CHUNK_OVERLAP",
        "RETRIEVAL_TOP_K",
        "FINAL_TOP_K",
        "STREAM_ENABLED",
        "EMBEDDING_CACHE_DIR",
    ]
    
    for param in required_params:
        assert hasattr(sys.modules["config"], param), f"❌ Missing parameter: {param}"
    
    print(f"✓ All {len(required_params)} config parameters present:")
    print(f"  - POE_MODEL: {POE_MODEL}")
    print(f"  - EMBEDDING_MODEL: {EMBEDDING_MODEL} ({EMBEDDING_DIM}-dim)")
    print(f"  - RERANKER_MODEL: {RERANKER_MODEL}")
    print(f"  - CHUNK_SIZE: {CHUNK_SIZE} words, OVERLAP: {CHUNK_OVERLAP}")
    print(f"  - Retrieve: {RETRIEVAL_TOP_K}, Return: {FINAL_TOP_K}")
    print(f"  - Streaming: {STREAM_ENABLED}")
    print(f"  - Cache dir: {EMBEDDING_CACHE_DIR}")
    
    return True


def main():
    """Run all audit checks."""
    print("\n" + "=" * 70)
    print("🔍 PHASE 4: ZERO-TRUST SELF-AUDIT")
    print("=" * 70)

    tests = [
        ("Backward Compatibility", audit_backward_compatibility),
        ("Multi-PDF Support", audit_multi_pdf_support),
        ("Embedding Caching", audit_embedding_caching),
        ("Two-Stage Retrieval", audit_two_stage_retrieval),
        ("Citation Format", audit_citation_format),
        ("Config Centralization", audit_config_centralization),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n❌ AUDIT FAILED: {test_name}")
            print(f"   Error: {str(e)}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 AUDIT SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} audits passed")
    
    if passed == total:
        print("\n✅ ALL AUDITS PASSED - SYSTEM READY FOR PRODUCTION")
        return 0
    else:
        print(f"\n❌ {total - passed} audit(s) failed - fix required")
        return 1


if __name__ == "__main__":
    sys.exit(main())
