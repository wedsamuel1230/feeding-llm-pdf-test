"""Embedding generation and caching utilities."""
import json
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple
from sentence_transformers import SentenceTransformer
import config


class EmbeddingCache:
    """Manages embedding caching to avoid recomputation."""
    
    def __init__(self):
        self.cache_dir = Path(config.EMBEDDING_CACHE_DIR)
        self.cache_dir.mkdir(exist_ok=True)
        self.model = SentenceTransformer(config.EMBEDDING_MODEL)
        self.memory_cache: Dict[str, np.ndarray] = {}
    
    def _get_cache_path(self, pdf_id: str) -> Path:
        """Get cache file path for a PDF."""
        return self.cache_dir / f"{pdf_id}_embeddings.json"
    
    def _chunk_to_key(self, chunk: dict) -> str:
        """Create unique key for chunk (for in-memory caching)."""
        return f"{chunk['pdf_id']}_{chunk['chunk_id']}"
    
    def load_cached_embeddings(self, pdf_id: str) -> Dict[str, np.ndarray]:
        """Load embeddings from disk cache for a PDF."""
        cache_path = self._get_cache_path(pdf_id)
        if cache_path.exists():
            try:
                with open(cache_path, 'r') as f:
                    data = json.load(f)
                # Convert lists back to numpy arrays
                return {k: np.array(v) for k, v in data.items()}
            except Exception as e:
                print(f"⚠️  Failed to load embeddings cache: {e}")
                return {}
        return {}
    
    def save_embeddings(self, pdf_id: str, embeddings: Dict[str, np.ndarray]):
        """Save embeddings to disk cache."""
        cache_path = self._get_cache_path(pdf_id)
        try:
            # Convert numpy arrays to lists for JSON serialization
            data = {k: v.tolist() for k, v in embeddings.items()}
            with open(cache_path, 'w') as f:
                json.dump(data, f)
            print(f"✓ Cached {len(embeddings)} embeddings for PDF {pdf_id}")
        except Exception as e:
            print(f"⚠️  Failed to save embeddings cache: {e}")
    
    def get_embeddings(self, chunks: List[dict]) -> Dict[str, np.ndarray]:
        """
        Get embeddings for chunks, using cache when available.
        
        Returns:
            embeddings_dict: Dictionary mapping chunk keys to embedding vectors
        """
        embeddings = {}
        chunks_to_embed = []
        
        # Group chunks by PDF
        chunks_by_pdf = {}
        for chunk in chunks:
            pdf_id = chunk['pdf_id']
            if pdf_id not in chunks_by_pdf:
                chunks_by_pdf[pdf_id] = []
            chunks_by_pdf[pdf_id].append(chunk)
        
        # Try to load from cache, identify missing
        for pdf_id, pdf_chunks in chunks_by_pdf.items():
            cached = self.load_cached_embeddings(pdf_id)
            for chunk in pdf_chunks:
                key = self._chunk_to_key(chunk)
                if key in cached:
                    embeddings[key] = cached[key]
                else:
                    chunks_to_embed.append(chunk)
        
        # Embed missing chunks
        if chunks_to_embed:
            print(f"🔄 Computing embeddings for {len(chunks_to_embed)} chunks...")
            texts = [c['text'] for c in chunks_to_embed]
            batch_embeddings = self.model.encode(texts, show_progress_bar=False)
            
            # Store in memory and organize by PDF for caching
            embeddings_by_pdf = {}
            for chunk, emb in zip(chunks_to_embed, batch_embeddings):
                key = self._chunk_to_key(chunk)
                embeddings[key] = emb
                
                pdf_id = chunk['pdf_id']
                if pdf_id not in embeddings_by_pdf:
                    embeddings_by_pdf[pdf_id] = {}
                embeddings_by_pdf[pdf_id][key] = emb
            
            # Save to disk cache by PDF
            for pdf_id, pdf_embeddings in embeddings_by_pdf.items():
                self.save_embeddings(pdf_id, pdf_embeddings)
        
        return embeddings
    
    def embed_text(self, text: str) -> np.ndarray:
        """Embed a single text (e.g., query)."""
        return self.model.encode(text)
