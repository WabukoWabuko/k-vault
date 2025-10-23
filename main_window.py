#!/usr/bin/env python3
"""
K-Vault Main Window (Phase 5 - Rich Markdown Editor)
"""
from typing import Optional
from PyQt6.QtWidgets import (QMainWindow, QSplitter, QTreeWidget, QTreeWidgetItem, 
                             QVBoxLayout, QWidget, QHBoxLayout, QLabel, QMessageBox, QMenu, 
                             QToolBar, QLineEdit)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QKeySequence, QShortcut, QAction
import sys

from models import Note, Folder
from db_manager import DatabaseManager
from markdown_editor import MarkdownEditor

class MainWindow(QMainWindow):
    """Main window with rich Markdown editor"""
    
    def __init__(self, db_manager: DatabaseManager):
        super().__init__()
        self.db_manager = db_manager
        self.current_note: Optional[Note] = None
        self.is_renaming = False
        
        self.setup_ui()
        self.load_hierarchy()
        self.connect_signals()
        self.statusBar().showMessage("🚀 K-Vault Phase 5 - Rich Markdown Editor Ready!")
    
    def setup_ui(self):
        """VSCode-style layout with rich editor"""
        self.setWindowTitle("K-Vault - Phase 5 (Rich Markdown)")
        self.resize(1600, 1000)
        self.setMinimumSize(1000, 700)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout = QHBoxLayout(central_widget)
        main_layout.addWidget(main_splitter)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Sidebar (unchanged)
        self.sidebar = QTreeWidget()
        self.sidebar.setHeaderLabel("📁 Folders & Notes")
        self.sidebar.setMinimumWidth(280)
        self.sidebar.setMaximumWidth(500)
        self.sidebar.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        main_splitter.addWidget(self.sidebar)
        
        # RICH EDITOR AREA
        self.markdown_editor = MarkdownEditor()
        main_splitter.addWidget(self.markdown_editor)
        main_splitter.setSizes([320, 1280])
        main_splitter.setCollapsible(0, False)
        
        # Search bar (above editor)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Ctrl+K - Instant Search...")
        self.search_input.setMinimumHeight(36)
        main_splitter.insertWidget(1, self.search_input)
        
        self.setup_menu()
    
    def setup_menu(self):
        """Menu bar"""
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
        """Load folder hierarchy"""
        self.sidebar.clear()
        root_folders = self.db_manager.get_full_hierarchy()
        unassigned_notes = self.db_manager.get_notes()
        
        for folder in root_folders:
            self._add_folder_to_tree(folder)
        
        if unassigned_notes:
            unassigned_item = QTreeWidgetItem(["📋 Unassigned Notes"])
            unassigned_item.setData(0, Qt.ItemDataRole.UserRole, "root:unassigned")
            self.sidebar.addTopLevelItem(unassigned_item)
            for note in unassigned_notes:
                self._add_note_to_tree(note, unassigned_item)
    
    def _add_folder_to_tree(self, folder: Folder, parent_item: Optional[QTreeWidgetItem] = None):
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
        item = QTreeWidgetItem([f"  📄 {note.title}"])
        item.setData(0, Qt.ItemDataRole.UserRole, f"note:{note.id}")
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
        parent_item.addChild(item)
    
    def connect_signals(self):
        """Connect signals"""
        self.sidebar.itemClicked.connect(self.on_item_clicked)
        self.sidebar.itemDoubleClicked.connect(self.on_item_double_clicked)
        self.sidebar.customContextMenuRequested.connect(self.show_context_menu)
        self.sidebar.itemChanged.connect(self.on_item_renamed)
        
        # Rich editor signals
        self.markdown_editor.content_changed.connect(self.on_note_content_changed)
        self.markdown_editor.note_saved.connect(self.save_current_note)
        
        # Shortcuts
        QShortcut(QKeySequence("Ctrl+K"), self).activated.connect(self.focus_search)
        QShortcut(QKeySequence("F2"), self).activated.connect(self.rename_current_item)
    
    def on_item_clicked(self, item: QTreeWidgetItem):
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if data and data.startswith("note:"):
            note_id = int(data.split(":")[1])
            self.load_note(note_id)
    
    def on_item_double_clicked(self, item: QTreeWidgetItem):
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if data and data.startswith("folder:"):
            if item.isExpanded():
                self.sidebar.collapseItem(item)
            else:
                self.sidebar.expandItem(item)
    
    def load_note(self, note_id: int):
        """Load note into rich editor"""
        note = self.db_manager.get_note(note_id)
        if note:
            self.current_note = note
            self.markdown_editor.set_content(note.content)
            self.statusBar().showMessage(f"📄 {note.title} - Rich Markdown Editor")
    
    def create_new_note(self):
        """Create new note"""
        note = Note(title="Untitled", content="# New Note\n\nStart writing with **rich formatting**!")
        note.id = self.db_manager.create_note(note)
        self.load_note(note.id)
        self.load_hierarchy()
    
    def save_current_note(self):
        """Save note"""
        if self.current_note:
            self.current_note.content = self.markdown_editor.get_content()
            self.db_manager.update_note(self.current_note)
            self.statusBar().showMessage("💾 Saved - Rich Markdown")
    
    def on_note_content_changed(self, content: str):
        """Auto-save on content change"""
        if self.current_note:
            self.current_note.content = content
            QTimer.singleShot(2000, self.save_current_note)  # Auto-save after 2s
    
    # Context menu + rename (unchanged from Phase 4)
    def show_context_menu(self, position):
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
        current_item = self.sidebar.currentItem()
        if current_item:
            self.sidebar.editItem(current_item, 0)
    
    def on_item_renamed(self, item: QTreeWidgetItem, column: int):
        if self.is_renaming:
            return
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
                self.load_hierarchy()
                self.statusBar().showMessage(f"✅ Renamed: {new_name}")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Rename failed: {str(e)}")
    
    def delete_current_item(self):
        item = self.sidebar.currentItem()
        if item and QMessageBox.question(self, "Confirm Delete", "Delete this item?") == QMessageBox.DialogCode.Yes:
            data = item.data(0, Qt.ItemDataRole.UserRole)
            if data.startswith("note:"):
                note_id = int(data.split(":")[1])
                self.db_manager.delete_note(note_id)
            elif data.startswith("folder:"):
                folder_id = int(data.split(":")[1])
                self.db_manager.delete_folder(folder_id)
            self.load_hierarchy()
    
    def focus_search(self):
        self.search_input.setFocus()
        self.search_input.selectAll()
    
    def closeEvent(self, event):
        if self.current_note:
            self.save_current_note()
        event.accept()
