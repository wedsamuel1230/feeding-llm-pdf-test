"""Tkinter-based main window for RAG pipeline GUI."""

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import threading
import os
from pathlib import Path
from typing import List, Optional

from openai import OpenAI

from .. import config
from ..core import (
    chunk_multiple_pdfs,
    EmbeddingCache,
    Reranker,
    retrieve_with_reranking,
    build_rag_prompt
)


class RAGMainWindow:
    """Main application window for RAG pipeline."""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Advanced RAG Pipeline")
        self.root.geometry("900x700")
        
        self.pdf_paths: List[str] = []
        self.chunks: List[dict] = []
        self.poe_client: Optional[OpenAI] = None
        self.embedding_cache: Optional[EmbeddingCache] = None
        self.reranker: Optional[Reranker] = None
        self.is_processing = False
        self.token_var = tk.StringVar(value=str(config.MAX_TOKENS))
        
        self._initialize_components()
        self._build_ui()
        
    def _initialize_components(self):
        """Initialize Poe client and ML models."""
        try:
            api_key = os.getenv("POE_API_KEY")
            if not api_key:
                messagebox.showwarning(
                    "API Key Missing",
                    "POE_API_KEY environment variable not set.\n\n"
                    "Set it with:\n"
                    "  $env:POE_API_KEY = 'your-api-key'\n\n"
                    "You can still load PDFs, but queries will fail."
                )
            else:
                self.poe_client = OpenAI(
                    api_key=api_key,
                    base_url=config.POE_BASE_URL
                )
            
            self.embedding_cache = EmbeddingCache()
            self.reranker = Reranker()
            
        except Exception as e:
            messagebox.showerror("Initialization Error", f"Failed to initialize components:\n{e}")
    
    def _build_ui(self):
        """Build the main user interface."""
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        pdf_frame = ttk.LabelFrame(main_frame, text="📄 PDF Documents", padding="10")
        pdf_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        pdf_frame.columnconfigure(0, weight=1)
        
        self.pdf_listbox = tk.Listbox(pdf_frame, height=3, selectmode=tk.EXTENDED)
        self.pdf_listbox.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))
        
        btn_frame = ttk.Frame(pdf_frame)
        btn_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        self.btn_add_pdf = ttk.Button(btn_frame, text="Add PDF(s)", command=self._add_pdfs)
        self.btn_add_pdf.pack(side=tk.LEFT, padx=(0, 5))
        
        self.btn_clear_pdfs = ttk.Button(btn_frame, text="Clear All", command=self._clear_pdfs)
        self.btn_clear_pdfs.pack(side=tk.LEFT)
        
        self.pdf_status_label = ttk.Label(pdf_frame, text="No PDFs loaded", foreground="gray")
        self.pdf_status_label.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))
        
        model_frame = ttk.LabelFrame(main_frame, text="🤖 Model Selection", padding="10")
        model_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        model_frame.columnconfigure(1, weight=1)
        
        ttk.Label(model_frame, text="Model:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        self.model_var = tk.StringVar(value=config.POE_MODEL)
        self.model_combo = ttk.Combobox(
            model_frame,
            textvariable=self.model_var,
            values=config.POE_AVAILABLE_MODELS,
            state="readonly",
            width=40
        )
        self.model_combo.grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        # Token limit configuration
        ttk.Label(model_frame, text="Max Tokens:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        
        token_control_frame = ttk.Frame(model_frame)
        token_control_frame.grid(row=1, column=1, sticky=tk.W, pady=(10, 0))
        
        self.token_spinbox = ttk.Spinbox(
            token_control_frame,
            from_=512,
            to=8192,
            increment=256,
            textvariable=self.token_var,
            width=10
        )
        self.token_spinbox.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Label(token_control_frame, text="(512-8192, default: 2048)", foreground="gray").pack(side=tk.LEFT)
        
        query_frame = ttk.LabelFrame(main_frame, text="❓ Query", padding="10")
        query_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        query_frame.columnconfigure(0, weight=1)
        
        self.query_entry = ttk.Entry(query_frame, font=("Segoe UI", 10))
        self.query_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        self.query_entry.bind('<Return>', lambda e: self._submit_query())
        
        self.btn_submit = ttk.Button(query_frame, text="Submit", command=self._submit_query, width=15)
        self.btn_submit.grid(row=0, column=1)
        
        response_frame = ttk.LabelFrame(main_frame, text="💬 Response", padding="10")
        response_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        response_frame.columnconfigure(0, weight=1)
        response_frame.rowconfigure(0, weight=1)
        
        self.response_text = scrolledtext.ScrolledText(
            response_frame,
            wrap=tk.WORD,
            font=("Segoe UI", 10),
            state=tk.DISABLED
        )
        self.response_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.response_text.tag_configure("citation", foreground="#0066cc", font=("Segoe UI", 9, "italic"))
        self.response_text.tag_configure("error", foreground="#cc0000")
        
        self.status_label = ttk.Label(main_frame, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.grid(row=4, column=0, sticky=(tk.W, tk.E))
        
    def _add_pdfs(self):
        """Open file dialog to add PDF files."""
        filepaths = filedialog.askopenfilenames(
            title="Select PDF Files",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if filepaths:
            for filepath in filepaths:
                if filepath not in self.pdf_paths:
                    self.pdf_paths.append(filepath)
                    self.pdf_listbox.insert(tk.END, Path(filepath).name)
            
            self._load_pdfs()
    
    def _clear_pdfs(self):
        """Clear all loaded PDFs."""
        self.pdf_paths.clear()
        self.chunks.clear()
        self.pdf_listbox.delete(0, tk.END)
        self.pdf_status_label.config(text="No PDFs loaded", foreground="gray")
        self._update_status("PDFs cleared")
    
    def _load_pdfs(self):
        """Load and chunk PDFs in background thread."""
        if not self.pdf_paths:
            return
        
        self._update_status("Loading PDFs...")
        self.btn_add_pdf.config(state=tk.DISABLED)
        
        def load_task():
            try:
                self.chunks = chunk_multiple_pdfs(self.pdf_paths)
                self.root.after(0, self._on_pdfs_loaded)
            except Exception as e:
                self.root.after(0, lambda: self._on_load_error(str(e)))
        
        threading.Thread(target=load_task, daemon=True).start()
    
    def _on_pdfs_loaded(self):
        """Callback when PDFs are loaded successfully."""
        num_chunks = len(self.chunks)
        num_pdfs = len(self.pdf_paths)
        self.pdf_status_label.config(
            text=f"✓ Loaded {num_pdfs} PDF(s), {num_chunks} chunks extracted",
            foreground="green"
        )
        self._update_status(f"Ready - {num_pdfs} PDF(s) loaded")
        self.btn_add_pdf.config(state=tk.NORMAL)
    
    def _on_load_error(self, error_msg: str):
        """Callback when PDF loading fails."""
        self.pdf_status_label.config(text=f"❌ Error loading PDFs", foreground="red")
        self._update_status("Error")
        self.btn_add_pdf.config(state=tk.NORMAL)
        messagebox.showerror("PDF Load Error", f"Failed to load PDFs:\n{error_msg}")
    
    def _submit_query(self):
        """Submit query and get streaming response."""
        query = self.query_entry.get().strip()
        
        if not query:
            messagebox.showwarning("Empty Query", "Please enter a query.")
            return
        
        # Allow queries even without PDFs (general knowledge mode)
        # if not self.chunks:
        #     messagebox.showwarning("No PDFs", "Please add PDF files first.")
        #     return
        
        if not self.poe_client:
            messagebox.showerror("API Error", "Poe API client not initialized. Check POE_API_KEY.")
            return
        
        if self.is_processing:
            messagebox.showinfo("Processing", "A query is already being processed.")
            return
        
        self.is_processing = True
        self.btn_submit.config(state=tk.DISABLED)
        self._clear_response()
        
        def query_task():
            try:
                # Only retrieve documents if PDFs are loaded
                if self.chunks:
                    self.root.after(0, lambda: self._update_status("Retrieving documents..."))
                    retrieved = retrieve_with_reranking(
                        query,
                        self.chunks,
                        self.embedding_cache,
                        self.reranker,
                        top_k=config.FINAL_TOP_K
                    )
                else:
                    # No PDFs loaded - use general knowledge mode
                    self.root.after(0, lambda: self._update_status("Querying with general knowledge..."))
                    retrieved = []
                
                # Build prompt - works with or without retrieved chunks
                prompt = build_rag_prompt(query, retrieved)
                self.root.after(0, lambda: self._update_status("Querying Poe API..."))
                
                model = self.model_var.get()
                self._stream_response(prompt, model, retrieved)
                
            except Exception as e:
                self.root.after(0, lambda: self._append_response(f"❌ Error: {e}", tag="error"))
                self.root.after(0, self._on_query_complete)
        
        threading.Thread(target=query_task, daemon=True).start()
    
    def _stream_response(self, prompt: str, model: str, retrieved_chunks: List[dict]):
        """Stream response from Poe API."""
        try:
            with self.poe_client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a helpful AI assistant. When PDF documents are provided, use them to answer questions. Otherwise, use your general knowledge."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=int(self.token_var.get()),
                stream=config.STREAM_ENABLED,
            ) as response:
                for chunk in response:
                    if chunk.choices[0].delta.content:
                        content = chunk.choices[0].delta.content
                        self.root.after(0, lambda c=content: self._append_response(c))
                
                self.root.after(0, self._on_query_complete)
                
        except Exception as e:
            self.root.after(0, lambda: self._append_response(f"\n\n❌ API Error: {e}", tag="error"))
            self.root.after(0, self._on_query_complete)
    
    def _append_response(self, text: str, tag: str = None):
        """Append text to response area."""
        self.response_text.config(state=tk.NORMAL)
        if tag:
            self.response_text.insert(tk.END, text, tag)
        else:
            self.response_text.insert(tk.END, text)
        self.response_text.see(tk.END)
        self.response_text.config(state=tk.DISABLED)
    
    def _append_citations(self, retrieved_chunks: List[dict]):
        """Append citations to response."""
        self._append_response("\n\n" + "="*70 + "\n")
        self._append_response("📚 SOURCE CITATIONS:\n", tag="citation")
        self._append_response("="*70 + "\n")
        
        for idx, chunk in enumerate(retrieved_chunks, start=1):
            pdf_name = chunk.get('pdf_name', 'Unknown')
            page = chunk.get('page', '?')
            citation = f"  [{idx}] {pdf_name}, Page {page}\n"
            self._append_response(citation, tag="citation")
        
        self._append_response("="*70 + "\n")
    
    def _clear_response(self):
        """Clear response text area."""
        self.response_text.config(state=tk.NORMAL)
        self.response_text.delete(1.0, tk.END)
        self.response_text.config(state=tk.DISABLED)
    
    def _on_query_complete(self):
        """Callback when query processing is complete."""
        self.is_processing = False
        self.btn_submit.config(state=tk.NORMAL)
        self._update_status("Ready")
    
    def _update_status(self, message: str):
        """Update status bar message."""
        self.status_label.config(text=message)


def create_app():
    """Create and return the Tkinter application."""
    root = tk.Tk()
    app = RAGMainWindow(root)
    return root
