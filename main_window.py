#!/usr/bin/env python3
"""
K-Vault Main Window (Phase 3 - Models Integration)
"""
from PyQt6.QtWidgets import (QMainWindow, QSplitter, QTreeWidget, QTreeWidgetItem, 
                             QTextEdit, QLineEdit, QPushButton, QVBoxLayout, 
                             QWidget, QHBoxLayout, QLabel, QMessageBox, QMenu)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QKeySequence, QShortcut, QAction, QIcon
import sys

from models import Note, Folder
from db_manager import db_manager

class MainWindow(QMainWindow):
    """Main application window with models"""
    
    note_selected = pyqtSignal(int)
    note_updated = pyqtSignal(Note)
    
    def __init__(self):
        super().__init__()
        self.current_note: Optional[Note] = None
        self.auto_save_timer = QTimer()
        self.setup_ui()
        self.load_hierarchy()
        self.connect_signals()
        self.statusBar().showMessage("Ready - Phase 3 Complete!")
    
    def setup_ui(self):
        """Enhanced UI setup"""
        self.setWindowTitle("K-Vault - Phase 3 (Models + Enhanced DB)")
        self.resize(1400, 900)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)
        
        # Enhanced Sidebar
        self.sidebar = QTreeWidget()
        self.sidebar.setHeaderLabel("📁 Folders & Notes (Phase 3)")
        self.sidebar.setMinimumWidth(350)
        splitter.addWidget(self.sidebar)
        
        # Editor Area
        editor_widget = QWidget()
        editor_layout = QVBoxLayout(editor_widget)
        
        # Toolbar
        toolbar = self.create_toolbar()
        editor_layout.addWidget(toolbar)
        
        # Search
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Ctrl+K - Instant fuzzy search...")
        editor_layout.addWidget(self.search_input)
        
        # Editor
        self.editor = QTextEdit()
        self.editor.setPlaceholderText("👈 Click a note to edit...\n\n💡 Phase 3 Features:\n• Data models (Note/Folder classes)\n• Enhanced DB with indexes\n• Auto-save every 3s\n• Full hierarchy support")
        self.editor.setFont(QFont("Segoe UI", 12))
        self.editor.setMinimumHeight(600)
        editor_layout.addWidget(self.editor)
        
        splitter.addWidget(editor_widget)
        splitter.setSizes([350, 1050])
        
        self.setup_menu()
    
    def create_toolbar(self):
        """Create editor toolbar"""
        from PyQt6.QtWidgets import QToolBar
        toolbar = QToolBar()
        toolbar.setMovable(False)
        
        new_btn = QPushButton("📄 New Note")
        new_btn.clicked.connect(self.create_new_note)
        toolbar.addWidget(new_btn)
        
        save_btn = QPushButton("💾 Save")
        save_btn.clicked.connect(self.save_current_note)
        toolbar.addWidget(save_btn)
        
        toolbar.addSeparator()
        
        self.status_label = QLabel("Ready")
        toolbar.addWidget(self.status_label)
        
        return toolbar
    
    def setup_menu(self):
        """Enhanced menu"""
        menubar = self.menuBar()
        
        file_menu = menubar.addMenu("File")
        new_action = QAction("New Note", self)
        new_action.setShortcut(QKeySequence("Ctrl+N"))
        new_action.triggered.connect(self.create_new_note)
        file_menu.addAction(new_action)
        
        file_menu.addSeparator()
        exit_action = QAction("Exit", self)
        exit_action.setShortcut(QKeySequence("Ctrl+Q"))
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
    
    def load_hierarchy(self):
        """Load full folder hierarchy"""
        self.sidebar.clear()
        
        # Load root folders and notes
        root_folders = db_manager.get_folders()
        unassigned_notes = db_manager.get_notes()
        
        for folder in root_folders:
            self._add_folder_to_tree(folder)
        
        # Unassigned notes
        if unassigned_notes:
            unassigned_item = QTreeWidgetItem(["📋 Unassigned Notes"])
            unassigned_item.setData(0, Qt.ItemDataRole.UserRole, "root:unassigned")
            self.sidebar.addTopLevelItem(unassigned_item)
            for note in unassigned_notes:
                self._add_note_to_tree(note, unassigned_item)
    
    def _add_folder_to_tree(self, folder: Folder, parent_item: Optional[QTreeWidgetItem] = None):
        """Recursively add folder to tree"""
        if parent_item is None:
            item = QTreeWidgetItem([f"📁 {folder.name}"])
            self.sidebar.addTopLevelItem(item)
        else:
            item = QTreeWidgetItem([f"  📁 {folder.name}"])
            parent_item.addChild(item)
        
        item.setData(0, Qt.ItemDataRole.UserRole, f"folder:{folder.id}")
        item.setIcon(0, QIcon())  # Placeholder
        
        # Add notes
        for note in folder.notes:
            self._add_note_to_tree(note, item)
        
        # Add children folders
        for child in folder.children:
            self._add_folder_to_tree(child, item)
    
    def _add_note_to_tree(self, note: Note, parent_item: QTreeWidgetItem):
        """Add note to tree"""
        item = QTreeWidgetItem([f"  📄 {note.title}"])
        item.setData(0, Qt.ItemDataRole.UserRole, f"note:{note.id}")
        parent_item.addChild(item)
    
    def connect_signals(self):
        """Connect signals"""
        self.sidebar.itemClicked.connect(self.on_item_clicked)
        self.editor.textChanged.connect(self.on_editor_changed)
        
        # Auto-save every 3 seconds
        self.auto_save_timer.timeout.connect(self.auto_save)
        self.auto_save_timer.start(3000)
        
        # Shortcuts
        QShortcut(QKeySequence("Ctrl+K"), self).activated.connect(self.focus_search)
        QShortcut(QKeySequence("Ctrl+S"), self).activated.connect(self.save_current_note)
    
    def on_item_clicked(self, item: QTreeWidgetItem):
        """Handle item selection"""
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if data and data.startswith("note:"):
            note_id = int(data.split(":")[1])
            self.load_note(note_id)
    
    def load_note(self, note_id: int):
        """Load note using models"""
        note = db_manager.get_note(note_id)
        if note:
            self.current_note = note
            self.editor.setText(note.content)
            self.editor.setFocus()
            self.status_label.setText(f"📄 {note.title} ({len(note.content)} chars)")
            self.statusBar().showMessage(f"Loaded: {note.title}")
    
    def create_new_note(self):
        """Create new note"""
        note = Note(title="Untitled Note", content="# New Note\n\nStart writing...")
        note_id = db_manager.create_note(note)
        self.load_note(note_id)
        self.load_hierarchy()  # Refresh tree
    
    def save_current_note(self):
        """Save current note"""
        if self.current_note:
            self.current_note.content = self.editor.toPlainText()
            self.current_note.title = self.current_note.title or "Untitled"
            db_manager.update_note(self.current_note)
            self.status_label.setText("💾 Saved")
            QTimer.singleShot(1000, lambda: self.status_label.setText("Ready"))
    
    def auto_save(self):
        """Auto-save current note"""
        if self.current_note and self.editor.document().isModified():
            self.save_current_note()
    
    def on_editor_changed(self):
        """Editor changed"""
        if self.current_note:
            self.status_label.setText("⏳ Unsaved changes")
    
    def focus_search(self):
        """Focus search"""
        self.search_input.setFocus()
        self.search_input.selectAll()
    
    def closeEvent(self, event):
        """Save on close"""
        if self.current_note:
            self.save_current_note()
        db_manager.close()
        event.accept()
