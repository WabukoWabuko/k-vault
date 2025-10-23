#!/usr/bin/env python3
"""
K-Vault Database Utilities
SQLite database with FTS5 for instant fuzzy search
"""
import sqlite3
import os
import json
from pathlib import Path
from typing import List, Optional, Dict, Any

class Database:
    """Main database handler for K-Vault"""
    
    def __init__(self, db_path: str = None):
        """Initialize database connection"""
        if db_path is None:
            # Store in user app data folder
            app_data = Path.home() / ".kvault"
            app_data.mkdir(exist_ok=True)
            self.db_path = app_data / "kvault.db"
        else:
            self.db_path = Path(db_path)
        
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = None
        self.connect()
        self.init_schema()
    
    def connect(self):
        """Connect to SQLite database"""
        self._conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self._conn.execute("PRAGMA foreign_keys = ON")
        self._conn.execute("PRAGMA journal_mode = WAL")
        self._conn.execute("PRAGMA synchronous = NORMAL")
    
    def init_schema(self):
        """Create tables and FTS index"""
        schema = """
        -- Folders table (hierarchical)
        CREATE TABLE IF NOT EXISTS folders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            parent_id INTEGER DEFAULT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (parent_id) REFERENCES folders(id) ON DELETE CASCADE
        );
        
        -- Notes table
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            folder_id INTEGER DEFAULT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (folder_id) REFERENCES folders(id) ON DELETE SET NULL
        );
        
        -- FTS5 virtual table for instant search
        CREATE VIRTUAL TABLE IF NOT EXISTS notes_fts USING fts5(
            title, 
            content, 
            content='notes',
            content_rowid='rowid'
        );
        
        -- Trigger to keep FTS in sync
        CREATE TRIGGER IF NOT EXISTS notes_ai AFTER INSERT ON notes BEGIN
            INSERT INTO notes_fts(rowid, title, content) VALUES (new.rowid, new.title, new.content);
        END;
        CREATE TRIGGER IF NOT EXISTS notes_ad AFTER DELETE ON notes BEGIN
            INSERT INTO notes_fts(notes_fts, rowid, title, content) 
            VALUES('delete', old.rowid, old.title, old.content);
        END;
        CREATE TRIGGER IF NOT EXISTS notes_au AFTER UPDATE ON notes BEGIN
            INSERT INTO notes_fts(notes_fts, rowid, title, content) 
            VALUES('delete', old.rowid, old.title, old.content);
            INSERT INTO notes_fts(rowid, title, content) VALUES (new.rowid, new.title, new.content);
        END;
        """
        self._conn.executescript(schema)
        self._conn.commit()
    
    def create_folder(self, name: str, parent_id: Optional[int] = None) -> int:
        """Create new folder"""
        cursor = self._conn.execute(
            "INSERT INTO folders (name, parent_id) VALUES (?, ?)",
            (name, parent_id)
        )
        self._conn.commit()
        return cursor.lastrowid
    
    def get_folders(self, parent_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get folders (recursive hierarchy)"""
        query = "SELECT * FROM folders WHERE parent_id = ? OR (parent_id IS NULL AND ? IS NULL) ORDER BY name"
        cursor = self._conn.execute(query, (parent_id, parent_id))
        return [{"id": row[0], "name": row[1], "parent_id": row[2]} for row in cursor.fetchall()]
    
    def create_note(self, title: str, content: str = "", folder_id: Optional[int] = None) -> int:
        """Create new note"""
        cursor = self._conn.execute(
            "INSERT INTO notes (title, content, folder_id) VALUES (?, ?, ?)",
            (title, content, folder_id)
        )
        self._conn.commit()
        return cursor.lastrowid
    
    def get_note(self, note_id: int) -> Optional[Dict[str, Any]]:
        """Get single note"""
        cursor = self._conn.execute(
            "SELECT * FROM notes WHERE id = ?", (note_id,)
        )
        row = cursor.fetchone()
        if row:
            return {
                "id": row[0], "title": row[1], "content": row[2], 
                "folder_id": row[3], "created_at": row[4], "updated_at": row[5]
            }
        return None
    
    def update_note(self, note_id: int, title: str, content: str):
        """Update note"""
        self._conn.execute(
            "UPDATE notes SET title = ?, content = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (title, content, note_id)
        )
        self._conn.commit()
    
    def delete_note(self, note_id: int):
        """Delete note"""
        self._conn.execute("DELETE FROM notes WHERE id = ?", (note_id,))
        self._conn.commit()
    
    def get_notes(self, folder_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get all notes in folder or root"""
        where_clause = "folder_id = ?" if folder_id else "folder_id IS NULL"
        cursor = self._conn.execute(f"SELECT * FROM notes WHERE {where_clause} ORDER BY title", (folder_id,) if folder_id else ())
        return [{"id": row[0], "title": row[1], "content": row[2], "folder_id": row[3]} for row in cursor.fetchall()]
    
    def search_notes(self, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Fuzzy search using FTS5"""
        cursor = self._conn.execute(
            "SELECT notes.*, rank FROM notes_fts() "
            "WHERE notes_fts MATCH ? ORDER BY rank LIMIT ?",
            (query + "*", limit)
        )
        return [{"id": row[0], "title": row[1], "content": row[2], "rank": row[-1]} for row in cursor.fetchall()]
    
    def close(self):
        """Close database connection"""
        if self._conn:
            self._conn.commit()
            self._conn.close()

# Global database instance
db = Database()
