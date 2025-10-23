#!/usr/bin/env python3
"""
K-Vault Main Window (Phase 6 - Drag & Drop Folders)
"""
from typing import Optional
from PyQt6.QtWidgets import (QMainWindow, QSplitter, QTreeWidgetItem, QVBoxLayout, QWidget, 
                             QHBoxLayout, QLineEdit, QMessageBox, QTreeWidget)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QKeySequence, QShortcut
import sys

from models import Note
from db_manager import DatabaseManager
from markdown_editor import MarkdownEditor
from folder_sidebar import FolderSidebar

class MainWindow(QMainWindow):
    """Phase 6: Full drag & drop + folder creation"""
    
    def __init__(self, db_manager: DatabaseManager):
        super().__init__()
        self.db_manager = db_manager
        self.current_note: Optional[Note] = None
        
        self.setup_ui()
        self.load_content()
        self.connect_signals()
        self.statusBar().showMessage("🚀 K-Vault Phase 6 - Drag & Drop Ready!")
    
    def setup_ui(self):
        """VSCode-style layout"""
        self.setWindowTitle("K-Vault - Phase 6 (Drag & Drop Folders)")
        self.resize(1600, 1000)
        self.setMinimumSize(1200, 800)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout = QHBoxLayout(central_widget)
        main_layout.addWidget(main_splitter)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # DRAG & DROP SIDEBAR
        self.sidebar = FolderSidebar(self.db_manager)
        main_splitter.addWidget(self.sidebar)
        
        # Editor Area
        editor_layout = QVBoxLayout()
        
        # Search bar
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Ctrl+K - Instant Search...")
        self.search_input.setMinimumHeight(40)
        editor_layout.addWidget(self.search_input)
        
        # Rich Markdown Editor
        self.markdown_editor = MarkdownEditor()
        editor_layout.addWidget(self.markdown_editor, 1)
        
        editor_container = QWidget()
        editor_container.setLayout(editor_layout)
        main_splitter.addWidget(editor_container)
        
        main_splitter.setSizes([350, 1250])
        main_splitter.setCollapsible(0, False)
    
    def load_content(self):
        """Load initial hierarchy"""
        self.sidebar.load_hierarchy()
    
    def connect_signals(self):
        """Connect all signals"""
        self.sidebar.itemClicked.connect(self.on_item_clicked)
        self.sidebar.itemDoubleClicked.connect(self.on_item_double_clicked)
        self.sidebar.customContextMenuRequested.connect(self.on_context_menu)
        self.sidebar.itemChanged.connect(self.on_item_renamed)
        
        # Rich editor
        self.markdown_editor.content_changed.connect(self.on_content_changed)
        self.markdown_editor.note_saved.connect(self.save_current_note)
        
        # Shortcuts
        QShortcut(QKeySequence("Ctrl+K"), self).activated.connect(self.focus_search)
        QShortcut(QKeySequence("Ctrl+N"), self).activated.connect(self.create_new_note)
    
    def on_item_clicked(self, item: QTreeWidgetItem):
        """Load note when clicked"""
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if data and data.startswith("note:"):
            note_id = int(data.split(":")[1])
            self.load_note(note_id)
    
    def on_item_double_clicked(self, item: QTreeWidgetItem):
        """Toggle folder expand/collapse"""
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if data and data.startswith("folder:"):
            if item.isExpanded():
                self.sidebar.collapseItem(item)
            else:
                self.sidebar.expandItem(item)
    
    def on_context_menu(self, position):
        """Show context menu"""
        item = self.sidebar.itemAt(position)
        if item:
            self.sidebar.contextMenuEvent(self.sidebar.mapEventToParent(position))
    
    def on_item_renamed(self, item: QTreeWidgetItem, column: int):
        """Handle rename completion"""
        data = item.data(0, Qt.ItemDataRole.UserRole)
        new_name = item.text(0).strip()
        
        if new_name and data:
            try:
                if data.startswith("note:"):
                    note_id = int(data.split(":")[1])
                    note = self.db_manager.get_note(note_id)
                    if note:
                        note.title = new_name.replace("📄 ", "").replace("  ", "")
                        self.db_manager.update_note(note)
                self.sidebar.load_hierarchy()
                self.statusBar().showMessage(f"✅ Renamed: {new_name}")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Rename failed: {str(e)}")
    
    def load_note(self, note_id: int):
        """Load note into rich editor"""
        note = self.db_manager.get_note(note_id)
        if note:
            self.current_note = note
            self.markdown_editor.set_content(note.content)
            self.statusBar().showMessage(f"📄 {note.title} - Drag notes between folders!")
    
    def create_new_note(self):
        """Create new note"""
        note = Note(title="Untitled", content="# New Note\n\nDrag me anywhere! 🎉")
        note.id = self.db_manager.create_note(note)
        self.sidebar.load_hierarchy()
        self.load_note(note.id)
    
    def save_current_note(self):
        """Save current note"""
        if self.current_note:
            self.current_note.content = self.markdown_editor.get_content()
            self.db_manager.update_note(self.current_note)
            self.statusBar().showMessage("💾 Saved")
    
    def on_content_changed(self, content: str):
        """Auto-save"""
        if self.current_note:
            QTimer.singleShot(2000, self.save_current_note)
    
    def focus_search(self):
        """Focus search"""
        self.search_input.setFocus()
        self.search_input.selectAll()
    
    def closeEvent(self, event):
        """Save on close"""
        if self.current_note:
            self.save_current_note()
        event.accept()
