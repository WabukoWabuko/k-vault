#!/usr/bin/env python3
"""
K-Vault Main Application Entry Point
Cross-platform Knowledge Organizer - PHASE 2
"""
import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

# Import our modules (all in ROOT)
from main_window import MainWindow
from db_utils import db

def main():
    """Main application entry point"""
    # Validate project structure
    required_files = ["main.py", "main_window.py", "db_utils.py"]
    missing = [f for f in required_files if not os.path.exists(f)]
    if missing:
        print("❌ ERROR: Missing files:", missing)
        sys.exit(1)
    
    # Create sample data
    print("🗄️  Creating sample data...")
    folder_id = db.create_folder("Getting Started")
    db.create_note("Welcome to K-Vault!", 
                   "# Welcome! 🚀\n\nThis is your first note.\n\n**Features:**\n- Rich Markdown\n- Instant search\n- Folder hierarchy", 
                   folder_id)
    db.create_note("Quick Start", "Create folders → Add notes → Start organizing!", folder_id)
    print("✅ Sample data created!")
    
    app = QApplication(sys.argv)
    app.setApplicationName("K-Vault")
    app.setApplicationVersion("2.0.0")
    app.setOrganizationName("K-Vault Team")
    
    # Modern styling
    app.setStyle('Fusion')
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    print("🎉 K-Vault Phase 2 Complete!")
    print("✅ Main window + SQLite database working!")
    print("✅ Sample data loaded - try clicking notes!")
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
