# Contributing to Advanced RAG Pipeline

Thank you for your interest in contributing! This document provides guidelines and best practices for contributing to the project.

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Git
- Basic understanding of RAG, embeddings, and LLMs

### Setup Development Environment

```powershell
# Clone your fork
git clone https://github.com/yourusername/rag-pipeline.git
cd rag-pipeline

# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies with dev extras
pip install -e ".[dev]"
```

## 📋 Development Workflow

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
# Or for bug fixes:
git checkout -b fix/issue-description
```

### 2. Make Your Changes

- Follow the coding standards below
- Write tests for new features
- Update documentation

### 3. Run Tests

```powershell
# Run all tests
pytest tests/ -v

# With coverage
pytest --cov=src --cov-report=html tests/

# Type checking
mypy src/

# Linting
flake8 src/ tests/
black --check src/ tests/
```

### 4. Commit Your Changes

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```bash
git commit -m "feat: add multi-language support for queries"
git commit -m "fix: resolve caching issue with special characters"
git commit -m "docs: update installation instructions"
```

**Commit Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### 5. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Then open a Pull Request on GitHub with:
- Clear title and description
- Reference to related issues
- Screenshots/demos if applicable

## 🎨 Coding Standards

### Python Style Guide

- Follow [PEP 8](https://pep8.org/)
- Use type hints for function signatures
- Maximum line length: 100 characters
- Use `black` for formatting
- Use `mypy` for type checking

### Example Code Style

```python
from typing import List, Dict, Optional


def process_documents(
    pdf_paths: List[str],
    chunk_size: int = 500,
    overlap: int = 50
) -> List[Dict[str, any]]:
    """
    Process PDF documents into chunks.
    
    Args:
        pdf_paths: List of PDF file paths
        chunk_size: Words per chunk (default: 500)
        overlap: Overlap between chunks (default: 50)
        
    Returns:
        List of chunk dictionaries with metadata
        
    Raises:
        FileNotFoundError: If PDF file doesn't exist
        ValueError: If chunk_size <= 0
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    
    # Implementation here
    pass
```

### GUI Code Standards

- Keep GUI code in `src/gui/`
- Separate business logic from presentation
- Use signals/slots for async operations
- Add docstrings to all public methods

## 🧪 Testing Guidelines

### Test Structure

```
tests/
├── test_core/
│   ├── test_embeddings.py
│   ├── test_reranker.py
│   └── test_retrieval.py
├── test_gui/
│   └── test_widgets.py
└── test_integration.py
```

### Writing Tests

```python
import pytest
from src.core import EmbeddingCache


def test_embedding_cache_initialization():
    """Test that EmbeddingCache initializes correctly."""
    cache = EmbeddingCache()
    assert cache.model is not None
    assert cache.cache_dir.exists()


def test_embed_text():
    """Test single text embedding."""
    cache = EmbeddingCache()
    embedding = cache.embed_text("test query")
    
    assert embedding.shape == (384,)
    assert embedding.dtype == np.float32
```

### Test Coverage Requirements

- Minimum 80% code coverage for new features
- 100% coverage for critical path (retrieval, embeddings)
- Include edge cases and error conditions

## 📚 Documentation

### Docstring Format

Use Google-style docstrings:

```python
def retrieve_documents(
    query: str,
    chunks: List[dict],
    top_k: int = 3
) -> List[dict]:
    """Retrieve relevant documents using semantic search.
    
    This function performs two-stage retrieval:
    1. Semantic search with embeddings (cosine similarity)
    2. Cross-encoder reranking for precision
    
    Args:
        query: User's question or search query
        chunks: List of document chunks to search
        top_k: Number of results to return (default: 3)
        
    Returns:
        List of top-k relevant chunks with 'score' field
        
    Example:
        >>> results = retrieve_documents(
        ...     "What is RAG?",
        ...     chunks,
        ...     top_k=5
        ... )
        >>> len(results)
        5
    """
```

### Update Documentation

When adding features, update:
- `README.md` (if user-facing)
- `docs/architecture.md` (if architectural change)
- Inline code comments for complex logic

## 🐛 Reporting Bugs

### Before Submitting

1. Check [existing issues](https://github.com/yourusername/rag-pipeline/issues)
2. Try the latest version
3. Gather debug information

### Bug Report Template

```markdown
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce:
1. Go to '...'
2. Click on '...'
3. See error

**Expected behavior**
What you expected to happen.

**Screenshots**
If applicable, add screenshots.

**Environment:**
 - OS: [e.g., Windows 11]
 - Python: [e.g., 3.11.5]
 - Version: [e.g., 1.0.0]

**Additional context**
Any other context about the problem.
```

## 💡 Suggesting Features

### Feature Request Template

```markdown
**Feature Description**
Clear description of the feature.

**Use Case**
Why is this feature needed? What problem does it solve?

**Proposed Solution**
How you imagine this feature working.

**Alternatives Considered**
Other approaches you've thought about.

**Additional Context**
Mockups, diagrams, or examples.
```

## 🏆 Recognition

Contributors will be acknowledged in:
- `CONTRIBUTORS.md`
- Release notes
- GitHub contributors page

## 📞 Getting Help

- **GitHub Discussions**: For questions and ideas
- **Discord**: [Join our community](https://discord.gg/yourserver)
- **Email**: maintainer@example.com

## 📜 Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/version/2/1/code_of_conduct/).

---

Thank you for contributing! 🎉
