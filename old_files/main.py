#!/usr/bin/env python3
"""Advanced RAG pipeline with semantic search, reranking, streaming, and multi-PDF support."""

import os
import sys
from typing import List
from openai import OpenAI

import config
from utils.pdf_processor import chunk_pdf_text, chunk_multiple_pdfs
from utils.embeddings import EmbeddingCache
from utils.reranker import Reranker
from utils.retrieval import (
    retrieve_with_reranking,
    filter_by_pdf,
    build_rag_prompt
)


def initialize_clients():
    """Initialize API and ML clients."""
    # Poe API client
    poe_client = OpenAI(
        api_key=config.POE_API_KEY,
        base_url=config.POE_BASE_URL,
    )
    
    # ML models for retrieval
    embedding_cache = EmbeddingCache()
    reranker = Reranker()
    
    return poe_client, embedding_cache, reranker


def load_pdfs(pdf_paths: List[str] = None) -> List[dict]:
    """Load and chunk PDFs."""
    if pdf_paths is None:
        pdf_paths = ["test-pdf.pdf"]
    
    print(f"📄 Loading {len(pdf_paths)} PDF(s)...")
    chunks = chunk_multiple_pdfs(pdf_paths)
    print(f"✓ Extracted {len(chunks)} chunks total\n")
    
    return chunks


def retrieve_documents(
    query: str,
    chunks: List[dict],
    embedding_cache: EmbeddingCache,
    reranker: Reranker,
    pdf_filter: str = None
) -> tuple:
    """Retrieve and rerank documents."""
    print("🔍 Retrieving relevant documents...")
    
    # Filter by PDF if specified
    if pdf_filter:
        chunks = filter_by_pdf(chunks, pdf_filter)
        print(f"   Filtered to {len(chunks)} chunks from PDF: {pdf_filter}")
    
    # Two-stage retrieval with semantic search + reranking
    retrieved = retrieve_with_reranking(
        query,
        chunks,
        embedding_cache,
        reranker,
        top_k=config.FINAL_TOP_K
    )
    
    print(f"✓ Retrieved {len(retrieved)} relevant chunks\n")
    return retrieved


def query_poe_streaming(
    poe_client: OpenAI,
    prompt: str,
    model: str = config.POE_MODEL
) -> None:
    """Query Poe API with streaming response."""
    print("💬 Querying Poe API (streaming)...\n")
    print("=" * 70)
    print("RESPONSE:")
    print("=" * 70)
    
    try:
        with poe_client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful AI assistant that answers questions about PDF documents with accurate citations."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=2048,
            stream=config.STREAM_ENABLED,
        ) as response:
            # Stream and collect response
            full_response = []
            for chunk in response:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    print(content, end="", flush=True)
                    full_response.append(content)
            
            print("\n")  # New line after streaming
            return "".join(full_response)
    
    except Exception as e:
        print(f"❌ Error: {e}")
        if "api_key" in str(e).lower():
            print("\n⚠️  Poe API key not set. Set it with:")
            print("   $env:POE_API_KEY = 'your-api-key'")
        raise


def main(pdf_paths: List[str] = None, query: str = None):
    """Main RAG pipeline."""
    print("\n" + "=" * 70)
    print("🚀 Advanced RAG Pipeline with Embeddings, Reranking & Streaming")
    print("=" * 70 + "\n")
    
    # Initialize
    poe_client, embedding_cache, reranker = initialize_clients()
    
    # Load PDFs
    chunks = load_pdfs(pdf_paths)
    
    # User query
    if query is None:
        query = "根據 PDF 說明重點並附出處。"  # "Explain the main points from PDF with sources."
    
    print(f"❓ Query: {query}\n")
    
    # Retrieve with semantic search + reranking
    retrieved = retrieve_documents(query, chunks, embedding_cache, reranker)
    
    if not retrieved:
        print("⚠️  No relevant documents found.")
        return
    
    # Build prompt with retrieved chunks
    prompt = build_rag_prompt(query, retrieved)
    
    # Query Poe with streaming
    response = query_poe_streaming(poe_client, prompt)
    
    # Display citations
    print("=" * 70)
    print("📚 SOURCE CITATIONS:")
    print("=" * 70)
    for idx, chunk in enumerate(retrieved, start=1):
        pdf_name = chunk.get('pdf_name', 'Unknown')
        page = chunk.get('page', '?')
        print(f"  [{idx}] {pdf_name}, Page {page}")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    try:
        # Support command-line arguments
        pdf_paths = None
        query = None
        
        if len(sys.argv) > 1:
            # Custom PDF paths or query
            if sys.argv[1].startswith("--pdf="):
                pdf_paths = sys.argv[1].replace("--pdf=", "").split(",")
            if len(sys.argv) > 2 and sys.argv[2].startswith("--query="):
                query = sys.argv[2].replace("--query=", "")
        
        main(pdf_paths, query)
    
    except KeyboardInterrupt:
        print("\n\n⏹️  Interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

