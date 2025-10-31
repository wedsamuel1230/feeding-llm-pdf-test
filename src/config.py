"""Configuration for RAG pipeline."""
import os

# API Configuration
POE_API_KEY = os.getenv("POE_API_KEY")
POE_BASE_URL = "https://api.poe.com/v1"
POE_MODEL = "Assistant"  # Default model (Poe's general-purpose router)

# Available Poe Models (for GUI dropdown) - Updated 2025-10-31
POE_AVAILABLE_MODELS = [
    # Poe
    "Assistant",                    # General-purpose router
    # OpenAI
    "GPT-5-Chat",                   # Latest non-reasoning GPT-5
    "GPT-5",                        # Flagship with improved coding
    "GPT-5-Pro",                    # Enhanced flagship
    "GPT-5-Codex",                  # Software engineering specialized
    "GPT-4o",                       # Natural, engaging writing
    "GPT-5-mini",                   # Fast, affordable
    "GPT-5-nano",                   # Extremely fast & cheap
    "o3-pro",                       # Well-rounded, powerful
    # Anthropic
    "Claude-Sonnet-4.5",            # Major capability leap
    "Claude-Haiku-4.5",             # Fast & efficient
    # Google
    "Gemini-2.5-Pro",               # Advanced frontier performance
    "Gemini-2.5-Flash",             # Built on 2.0 Flash
    # XAI
    "Grok-4",                       # xAI's most intelligent
    "Grok-4-Fast-Reasoning",        # Logic & complex tasks
    "Grok-4-Fast-Non-Reasoning",    # Content generation
    "Grok-Code-Fast-1",             # High-performance coding
    # Others
    "Qwen-3-Next-80B-Think",        # Next-gen with thinking mode
    "Qwen3-Next-80B",               # Next-gen foundation
    "DeepSeek-V3.2-Exp",            # Experimental model
    "DeepSeek-R1",                  # Open-source reasoning
]

# LLM Generation Configuration
MAX_TOKENS = 2048  # Default max tokens for LLM response (range: 512-8192)

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
