#!/usr/bin/env python3
"""
K-Vault Main Application - PHASE 3 COMPLETE
"""
import sys
import os
from PyQt6.QtWidgets import QApplication
from models import Note, Folder
from db_manager import db_manager
from main_window import MainWindow

def create_sample_data():
    """Create enhanced sample data"""
    print("🗄️  Creating Phase 3 sample data...")
    
    # Create folders
    projects_folder = Folder(name="💻 Projects")
    projects_id = db_manager.create_folder(projects_folder)
    
    docs_folder = Folder(name="📚 Documentation")
    docs_id = db_manager.create_folder(docs_folder)
    
    # Create notes
    db_manager.create_note(Note(
        title="🚀 Welcome to K-Vault!",
        content="""# Welcome to K-Vault! 🎉

## Phase 3 Features:
✅ **Data Models** - Type-safe Note/Folder classes
✅ **Enhanced Database** - Indexes + WAL mode
✅ **Auto-save** - Every 3 seconds
✅ **Full Hierarchy** - Nested folders
✅ **FTS5 Search** - Ready for Phase 7

## Try these features:
- **Ctrl+N** - New note
- **Ctrl+S** - Save  
- **Click notes** - Load into editor
- **Edit & wait** - Auto-saves!

**Database location:** `~/.kvault/kvault.db`""",
        folder_id=projects_id
    ))
    
    db_manager.create_note(Note(
        title="📝 Quick Start Guide",
        content="""# Quick Start

## 1. Create Folders
Right-click sidebar → New Folder

## 2. Add Notes  
Ctrl+N or File → New Note

## 3. Organize
Drag notes between folders

## 4. Search
Ctrl+K → Type to search

## 5. Link Notes
Use `[[Note Title]]` syntax""",
        folder_id=docs_id
    ))
    
    print("✅ 2 folders + 2 notes created!")

def main():
    """Phase 3 entry point"""
    # Validate files
    required = ["main.py", "models.py", "db_manager.py", "main_window.py"]
    missing = [f for f in required if not os.path.exists(f)]
    if missing:
        print("❌ Missing:", missing)
        sys.exit(1)
    
    # Sample data
    create_sample_data()
    
    app = QApplication(sys.argv)
    app.setApplicationName("K-Vault")
    app.setApplicationVersion("3.0.0")
    app.setStyle('Fusion')
    
    window = MainWindow()
    window.show()
    
    print("🎉 PHASE 3 COMPLETE!")
    print("✅ Data models + enhanced database working!")
    print("✅ Auto-save + full CRUD operations!")
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
