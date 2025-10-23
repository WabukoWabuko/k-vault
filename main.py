#!/usr/bin/env python3
"""
K-Vault - PHASE 4 COMPLETE (VSCode Style)
"""
import sys
import os
from PyQt6.QtWidgets import QApplication
from db_manager import db_manager
from main_window import MainWindow

def create_sample_data():
    """Phase 4 enhanced sample data"""
    print("🗄️  Creating VSCode-style sample data...")
    
    # Clear existing
    db_manager._conn.execute("DELETE FROM notes")
    db_manager._conn.execute("DELETE FROM folders")
    db_manager._conn.commit()
    
    # Create nested folders
    projects = db_manager.create_folder(Folder(name="💻 Projects"))
    db_manager.create_note(Note(title="My First Project", content="# Project Notes\n\nStart here...", folder_id=projects))
    
    docs = db_manager.create_folder(Folder(name="📚 Docs"))
    db_manager.create_note(Note(title="Getting Started", content="# Welcome!\n\nRight-click to rename\nF2 = Rename\nMaximize to see full layout", folder_id=docs))
    
    print("✅ 2 folders + 2 notes ready!")

def main():
    """Phase 4 entry"""
    required = ["main.py", "models.py", "db_manager.py", "main_window.py"]
    missing = [f for f in required if not os.path.exists(f)]
    if missing:
        print("❌ Missing:", missing)
        sys.exit(1)
    
    create_sample_data()
    
    app = QApplication(sys.argv)
    app.setApplicationName("K-Vault")
    app.setApplicationVersion("4.0.0")
    app.setStyle('Fusion')
    
    window = MainWindow()
    window.showMaximized()  # Start maximized like VSCode
    
    print("🎉 PHASE 4 COMPLETE!")
    print("✅ VSCode-style resizable layout")
    print("✅ Right-click rename + F2")
    print("✅ Maximize fills screen perfectly")
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
