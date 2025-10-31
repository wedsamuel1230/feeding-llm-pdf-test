#!/usr/bin/env python3
"""GUI entry point for RAG pipeline."""

import sys
from src.gui import create_app


def main():
    """Launch GUI application."""
    root = create_app()
    root.mainloop()


if __name__ == "__main__":
    main()
