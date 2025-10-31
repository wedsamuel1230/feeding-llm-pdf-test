"""Configuration for RAG pipeline."""
import os

# API Configuration
POE_API_KEY = os.getenv("POE_API_KEY")
POE_BASE_URL = "https://api.poe.com/v1"
POE_MODEL = "gpt-4o-mini"  # Use gpt-3.5-turbo for faster/cheaper testing, gpt-4o for better quality

# Embedding Configuration
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # Fast, local Sentence Transformer
EMBEDDING_DIM = 384
EMBEDDING_CACHE_DIR = ".embeddings_cache"

# Reranking Configuration
RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L-12-v2"  # Fast cross-encoder for reranking
RERANKER_TOP_K = 5  # Rerank top-5 before returning top-3

# RAG Configuration
CHUNK_SIZE = 500  # Words per chunk
CHUNK_OVERLAP = 50  # Overlap for context
RETRIEVAL_TOP_K = 5  # Retrieve more for reranking
FINAL_TOP_K = 3  # Final citations returned to LLM

# Streaming
STREAM_ENABLED = True

# Create cache directory if it doesn't exist
os.makedirs(EMBEDDING_CACHE_DIR, exist_ok=True)
