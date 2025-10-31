"""Example usage of the RAG pipeline."""

from src.core import (
    chunk_pdf_text,
    EmbeddingCache,
    Reranker,
    retrieve_with_reranking,
    build_rag_prompt
)
from openai import OpenAI
import os


def example_basic_usage():
    """Basic example: single PDF, single query."""
    print("=" * 70)
    print("Example 1: Basic Usage")
    print("=" * 70)
    
    # 1. Load and chunk PDF
    chunks = chunk_pdf_text("your-document.pdf", chunk_size=500, overlap=50)
    print(f"Loaded {len(chunks)} chunks")
    
    # 2. Initialize components
    cache = EmbeddingCache()
    reranker = Reranker()
    
    # 3. Query
    query = "What is the main topic of this document?"
    results = retrieve_with_reranking(query, chunks, cache, reranker, top_k=3)
    
    # 4. Display results
    for idx, chunk in enumerate(results, start=1):
        print(f"\n[{idx}] Score: {chunk['score']:.3f}")
        print(f"Page: {chunk['page']}")
        print(f"Text: {chunk['text'][:200]}...")


def example_multi_pdf():
    """Example: multiple PDFs."""
    from src.core import chunk_multiple_pdfs
    
    print("\n" + "=" * 70)
    print("Example 2: Multiple PDFs")
    print("=" * 70)
    
    pdf_files = ["doc1.pdf", "doc2.pdf", "doc3.pdf"]
    chunks = chunk_multiple_pdfs(pdf_files)
    
    print(f"Loaded {len(chunks)} chunks from {len(pdf_files)} PDFs")
    
    # Group by PDF
    pdf_groups = {}
    for chunk in chunks:
        pdf_name = chunk['pdf_name']
        if pdf_name not in pdf_groups:
            pdf_groups[pdf_name] = []
        pdf_groups[pdf_name].append(chunk)
    
    for pdf, chunks_list in pdf_groups.items():
        print(f"  {pdf}: {len(chunks_list)} chunks")


def example_with_llm():
    """Example: full RAG pipeline with LLM."""
    print("\n" + "=" * 70)
    print("Example 3: Full RAG Pipeline with LLM")
    print("=" * 70)
    
    # Setup
    chunks = chunk_pdf_text("your-document.pdf")
    cache = EmbeddingCache()
    reranker = Reranker()
    
    client = OpenAI(
        api_key=os.getenv("POE_API_KEY"),
        base_url="https://api.poe.com/v1"
    )
    
    # Query
    query = "Summarize the key findings"
    results = retrieve_with_reranking(query, chunks, cache, reranker)
    
    # Build prompt
    prompt = build_rag_prompt(query, results)
    
    # Call LLM
    print("\nQuerying LLM...")
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        stream=True
    )
    
    print("Response:")
    for chunk in response:
        if chunk.choices[0].delta.content:
            print(chunk.choices[0].delta.content, end="", flush=True)
    print("\n")


def example_custom_config():
    """Example: custom configuration."""
    from src import config
    
    print("\n" + "=" * 70)
    print("Example 4: Custom Configuration")
    print("=" * 70)
    
    # Temporarily override config
    original_top_k = config.FINAL_TOP_K
    config.FINAL_TOP_K = 5  # Return 5 results instead of 3
    
    chunks = chunk_pdf_text("your-document.pdf")
    cache = EmbeddingCache()
    reranker = Reranker()
    
    results = retrieve_with_reranking(
        "What are the main conclusions?",
        chunks,
        cache,
        reranker,
        top_k=5  # Can also pass directly
    )
    
    print(f"Retrieved {len(results)} results (configured for top-{config.FINAL_TOP_K})")
    
    # Restore
    config.FINAL_TOP_K = original_top_k


if __name__ == "__main__":
    # Run examples
    # Note: Replace "your-document.pdf" with actual PDF path
    
    # Uncomment to run:
    # example_basic_usage()
    # example_multi_pdf()
    # example_with_llm()
    # example_custom_config()
    
    print("\nTo run examples, uncomment the function calls above.")
    print("Make sure to replace 'your-document.pdf' with an actual PDF file.")
