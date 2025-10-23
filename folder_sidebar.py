#!/usr/bin/env python3
"""
K-Vault Drag & Drop Folder Sidebar (FIXED)
Full hierarchical drag/drop + context menu
"""
from typing import Optional, List
from PyQt6.QtWidgets import (QTreeWidget, QTreeWidgetItem, QMenu, QMessageBox, 
                             QInputDialog, QSizePolicy)
from PyQt6.QtCore import Qt, pyqtSignal, QMimeData
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QDrag
from models import Note, Folder
from db_manager import DatabaseManager

class FolderSidebar(QTreeWidget):
    """Drag & drop enabled folder sidebar"""
    note_selected = pyqtSignal(int)
    folder_selected = pyqtSignal(int)
    item_renamed = pyqtSignal(str, str)  # old_name, new_name
    item_deleted = pyqtSignal(str)
    
    def __init__(self, db_manager: DatabaseManager):
        super().__init__()
        self.db_manager = db_manager
        self.setHeaderLabel("📁 Folders & Notes")
        self.setMinimumWidth(280)
        self.setMaximumWidth(500)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QTreeWidget.DragDropMode.InternalMove)
        self.setAlternatingRowColors(True)
        self.setup_tree()
    
    def setup_tree(self):
        """Setup tree properties for drag/drop"""
        self.setSelectionMode(QTreeWidget.SelectionMode.SingleSelection)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
    
    def load_hierarchy(self):
        """Load complete folder hierarchy"""
        self.clear()
        root_folders = self.db_manager.get_full_hierarchy()
        unassigned_notes = self.db_manager.get_notes()
        
        for folder in root_folders:
            self._add_folder_to_tree(folder)
        
        if unassigned_notes:
            unassigned_item = QTreeWidgetItem(["📋 Unassigned Notes"])
            unassigned_item.setData(0, Qt.ItemDataRole.UserRole, "root:unassigned")
            unassigned_item.setFlags(Qt.ItemFlag.ItemIsDropEnabled)
            self.addTopLevelItem(unassigned_item)
            for note in unassigned_notes:
                self._add_note_to_tree(note, unassigned_item)
    
    def _add_folder_to_tree(self, folder: Folder, parent_item: Optional[QTreeWidgetItem] = None):
        """Recursively add folder"""
        if parent_item:
            item = QTreeWidgetItem([f"  📁 {folder.name}"])
            parent_item.addChild(item)
        else:
            item = QTreeWidgetItem([f"📁 {folder.name}"])
            self.addTopLevelItem(item)
        
        item.setData(0, Qt.ItemDataRole.UserRole, f"folder:{folder.id}")
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable | Qt.ItemFlag.ItemIsDragEnabled | Qt.ItemFlag.ItemIsDropEnabled)
        
        # Add notes
        for note in folder.notes:
            self._add_note_to_tree(note, item)
        
        # Add children folders
        for child in folder.children:
            self._add_folder_to_tree(child, item)
    
    def _add_note_to_tree(self, note: Note, parent_item: QTreeWidgetItem):
        """Add single note"""
        item = QTreeWidgetItem([f"  📄 {note.title}"])
        item.setData(0, Qt.ItemDataRole.UserRole, f"note:{note.id}")
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable | Qt.ItemFlag.ItemIsDragEnabled)
        parent_item.addChild(item)
    
    def contextMenuEvent(self, event):
        """Right-click context menu"""
        item = self.itemAt(event.pos())
        if item:
            menu = QMenu(self)
            data = item.data(0, Qt.ItemDataRole.UserRole)
            
            if data and data.startswith("note:"):
                menu.addAction("📄 Rename Note", self.rename_item)
                menu.addAction("🗑️  Delete Note", lambda: self.delete_item(item))
            elif data and data.startswith("folder:"):
                menu.addAction("📁 New Folder", self.create_folder_dialog)
                menu.addAction("📁 Rename Folder", self.rename_item)
                menu.addAction("🗑️  Delete Folder", lambda: self.delete_item(item))
            else:
                menu.addAction("📁 New Folder", self.create_folder_dialog)
            
            menu.exec(event.globalPos())
    
    def create_folder_dialog(self):
        """Create new folder dialog"""
        parent_item = self.currentItem()
        parent_id = None
        
        if parent_item:
            data = parent_item.data(0, Qt.ItemDataRole.UserRole)
            if data and data.startswith("folder:"):
                parent_id = int(data.split(":")[1])
        
        name, ok = QInputDialog.getText(self, "New Folder", "Folder name:")
        if ok and name.strip():
            folder = Folder(name=name.strip())
            folder.parent_id = parent_id
            self.db_manager.create_folder(folder)
            self.load_hierarchy()
    
    def rename_item(self):
        """Start rename on current item"""
        current_item = self.currentItem()
        if current_item:
            self.editItem(current_item, 0)
    
        def itemChanged(self, item: QTreeWidgetItem, column: int):
            """Handle rename completion - INTERNAL"""
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
                    print(f"✅ Renamed: {new_name}")  # Internal feedback
                    
                except Exception as e:
                    print(f"Rename error: {e}")
    
    def delete_item(self, item: QTreeWidgetItem):
        """Delete item with confirmation"""
        data = item.data(0, Qt.ItemDataRole.UserRole)
        message = "Delete this note?" if data.startswith("note:") else "Delete this folder and all contents?"
        
        if QMessageBox.question(self, "Confirm Delete", message) == QMessageBox.DialogCode.Yes:
            try:
                if data.startswith("note:"):
                    note_id = int(data.split(":")[1])
                    self.db_manager.delete_note(note_id)
                elif data.startswith("folder:"):
                    folder_id = int(data.split(":")[1])
                    self.db_manager.delete_folder(folder_id)
                
                self.load_hierarchy()
                self.item_deleted.emit(data)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Delete failed: {str(e)}")
    
    # ===== DRAG & DROP (SIMPLIFIED) =====
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Accept drag events"""
        if event.mimeData().hasText():
            event.acceptProposedAction()
        else:
            event.ignore()
    
    def dragMoveEvent(self, event):
        """Handle drag over"""
        event.acceptProposedAction()
    
    def dropEvent(self, event: QDropEvent):
        """Handle drop"""
        if event.mimeData().hasText():
            source_data = event.mimeData().text()
            target_item = self.itemAt(event.pos())
            
            if target_item and source_data:
                self.handle_drop(source_data, target_item)
                event.acceptProposedAction()
            else:
                event.ignore()
        else:
            event.ignore()
    
    def startDrag(self, supportedActions):
        """Start drag operation"""
        items = self.selectedItems()
        if items:
            item = items[0]
            data = item.data(0, Qt.ItemDataRole.UserRole)
            
            drag = QDrag(self)
            mime = QMimeData()
            mime.setText(data)
            drag.setMimeData(mime)
            drag.exec(Qt.DropAction.MoveAction)
    
    def handle_drop(self, source_data: str, target_item: QTreeWidgetItem):
        """Process drop operation"""
        target_data = target_item.data(0, Qt.ItemDataRole.UserRole)
        
        try:
            if source_data.startswith("note:") and target_data.startswith("folder:"):
                # Move note to folder
                note_id = int(source_data.split(":")[1])
                folder_id = int(target_data.split(":")[1])
                self.db_manager.move_note_to_folder(note_id, folder_id)
                
            elif source_data.startswith("folder:") and target_data.startswith("folder:"):
                # Move folder to folder (as child)
                source_folder_id = int(source_data.split(":")[1])
                target_folder_id = int(target_data.split(":")[1])
                self.db_manager.move_folder(source_folder_id, target_folder_id)
            
            elif source_data.startswith("note:") and (target_data == "root:unassigned" or not target_data):
                # Move note to unassigned
                note_id = int(source_data.split(":")[1])
                self.db_manager.move_note_to_folder(note_id, None)
            
            self.load_hierarchy()
        except Exception as e:
            print(f"Drop error: {e}")
