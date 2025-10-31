#!/usr/bin/env python3
"""GUI entry point for RAG pipeline."""

import sys
from PyQt5.QtWidgets import QApplication

from src.gui import RAGMainWindow


def main():
    """Launch GUI application."""
    app = QApplication(sys.argv)
    app.setApplicationName("Advanced RAG Pipeline")
    app.setOrganizationName("RAG System")
    
    window = RAGMainWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
