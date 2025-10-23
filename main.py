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
    """Phase 6: Nested folder sample data"""
    print("🗄️  Creating Phase 6 sample data...")
    
    # Clear existing
    try:
        db._conn.execute("DELETE FROM notes")
        db._conn.execute("DELETE FROM folders")
        db._conn.commit()
    except:
        pass
    
    # Create nested structure for drag/drop testing
    projects = db.create_folder(Folder(name="💻 Projects"))
    db.create_note(Note(title="Frontend", content="# Frontend Tasks\nDrag me!", folder_id=projects))
    db.create_note(Note(title="Backend", content="# Backend API\nTry dragging!", folder_id=projects))
    
    frontend = db.create_folder(Folder(name="🌐 Frontend", parent_id=projects))
    db.create_note(Note(title="React Components", content="# React Components\nDouble-click folders!", folder_id=frontend))
    
    docs = db.create_folder(Folder(name="📚 Documentation"))
    db.create_note(Note(title="Phase 6 Guide", content="""# Drag & Drop Guide 🎉

## Features:
• **Drag notes** between folders
• **Drag folders** into other folders  
• **Right-click** → New Folder
• **F2** → Rename
• **Right-click** → Delete

## Try:
1. Drag "Frontend" into "Projects"
2. Right-click → New Folder
3. Drag notes around! 👇""", folder_id=docs))
    
    print("✅ Nested folders + drag/drop samples ready!")

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
    
    # Create and show main window - PASS DATABASE!
    from main_window import MainWindow
    window = MainWindow(db_manager)  # ← PASS DB INSTANCE
    window.showMaximized()  # VSCode-style start
    
    print("🎉 PHASE 4 COMPLETE!")
    print("✅ VSCode-style resizable layout")
    print("✅ Right-click rename + F2")
    print("✅ 100% SAFE database (no globals!)")
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
