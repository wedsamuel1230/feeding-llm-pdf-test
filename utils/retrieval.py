"""Retrieval and context injection utilities with semantic search."""
import numpy as np
from typing import List, Dict, Tuple
from .embeddings import EmbeddingCache
from .reranker import Reranker
import config


def semantic_search(
    query: str,
    chunks: List[dict],
    embeddings_dict: Dict[str, np.ndarray],
    query_embedding: np.ndarray,
    top_k: int = config.RETRIEVAL_TOP_K
) -> List[Dict]:
    """
    Semantic search using embeddings with caching.
    
    Args:
        query: User query text
        chunks: List of PDF chunks
        embeddings_dict: Dictionary mapping chunk keys to embeddings
        query_embedding: Query embedding vector
        top_k: Number of results to return
        
    Returns:
        List of chunk dicts with added 'score' field, sorted by relevance
    """
    if not chunks:
        return []
    
    # Compute similarities
    similarities = []
    for chunk in chunks:
        chunk_key = f"{chunk['pdf_id']}_{chunk['chunk_id']}"
        
        if chunk_key in embeddings_dict:
            chunk_emb = embeddings_dict[chunk_key]
            # Cosine similarity
            similarity = np.dot(query_embedding, chunk_emb) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(chunk_emb) + 1e-8
            )
            chunk_copy = chunk.copy()
            chunk_copy['score'] = float(similarity)
            similarities.append(chunk_copy)
    
    # Sort and return top_k
    similarities.sort(key=lambda x: x['score'], reverse=True)
    return similarities[:top_k]


def retrieve_with_reranking(
    query: str,
    chunks: List[dict],
    embedding_cache: EmbeddingCache,
    reranker: Reranker,
    top_k: int = config.FINAL_TOP_K
) -> List[Dict]:
    """
    Two-stage retrieval: semantic search + cross-encoder reranking.
    
    Args:
        query: User query
        chunks: All chunks
        embedding_cache: Embedding cache
        reranker: Cross-encoder reranker
        top_k: Final number of results
        
    Returns:
        Top-k reranked results with 'score' field
    """
    # Get embeddings and query embedding
    embeddings_dict = embedding_cache.get_embeddings(chunks)
    query_embedding = embedding_cache.embed_text(query)
    
    # Stage 1: Semantic search for top-N candidates
    candidates = semantic_search(
        query,
        chunks,
        embeddings_dict,
        query_embedding,
        top_k=config.RETRIEVAL_TOP_K
    )
    
    if not candidates:
        return []
    
    # Stage 2: Rerank with cross-encoder
    reranked = reranker.rerank(query, candidates, top_k=top_k)
    
    return reranked


def filter_by_pdf(chunks: List[dict], pdf_id: str) -> List[dict]:
    """Filter chunks by document ID."""
    return [c for c in chunks if c.get('pdf_id') == pdf_id]


def format_context_for_prompt(retrieved_chunks: List[Dict]) -> str:
    """
    Format retrieved chunks into system context with citations.
    
    Args:
        retrieved_chunks: List of chunk dicts with 'score' field from retrieval
        
    Returns:
        Formatted context string for LLM prompt
    """
    if not retrieved_chunks:
        return ""
    
    context_parts = ["## PDF Context Retrieved:"]
    
    for idx, chunk in enumerate(retrieved_chunks, start=1):
        page = chunk.get('page', '?')
        pdf_name = chunk.get('pdf_name', 'Unknown')
        chunk_id = chunk.get('chunk_id', idx)
        score = chunk.get('score', 0.0)
        text_preview = chunk['text'][:200] + "..." if len(chunk['text']) > 200 else chunk['text']
        
        context_parts.append(f"\n[{idx}] {pdf_name}, Page {page}")
        context_parts.append(f"{text_preview}")
    
    return "\n".join(context_parts)


def build_rag_prompt(user_query: str, retrieved_chunks: List[Dict]) -> str:
    """Build final prompt with context for LLM."""
    context = format_context_for_prompt(retrieved_chunks)
    
    prompt = f"""You are an AI assistant that answers questions based on provided PDF content.
Use the retrieved PDF context below to answer the user's question.
Always cite the source (PDF name, page number) when referencing the documents.
If the answer is not in the provided context, say so clearly.

{context}

---

User Question: {user_query}

Please provide a detailed answer with specific citations."""
    return prompt


# Backward compatibility: Keep old function name
def simple_similarity_search(query: str, chunks: List[dict], top_k: int = 3) -> List[dict]:
    """Legacy function for backward compatibility - keyword-based search."""
    query_words = set(query.lower().split())
    scored_chunks = []
    
    for chunk in chunks:
        chunk_words = set(chunk['text'].lower().split())
        if query_words and chunk_words:
            intersection = query_words & chunk_words
            union = query_words | chunk_words
            score = len(intersection) / len(union)
        else:
            score = 0.0
        chunk_copy = chunk.copy()
        chunk_copy['score'] = score
        scored_chunks.append(chunk_copy)
    
    scored_chunks.sort(key=lambda x: x['score'], reverse=True)
    return scored_chunks[:top_k]
