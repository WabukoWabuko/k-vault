#!/usr/bin/env python3
"""
K-Vault Main Window
Central UI component with sidebar, editor, search
"""
from PyQt6.QtWidgets import (QMainWindow, QSplitter, QTreeWidget, QTreeWidgetItem, 
                             QTextEdit, QLineEdit, QPushButton, QVBoxLayout, 
                             QWidget, QHBoxLayout, QLabel, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QKeySequence, QShortcut, QAction
import sys

from db_utils import db

class MainWindow(QMainWindow):
    """Main application window"""
    
    note_selected = pyqtSignal(int)  # Signal when note is selected
    
    def __init__(self):
        super().__init__()
        self.current_note_id = None
        self.setup_ui()
        self.load_folders()
        self.connect_signals()
        self.statusBar().showMessage("Ready")
    
    def setup_ui(self):
        """Setup main UI layout"""
        self.setWindowTitle("K-Vault - Phase 2")
        self.resize(1200, 800)
        
        # Central widget with splitter
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout with horizontal splitter
        main_layout = QHBoxLayout(central_widget)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)
        
        # LEFT: Sidebar (folders + notes)
        self.sidebar = QTreeWidget()
        self.sidebar.setHeaderLabel("📁 Folders & Notes")
        self.sidebar.setMinimumWidth(300)
        splitter.addWidget(self.sidebar)
        
        # RIGHT: Editor area
        editor_widget = QWidget()
        editor_layout = QVBoxLayout(editor_widget)
        
        # Search bar
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search notes... (Ctrl+K)")
        editor_layout.addWidget(self.search_input)
        
        # Editor
        self.editor = QTextEdit()
        self.editor.setPlaceholderText("Select a note or create new...")
        self.editor.setFont(QFont("Consolas", 12))
        editor_layout.addWidget(self.editor)
        
        splitter.addWidget(editor_widget)
        splitter.setSizes([300, 900])  # Sidebar:Editor ratio
        
        # Menu bar
        self.setup_menu()
    
    def setup_menu(self):
        """Setup menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        new_action = QAction("New Note", self)
        file_menu.addAction(new_action)
    
    def load_folders(self):
        """Load folder structure into sidebar"""
        self.sidebar.clear()
        
        # Root items
        root_folders = db.get_folders()
        for folder in root_folders:
            folder_item = QTreeWidgetItem([folder["name"]])
            folder_item.setData(0, Qt.ItemDataRole.UserRole, f"folder:{folder['id']}")
            self.sidebar.addTopLevelItem(folder_item)
            
            # Add notes to folder
            notes = db.get_notes(folder["id"])
            for note in notes:
                note_item = QTreeWidgetItem([f"  📄 {note['title']}"])
                note_item.setData(0, Qt.ItemDataRole.UserRole, f"note:{note['id']}")
                folder_item.addChild(note_item)
        
        # Unassigned notes
        unassigned_notes = db.get_notes()
        if unassigned_notes:
            unassigned_item = QTreeWidgetItem(["📋 Unassigned Notes"])
            self.sidebar.addTopLevelItem(unassigned_item)
            for note in unassigned_notes:
                note_item = QTreeWidgetItem([f"  📄 {note['title']}"])
                note_item.setData(0, Qt.ItemDataRole.UserRole, f"note:{note['id']}")
                unassigned_item.addChild(note_item)
    
    def connect_signals(self):
        """Connect all signals"""
        self.sidebar.itemClicked.connect(self.on_item_clicked)
        
        # Ctrl+K for search
        search_shortcut = QShortcut(QKeySequence("Ctrl+K"), self)
        search_shortcut.activated.connect(self.focus_search)
    
    def on_item_clicked(self, item: QTreeWidgetItem):
        """Handle sidebar item selection"""
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if data and data.startswith("note:"):
            note_id = int(data.split(":")[1])
            self.load_note(note_id)
    
    def load_note(self, note_id: int):
        """Load note into editor"""
        note = db.get_note(note_id)
        if note:
            self.current_note_id = note_id
            self.editor.setText(note["content"])
            self.editor.setFocus()
            self.statusBar().showMessage(f"Loaded: {note['title']}")
    
    def focus_search(self):
        """Focus search input"""
        self.search_input.setFocus()
    
    def closeEvent(self, event):
        """Save on close"""
        db.close()
        event.accept()
