"""PDF extraction and chunking utilities with multi-PDF support."""
import pdfplumber
import hashlib
from typing import List, Dict
from pathlib import Path


def get_pdf_id(pdf_path: str) -> str:
    """Generate unique ID for PDF (hash of filename and size)."""
    stat = Path(pdf_path).stat()
    hash_input = f"{Path(pdf_path).name}_{stat.st_size}"
    return hashlib.md5(hash_input.encode()).hexdigest()[:8]


def chunk_pdf_text(pdf_path: str, chunk_size: int = 500, overlap: int = 50) -> List[dict]:
    """
    Chunk PDF text with page awareness and overlap.
    
    Args:
        pdf_path: Path to PDF file
        chunk_size: Approximate words per chunk
        overlap: Number of words to overlap between chunks
        
    Returns:
        List of chunks with metadata: {
            'text': str,
            'page': int,
            'chunk_id': int,
            'pdf_id': str,
            'pdf_name': str
        }
    """
    chunks = []
    chunk_id = 0
    pdf_id = get_pdf_id(pdf_path)
    pdf_name = Path(pdf_path).name
    
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            text = page.extract_text()
            if not text.strip():
                continue
            
            words = text.split()
            for i in range(0, len(words), chunk_size - overlap):
                chunk_words = words[i:i + chunk_size]
                if chunk_words:
                    chunk_text = ' '.join(chunk_words)
                    chunks.append({
                        'text': chunk_text,
                        'page': page_num,
                        'chunk_id': chunk_id,
                        'pdf_id': pdf_id,
                        'pdf_name': pdf_name,
                        'start_word_idx': i,
                        'end_word_idx': i + len(chunk_words)
                    })
                    chunk_id += 1
    
    return chunks


def chunk_multiple_pdfs(pdf_paths: List[str], chunk_size: int = 500, overlap: int = 50) -> List[dict]:
    """
    Chunk multiple PDFs into a unified corpus.
    
    Args:
        pdf_paths: List of PDF file paths
        chunk_size: Words per chunk
        overlap: Overlap between chunks
        
    Returns:
        Combined list of chunks with pdf_id and pdf_name
    """
    all_chunks = []
    for pdf_path in pdf_paths:
        chunks = chunk_pdf_text(pdf_path, chunk_size, overlap)
        all_chunks.extend(chunks)
    return all_chunks


def get_pdf_summary(pdf_path: str) -> str:
    """Get basic PDF info."""
    with pdfplumber.open(pdf_path) as pdf:
        num_pages = len(pdf.pages)
    pdf_id = get_pdf_id(pdf_path)
    return f"PDF '{Path(pdf_path).name}' with {num_pages} pages (ID: {pdf_id})"
