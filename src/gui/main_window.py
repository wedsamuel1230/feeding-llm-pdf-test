"""Main GUI window for RAG pipeline."""

import sys
from pathlib import Path
from typing import List, Optional

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QTextEdit, QLabel, QComboBox, QFileDialog,
    QLineEdit, QMessageBox, QSplitter, QGroupBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QIcon

from openai import OpenAI

from .. import config
from ..core import (
    chunk_multiple_pdfs,
    EmbeddingCache,
    Reranker,
    retrieve_with_reranking,
    build_rag_prompt
)
from .widgets import DropZone


class QueryThread(QThread):
    """Background thread for RAG query processing."""
    
    chunk_received = pyqtSignal(str)  # Streaming chunks
    finished = pyqtSignal()
    error = pyqtSignal(str)
    
    def __init__(self, client: OpenAI, prompt: str, model: str):
        super().__init__()
        self.client = client
        self.prompt = prompt
        self.model = model
    
    def run(self):
        """Execute query in background."""
        try:
            with self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful AI assistant that answers questions about PDF documents with accurate citations."
                    },
                    {
                        "role": "user",
                        "content": self.prompt
                    }
                ],
                max_tokens=2048,
                stream=True,
            ) as response:
                for chunk in response:
                    if chunk.choices[0].delta.content:
                        self.chunk_received.emit(chunk.choices[0].delta.content)
            
            self.finished.emit()
        
        except Exception as e:
            self.error.emit(str(e))


class RAGMainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🚀 Advanced RAG Pipeline - PDF Q&A")
        self.setGeometry(100, 100, 1200, 800)
        
        # Core components
        self.embedding_cache: Optional[EmbeddingCache] = None
        self.reranker: Optional[Reranker] = None
        self.poe_client: Optional[OpenAI] = None
        self.chunks: List[dict] = []
        self.query_thread: Optional[QueryThread] = None
        
        # Setup UI
        self._setup_ui()
        self._setup_connections()
        
        # Initialize components
        self._initialize_components()
    
    def _setup_ui(self):
        """Setup the user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # === Top Section: Configuration ===
        config_group = QGroupBox("⚙️ Configuration")
        config_layout = QVBoxLayout()
        
        # Model selection
        model_layout = QHBoxLayout()
        model_label = QLabel("LLM Model:")
        model_label.setMinimumWidth(100)
        
        self.model_combo = QComboBox()
        self.model_combo.addItems(config.POE_AVAILABLE_MODELS)
        self.model_combo.setCurrentText(config.POE_MODEL)
        self.model_combo.setToolTip("Select the Poe API model to use")
        
        model_layout.addWidget(model_label)
        model_layout.addWidget(self.model_combo, 1)
        
        # API key status
        self.api_status_label = QLabel()
        self._update_api_status()
        model_layout.addWidget(self.api_status_label)
        
        config_layout.addLayout(model_layout)
        config_group.setLayout(config_layout)
        main_layout.addWidget(config_group)
        
        # === Middle Section: File Upload ===
        file_group = QGroupBox("📄 PDF Documents")
        file_layout = QVBoxLayout()
        
        # Drop zone
        self.drop_zone = DropZone()
        self.drop_zone.setMinimumHeight(150)
        file_layout.addWidget(self.drop_zone)
        
        # File control buttons
        btn_layout = QHBoxLayout()
        
        self.add_btn = QPushButton("➕ Add Files")
        self.add_btn.clicked.connect(self._add_files)
        
        self.remove_btn = QPushButton("➖ Remove Selected")
        self.remove_btn.clicked.connect(self.drop_zone.remove_selected)
        
        self.clear_btn = QPushButton("🗑️ Clear All")
        self.clear_btn.clicked.connect(self.drop_zone.clear_all)
        
        self.process_btn = QPushButton("⚡ Process PDFs")
        self.process_btn.clicked.connect(self._process_pdfs)
        self.process_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                font-weight: bold;
                padding: 8px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.remove_btn)
        btn_layout.addWidget(self.clear_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(self.process_btn)
        
        file_layout.addLayout(btn_layout)
        
        # Status label
        self.status_label = QLabel("📊 Status: Ready")
        self.status_label.setStyleSheet("color: #666; font-style: italic;")
        file_layout.addWidget(self.status_label)
        
        file_group.setLayout(file_layout)
        main_layout.addWidget(file_group)
        
        # === Bottom Section: Query & Response ===
        qa_splitter = QSplitter(Qt.Vertical)
        
        # Query section
        query_group = QGroupBox("❓ Your Question")
        query_layout = QVBoxLayout()
        
        self.query_input = QTextEdit()
        self.query_input.setPlaceholderText("Enter your question about the PDF documents...")
        self.query_input.setMaximumHeight(100)
        self.query_input.setFont(QFont("Segoe UI", 10))
        
        self.ask_btn = QPushButton("🚀 Ask Question")
        self.ask_btn.clicked.connect(self._ask_question)
        self.ask_btn.setEnabled(False)
        self.ask_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                font-weight: bold;
                padding: 10px;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        
        query_layout.addWidget(self.query_input)
        query_layout.addWidget(self.ask_btn)
        query_group.setLayout(query_layout)
        
        # Response section
        response_group = QGroupBox("💬 AI Response")
        response_layout = QVBoxLayout()
        
        self.response_display = QTextEdit()
        self.response_display.setReadOnly(True)
        self.response_display.setFont(QFont("Segoe UI", 10))
        self.response_display.setPlaceholderText("AI response will appear here...")
        
        response_layout.addWidget(self.response_display)
        response_group.setLayout(response_layout)
        
        qa_splitter.addWidget(query_group)
        qa_splitter.addWidget(response_group)
        qa_splitter.setSizes([150, 350])
        
        main_layout.addWidget(qa_splitter, 1)
    
    def _setup_connections(self):
        """Setup signal-slot connections."""
        self.drop_zone.files_changed.connect(self._on_files_changed)
    
    def _initialize_components(self):
        """Initialize ML components."""
        try:
            self.status_label.setText("📊 Status: Initializing ML models...")
            
            # Initialize Poe client
            if config.POE_API_KEY:
                self.poe_client = OpenAI(
                    api_key=config.POE_API_KEY,
                    base_url=config.POE_BASE_URL,
                )
            
            # Initialize embedding cache and reranker
            self.embedding_cache = EmbeddingCache()
            self.reranker = Reranker()
            
            self.status_label.setText("📊 Status: Ready - Add PDF files to begin")
        
        except Exception as e:
            self.status_label.setText(f"⚠️ Status: Initialization error: {str(e)}")
            QMessageBox.critical(self, "Initialization Error", f"Failed to initialize components:\n{str(e)}")
    
    def _update_api_status(self):
        """Update API key status indicator."""
        if config.POE_API_KEY:
            self.api_status_label.setText("✅ API Key Set")
            self.api_status_label.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.api_status_label.setText("❌ API Key Missing")
            self.api_status_label.setStyleSheet("color: red; font-weight: bold;")
            self.api_status_label.setToolTip("Set POE_API_KEY environment variable")
    
    def _on_files_changed(self, files: list):
        """Handle file list changes."""
        if files:
            self.status_label.setText(f"📊 Status: {len(files)} file(s) added - Click 'Process PDFs'")
        else:
            self.status_label.setText("📊 Status: No files added")
            self.chunks = []
            self.ask_btn.setEnabled(False)
    
    def _add_files(self):
        """Open file dialog to add PDFs."""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select PDF Files",
            "",
            "PDF Files (*.pdf)"
        )
        if files:
            self.drop_zone.add_files(files)
    
    def _process_pdfs(self):
        """Process uploaded PDFs."""
        files = self.drop_zone.get_files()
        
        if not files:
            QMessageBox.warning(self, "No Files", "Please add PDF files first.")
            return
        
        try:
            self.status_label.setText(f"⏳ Processing {len(files)} PDF(s)...")
            self.process_btn.setEnabled(False)
            
            # Chunk PDFs
            self.chunks = chunk_multiple_pdfs(files)
            
            # Pre-generate embeddings
            if self.embedding_cache:
                self.embedding_cache.get_embeddings(self.chunks)
            
            self.status_label.setText(f"✅ Processed {len(files)} PDF(s) - {len(self.chunks)} chunks ready")
            self.ask_btn.setEnabled(True)
            self.process_btn.setEnabled(True)
            
            QMessageBox.information(
                self,
                "Success",
                f"Successfully processed {len(files)} PDF(s)\n{len(self.chunks)} text chunks extracted and embedded."
            )
        
        except Exception as e:
            self.status_label.setText(f"❌ Error processing PDFs: {str(e)}")
            self.process_btn.setEnabled(True)
            QMessageBox.critical(self, "Processing Error", f"Failed to process PDFs:\n{str(e)}")
    
    def _ask_question(self):
        """Ask a question about the PDFs."""
        query = self.query_input.toPlainText().strip()
        
        if not query:
            QMessageBox.warning(self, "No Question", "Please enter a question.")
            return
        
        if not self.chunks:
            QMessageBox.warning(self, "No Documents", "Please process PDF files first.")
            return
        
        if not config.POE_API_KEY:
            QMessageBox.critical(
                self,
                "API Key Missing",
                "Please set the POE_API_KEY environment variable and restart the application."
            )
            return
        
        try:
            # Disable UI during processing
            self.ask_btn.setEnabled(False)
            self.response_display.clear()
            self.response_display.append("🔍 Retrieving relevant documents...\n")
            
            # Retrieve relevant chunks
            retrieved = retrieve_with_reranking(
                query,
                self.chunks,
                self.embedding_cache,
                self.reranker,
                top_k=config.FINAL_TOP_K
            )
            
            if not retrieved:
                self.response_display.append("⚠️ No relevant documents found.\n")
                self.ask_btn.setEnabled(True)
                return
            
            self.response_display.append(f"✓ Retrieved {len(retrieved)} relevant chunks\n")
            self.response_display.append("💬 Querying AI model...\n\n")
            self.response_display.append("─" * 70 + "\n")
            
            # Build prompt
            prompt = build_rag_prompt(query, retrieved)
            
            # Get selected model
            model = self.model_combo.currentText()
            
            # Start query thread
            self.query_thread = QueryThread(self.poe_client, prompt, model)
            self.query_thread.chunk_received.connect(self._on_chunk_received)
            self.query_thread.finished.connect(lambda: self._on_query_finished(retrieved))
            self.query_thread.error.connect(self._on_query_error)
            self.query_thread.start()
        
        except Exception as e:
            self.response_display.append(f"\n❌ Error: {str(e)}\n")
            self.ask_btn.setEnabled(True)
    
    def _on_chunk_received(self, chunk: str):
        """Handle streaming response chunk."""
        self.response_display.insertPlainText(chunk)
        self.response_display.ensureCursorVisible()
    
    def _on_query_finished(self, retrieved_chunks: list):
        """Handle query completion."""
        self.response_display.append("\n\n" + "─" * 70 + "\n")
        self.response_display.append("📚 SOURCE CITATIONS:\n")
        self.response_display.append("─" * 70 + "\n")
        
        for idx, chunk in enumerate(retrieved_chunks, start=1):
            pdf_name = chunk.get('pdf_name', 'Unknown')
            page = chunk.get('page', '?')
            score = chunk.get('score', 0.0)
            self.response_display.append(f"  [{idx}] {pdf_name}, Page {page} (score: {score:.3f})\n")
        
        self.response_display.append("─" * 70 + "\n")
        self.ask_btn.setEnabled(True)
    
    def _on_query_error(self, error: str):
        """Handle query error."""
        self.response_display.append(f"\n❌ Error: {error}\n")
        
        if "api_key" in error.lower():
            self.response_display.append("\n⚠️ Poe API key not set or invalid.\n")
            self.response_display.append("Set it with: $env:POE_API_KEY = 'your-api-key'\n")
        
        self.ask_btn.setEnabled(True)
