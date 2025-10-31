"""Custom drag-and-drop widget for PDF file upload."""

from PyQt5.QtWidgets import QListWidget, QListWidgetItem, QAbstractItemView
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QDragEnterEvent, QDropEvent
from pathlib import Path


class DropZone(QListWidget):
    """Drag-and-drop zone for PDF files."""
    
    files_changed = pyqtSignal(list)  # Emit list of file paths
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setDragDropMode(QAbstractItemView.DragDrop)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setAlternatingRowColors(True)
        
        # Styling
        self.setStyleSheet("""
            QListWidget {
                border: 2px dashed #aaaaaa;
                border-radius: 8px;
                background-color: #f9f9f9;
                padding: 10px;
                font-size: 13px;
            }
            QListWidget::item {
                padding: 8px;
                border-radius: 4px;
            }
            QListWidget::item:selected {
                background-color: #0078d4;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #e8e8e8;
            }
        """)
        
        # Placeholder text
        self._show_placeholder()
    
    def _show_placeholder(self):
        """Show placeholder text when empty."""
        if self.count() == 0:
            placeholder = QListWidgetItem("📄 Drag and drop PDF files here, or click 'Add Files' button")
            placeholder.setFlags(Qt.NoItemFlags)
            placeholder.setForeground(Qt.gray)
            self.addItem(placeholder)
    
    def _remove_placeholder(self):
        """Remove placeholder text."""
        if self.count() > 0 and self.item(0).flags() == Qt.NoItemFlags:
            self.takeItem(0)
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter event."""
        if event.mimeData().hasUrls():
            # Check if any file is a PDF
            urls = event.mimeData().urls()
            has_pdf = any(url.toLocalFile().lower().endswith('.pdf') for url in urls)
            if has_pdf:
                event.acceptProposedAction()
            else:
                event.ignore()
        else:
            event.ignore()
    
    def dragMoveEvent(self, event):
        """Handle drag move event."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()
    
    def dropEvent(self, event: QDropEvent):
        """Handle drop event."""
        if event.mimeData().hasUrls():
            self._remove_placeholder()
            
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                if file_path.lower().endswith('.pdf'):
                    self.add_file(file_path)
            
            event.acceptProposedAction()
            self.files_changed.emit(self.get_files())
        else:
            event.ignore()
    
    def add_file(self, file_path: str):
        """Add a file to the list."""
        self._remove_placeholder()
        
        # Check for duplicates
        existing_paths = [self.item(i).data(Qt.UserRole) for i in range(self.count())]
        if file_path in existing_paths:
            return
        
        # Add new file
        file_name = Path(file_path).name
        item = QListWidgetItem(f"📄 {file_name}")
        item.setData(Qt.UserRole, file_path)
        self.addItem(item)
    
    def add_files(self, file_paths: list):
        """Add multiple files."""
        for path in file_paths:
            self.add_file(path)
        self.files_changed.emit(self.get_files())
    
    def remove_selected(self):
        """Remove selected files."""
        for item in self.selectedItems():
            self.takeItem(self.row(item))
        
        if self.count() == 0:
            self._show_placeholder()
        
        self.files_changed.emit(self.get_files())
    
    def clear_all(self):
        """Clear all files."""
        self.clear()
        self._show_placeholder()
        self.files_changed.emit([])
    
    def get_files(self) -> list:
        """Get list of all file paths."""
        files = []
        for i in range(self.count()):
            item = self.item(i)
            if item.flags() != Qt.NoItemFlags:  # Skip placeholder
                file_path = item.data(Qt.UserRole)
                if file_path:
                    files.append(file_path)
        return files
