"""Reranking utilities for improving retrieval quality."""
import numpy as np
from typing import List, Dict
from sentence_transformers import CrossEncoder

from .. import config


class Reranker:
    """Cross-encoder based reranker for retrieval results."""
    
    def __init__(self):
        self.model = CrossEncoder(config.RERANKER_MODEL)
    
    def rerank(
        self,
        query: str,
        chunks: List[Dict],
        top_k: int = 3
    ) -> List[Dict]:
        """
        Rerank chunks by relevance to query using cross-encoder.
        
        Args:
            query: User query text
            chunks: List of chunks (already retrieved by embedding search)
            top_k: Number of top chunks to return
            
        Returns:
            List of chunk dicts with added/updated 'score' field, sorted by score
        """
        if not chunks:
            return []
        
        # Prepare pairs for cross-encoder: [query, chunk_text]
        pairs = [[query, chunk['text']] for chunk in chunks]
        
        # Get scores
        scores = self.model.predict(pairs)
        
        # Sort by score and add score to chunks
        ranked_chunks = []
        for chunk, score in zip(chunks, scores):
            chunk_copy = chunk.copy()
            chunk_copy['score'] = float(score)
            ranked_chunks.append(chunk_copy)
        
        ranked_chunks.sort(key=lambda x: x['score'], reverse=True)
        return ranked_chunks[:top_k]
