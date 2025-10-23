#!/usr/bin/env python3
"""
K-Vault Main Window (Phase 4 - VSCode Style + Database Parameter)
"""
from typing import Optional
from PyQt6.QtWidgets import (QMainWindow, QSplitter, QTreeWidget, QTreeWidgetItem, 
                             QTextEdit, QLineEdit, QPushButton, QVBoxLayout, 
                             QWidget, QHBoxLayout, QLabel, QMessageBox, QMenu, 
                             QToolBar, QInputDialog, QSizePolicy)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QKeySequence, QShortcut, QAction, QIcon
import sys

from models import Note, Folder
from db_manager import DatabaseManager

class MainWindow(QMainWindow):
    """VSCode-style resizable main window"""
    
    note_selected = pyqtSignal(int)
    note_updated = pyqtSignal(Note)
    
    def __init__(self, db_manager: DatabaseManager):  # ← ACCEPT DB PARAMETER
        super().__init__()
        self.db_manager = db_manager  # ← STORE DB INSTANCE
        self.current_note: Optional[Note] = None
        self.auto_save_timer = QTimer()
        self.is_renaming = False
        self.setup_ui()
        self.load_hierarchy()
        self.connect_signals()
        self.statusBar().showMessage("🚀 K-Vault Phase 4 - VSCode Style Ready!")
    
    def setup_ui(self):
        """VSCode-style resizable layout"""
        self.setWindowTitle("K-Vault - Phase 4 (VSCode Style)")
        self.resize(1400, 900)
        self.setMinimumSize(800, 600)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout = QHBoxLayout(central_widget)
        main_layout.addWidget(main_splitter)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Sidebar
        self.sidebar = QTreeWidget()
        self.sidebar.setHeaderLabel("📁 Folders & Notes")
        self.sidebar.setMinimumWidth(280)
        self.sidebar.setMaximumWidth(500)
        self.sidebar.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        main_splitter.addWidget(self.sidebar)
        
        # Editor Area
        editor_widget = QWidget()
        editor_layout = QVBoxLayout(editor_widget)
        editor_layout.setContentsMargins(8, 8, 8, 8)
        editor_layout.setSpacing(8)
        
        # Toolbar
        toolbar = self.create_toolbar()
        editor_layout.addWidget(toolbar)
        
        # Search
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Ctrl+K - Instant Search...")
        self.search_input.setMinimumHeight(36)
        editor_layout.addWidget(self.search_input)
        
        # Editor
        self.editor = QTextEdit()
        self.editor.setPlaceholderText(
            "👈 Click a note/folder to start...\n\n"
            "🎉 PHASE 4 FEATURES:\n"
            "• VSCode-style resizable panels\n"
            "• Maximize fills entire screen\n"
            "• Right-click rename (folders/notes)\n"
            "• F2 = Rename shortcut\n"
            "• Drag handle between sidebar/editor"
        )
        self.editor.setFont(QFont("SF Mono", 13))
        self.editor.setMinimumHeight(500)
        editor_layout.addWidget(self.editor, 1)
        
        main_splitter.addWidget(editor_widget)
        main_splitter.setSizes([320, 1080])
        main_splitter.setCollapsible(0, False)
        
        self.setup_menu()
    
    def create_toolbar(self):
        """VSCode-style toolbar"""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        toolbar.setFloatable(False)
        
        new_btn = QPushButton("📄 New Note")
        new_btn.setShortcut(QKeySequence("Ctrl+N"))
        new_btn.clicked.connect(self.create_new_note)
        toolbar.addWidget(new_btn)
        
        save_btn = QPushButton("💾 Save")
        save_btn.setShortcut(QKeySequence("Ctrl+S"))
        save_btn.clicked.connect(self.save_current_note)
        toolbar.addWidget(save_btn)
        
        toolbar.addSeparator()
        
        self.status_label = QLabel("Ready")
        self.status_label.setMinimumWidth(200)
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
        
        edit_menu = menubar.addMenu("Edit")
        rename_action = QAction("Rename", self)
        rename_action.setShortcut(QKeySequence("F2"))
        rename_action.triggered.connect(self.rename_current_item)
        edit_menu.addAction(rename_action)
    
    def load_hierarchy(self):
        """Load full folder hierarchy"""
        self.sidebar.clear()
        root_folders = self.db_manager.get_full_hierarchy()  # ← USE SELF.DB_MANAGER
        unassigned_notes = self.db_manager.get_notes()       # ← USE SELF.DB_MANAGER
        
        for folder in root_folders:
            self._add_folder_to_tree(folder)
        
        if unassigned_notes:
            unassigned_item = QTreeWidgetItem(["📋 Unassigned Notes"])
            unassigned_item.setData(0, Qt.ItemDataRole.UserRole, "root:unassigned")
            self.sidebar.addTopLevelItem(unassigned_item)
            for note in unassigned_notes:
                self._add_note_to_tree(note, unassigned_item)
    
    def _add_folder_to_tree(self, folder: Folder, parent_item: Optional[QTreeWidgetItem] = None):
        """Add folder recursively"""
        if parent_item:
            item = QTreeWidgetItem([f"  📁 {folder.name}"])
            parent_item.addChild(item)
        else:
            item = QTreeWidgetItem([f"📁 {folder.name}"])
            self.sidebar.addTopLevelItem(item)
        
        item.setData(0, Qt.ItemDataRole.UserRole, f"folder:{folder.id}")
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
        
        for note in folder.notes:
            self._add_note_to_tree(note, item)
        
        for child in folder.children:
            self._add_folder_to_tree(child, item)
    
    def _add_note_to_tree(self, note: Note, parent_item: QTreeWidgetItem):
        """Add note to tree"""
        item = QTreeWidgetItem([f"  📄 {note.title}"])
        item.setData(0, Qt.ItemDataRole.UserRole, f"note:{note.id}")
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
        parent_item.addChild(item)
    
    def connect_signals(self):
        """Connect all signals"""
        self.sidebar.itemClicked.connect(self.on_item_clicked)
        self.sidebar.itemDoubleClicked.connect(self.on_item_double_clicked)
        self.sidebar.customContextMenuRequested.connect(self.show_context_menu)
        self.sidebar.itemChanged.connect(self.on_item_renamed)
        
        self.editor.textChanged.connect(self.on_editor_changed)
        
        self.auto_save_timer.timeout.connect(self.auto_save)
        self.auto_save_timer.start(2000)
        
        QShortcut(QKeySequence("Ctrl+K"), self).activated.connect(self.focus_search)
        QShortcut(QKeySequence("F2"), self).activated.connect(self.rename_current_item)
    
    def show_context_menu(self, position):
        """Right-click context menu"""
        item = self.sidebar.itemAt(position)
        if item:
            menu = QMenu(self)
            
            data = item.data(0, Qt.ItemDataRole.UserRole)
            if data and data.startswith("note:"):
                menu.addAction("📄 Rename Note", self.rename_current_item)
                menu.addAction("🗑️  Delete Note", self.delete_current_item)
            elif data and data.startswith("folder:"):
                menu.addAction("📁 Rename Folder", self.rename_current_item)
                menu.addAction("🗑️  Delete Folder", self.delete_current_item)
            
            menu.exec(self.sidebar.mapToGlobal(position))
    
    def rename_current_item(self):
        """Rename selected item"""
        current_item = self.sidebar.currentItem()
        if current_item:
            self.sidebar.editItem(current_item, 0)
    
    def on_item_renamed(self, item: QTreeWidgetItem, column: int):
        """Handle rename completion"""
        if self.is_renaming:
            return
        
        data = item.data(0, Qt.ItemDataRole.UserRole)
        new_name = item.text(0).strip()
        
        if new_name and data:
            try:
                if data.startswith("note:"):
                    note_id = int(data.split(":")[1])
                    note = self.db_manager.get_note(note_id)  # ← USE SELF.DB_MANAGER
                    if note:
                        note.title = new_name.replace("📄 ", "").replace("  ", "")
                        self.db_manager.update_note(note)        # ← USE SELF.DB_MANAGER
                
                elif data.startswith("folder:"):
                    folder_id = int(data.split(":")[1])
                    self.load_hierarchy()  # Refresh after rename
                
                self.load_hierarchy()
                self.statusBar().showMessage(f"✅ Renamed: {new_name}")
                
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Rename failed: {str(e)}")
    
    def on_item_clicked(self, item: QTreeWidgetItem):
        """Single click"""
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if data and data.startswith("note:"):
            note_id = int(data.split(":")[1])
            self.load_note(note_id)
    
    def on_item_double_clicked(self, item: QTreeWidgetItem):
        """Double click folder"""
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if data and data.startswith("folder:"):
            if item.isExpanded():
                self.sidebar.collapseItem(item)
            else:
                self.sidebar.expandItem(item)
    
    def load_note(self, note_id: int):
        """Load note"""
        note = self.db_manager.get_note(note_id)  # ← USE SELF.DB_MANAGER
        if note:
            self.current_note = note
            self.editor.setText(note.content)
            self.status_label.setText(f"📄 {note.title} ({len(note.content)} chars)")
    
    def create_new_note(self):
        """New note"""
        note = Note(title="Untitled", content="# New Note\n\nStart writing...")
        note.id = self.db_manager.create_note(note)  # ← USE SELF.DB_MANAGER
        self.load_note(note.id)
        self.load_hierarchy()
    
    def delete_current_item(self):
        """Delete selected item"""
        item = self.sidebar.currentItem()
        if item and QMessageBox.question(self, "Confirm Delete", "Delete this item?") == QMessageBox.DialogCode.Yes:
            data = item.data(0, Qt.ItemDataRole.UserRole)
            if data.startswith("note:"):
                note_id = int(data.split(":")[1])
                self.db_manager.delete_note(note_id)  # ← USE SELF.DB_MANAGER
            elif data.startswith("folder:"):
                folder_id = int(data.split(":")[1])
                self.db_manager.delete_folder(folder_id)  # ← USE SELF.DB_MANAGER
            
            self.load_hierarchy()
    
    def save_current_note(self):
        """Manual save"""
        if self.current_note:
            self.current_note.content = self.editor.toPlainText()
            self.db_manager.update_note(self.current_note)  # ← USE SELF.DB_MANAGER
            self.status_label.setText("💾 Saved")
            QTimer.singleShot(800, lambda: self.status_label.setText("Ready"))
    
    def auto_save(self):
        """Auto-save"""
        if self.current_note and self.editor.document().isModified():
            self.save_current_note()
    
    def on_editor_changed(self):
        """Editor changed"""
        if self.current_note:
            self.status_label.setText("⏳ Unsaved")
    
    def focus_search(self):
        """Focus search"""
        self.search_input.setFocus()
        self.search_input.selectAll()
    
    def closeEvent(self, event):
        """Save on close"""
        if self.current_note:
            self.save_current_note()
        # Database closed by main.py
        event.accept()
