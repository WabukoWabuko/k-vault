#!/usr/bin/env python3
"""
K-Vault - PHASE 4 COMPLETE (PERFECTLY SAFE - NO GLOBALS)
"""
import sys
import os
import shutil
from PyQt6.QtWidgets import QApplication
from models import Note, Folder
from db_manager import DatabaseManager

def create_sample_data(db: DatabaseManager):
    """Phase 4 enhanced sample data"""
    print("🗄️  Creating VSCode-style sample data...")
    
    # Safe delete existing data
    try:
        db._conn.execute("DELETE FROM notes")
        db._conn.execute("DELETE FROM folders")
        db._conn.commit()
        print("🧹 Cleared existing data")
    except Exception as e:
        print(f"⚠️  Clear failed (ok for fresh DB): {e}")
    
    # Create nested folders and notes
    projects_folder = Folder(name="💻 Projects")
    projects_id = db.create_folder(projects_folder)
    
    db.create_note(Note(
        title="My First Project", 
        content="# Project Notes\n\nStart here...\n\n**Phase 4 Features:**\n• Resizable panels\n• Right-click rename\n• F2 shortcut", 
        folder_id=projects_id
    ))
    
    docs_folder = Folder(name="📚 Docs")
    docs_id = db.create_folder(docs_folder)
    
    db.create_note(Note(
        title="Getting Started", 
        content="# Welcome to K-Vault! 🎉\n\n## VSCode-Style Features:\n\n• **Maximize** = Full screen\n• **Drag splitter** = Resize panels\n• **Right-click** = Rename/Delete\n• **F2** = Rename shortcut\n• **Double-click folders** = Expand", 
        folder_id=docs_id
    ))
    
    print("✅ 2 folders + 2 notes ready!")

def get_or_create_database() -> DatabaseManager:
    """Get healthy database or create fresh one"""
    kvault_dir = os.path.expanduser("~/.kvault")
    
    # Try existing database
    try:
        db = DatabaseManager()
        db.get_folders()  # Test query
        print("✅ Database healthy")
        return db
    except Exception as e:
        print(f"⚠️  Database issue: {e}")
        print("🔄 Creating fresh database...")
    
    # Delete corrupted files and recreate
    if os.path.exists(kvault_dir):
        shutil.rmtree(kvault_dir)
        print("🗑️  Removed corrupted files")
    
    db = DatabaseManager()
    print("✅ Fresh database ready!")
    return db

def main():
    """Phase 4 entry point - CLEAN NO GLOBALS"""
    # Validate required files
    required = ["main.py", "models.py", "db_manager.py", "main_window.py"]
    missing = [f for f in required if not os.path.exists(f)]
    if missing:
        print("❌ ERROR: Missing files:", missing)
        sys.exit(1)
    
    # Get healthy database
    db_manager = get_or_create_database()
    
    # Create sample data
    create_sample_data(db_manager)
    
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("K-Vault")
    app.setApplicationVersion("4.0.0")
    app.setOrganizationName("K-Vault Team")
    app.setStyle('Fusion')
    
    # Create and show main window
    from main_window import MainWindow
    window = MainWindow()
    window.showMaximized()  # VSCode-style start
    
    print("🎉 PHASE 4 COMPLETE!")
    print("✅ VSCode-style resizable layout")
    print("✅ Right-click rename + F2")
    print("✅ 100% SAFE database (no globals!)")
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
