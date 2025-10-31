"""Configuration for RAG pipeline."""
import os

# API Configuration
POE_API_KEY = os.getenv("POE_API_KEY")
POE_BASE_URL = "https://api.poe.com/v1"
POE_MODEL = "gpt-4o-mini"  # Default model

# Available Poe Models (for GUI dropdown)
POE_AVAILABLE_MODELS = [
    "gpt-4o-mini",          # GPT-4o Mini (Fast, cost-effective)
    "gpt-4o",               # GPT-4o (Most capable)
    "gpt-3.5-turbo",        # GPT-3.5 Turbo (Legacy, fast)
    "claude-3.5-sonnet",    # Claude 3.5 Sonnet (Anthropic)
    "claude-3-opus",        # Claude 3 Opus (Most capable Claude)
    "claude-3-haiku",       # Claude 3 Haiku (Fast)
    "gemini-2.0-flash-exp", # Google Gemini 2.0 Flash
    "gemini-pro",           # Google Gemini Pro
    "llama-3.3-70b",        # Meta Llama 3.3 70B
    "llama-3.1-405b",       # Meta Llama 3.1 405B
    "mistral-large",        # Mistral Large
    "qwen-2.5-72b",         # Alibaba Qwen 2.5 72B
]

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
