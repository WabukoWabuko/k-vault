#!/usr/bin/env python3
"""
K-Vault Database Manager
Enhanced database layer with models integration
"""
import sqlite3
import os
from pathlib import Path
from typing import List, Optional, Dict, Any
from models import Folder, Note, SearchResult, ItemType

class DatabaseManager:
    """Enhanced database manager with full CRUD and hierarchy"""
    
    def __init__(self, db_path: str = None):
        """Initialize with models support"""
        if db_path is None:
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
        """Connect with optimized settings + integrity check"""
        self._conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA foreign_keys = ON")
        self._conn.execute("PRAGMA journal_mode = WAL")
        self._conn.execute("PRAGMA synchronous = NORMAL")
        self._conn.execute("PRAGMA cache_size = 10000")
        
        # Integrity check
        if not self.integrity_check():
            raise Exception("Database corrupted - will be recreated")
    
    def init_schema(self):
        """Enhanced schema with indexes"""
        schema = """
        -- Drop old FTS if exists (for migration)
        DROP TABLE IF EXISTS notes_fts;
        
        -- Folders table
        CREATE TABLE IF NOT EXISTS folders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL CHECK (name <> ''),
            parent_id INTEGER DEFAULT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(parent_id, name),
            FOREIGN KEY (parent_id) REFERENCES folders(id) ON DELETE CASCADE
        );
        
        CREATE INDEX IF NOT EXISTS idx_folders_parent ON folders(parent_id);
        CREATE INDEX IF NOT EXISTS idx_folders_name ON folders(name);
        
        -- Notes table
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL CHECK (title <> ''),
            content TEXT NOT NULL,
            folder_id INTEGER DEFAULT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(folder_id, title),
            FOREIGN KEY (folder_id) REFERENCES folders(id) ON DELETE SET NULL
        );
        
        CREATE INDEX IF NOT EXISTS idx_notes_folder ON notes(folder_id);
        CREATE INDEX IF NOT EXISTS idx_notes_title ON notes(title);
        
        -- FTS5 for instant search (enhanced)
        CREATE VIRTUAL TABLE IF NOT EXISTS notes_fts USING fts5(
            title, content, 
            content='notes',
            content_rowid='rowid',
            prefix='2 3 4 5'
        );
        
        -- FTS Triggers
        DROP TRIGGER IF EXISTS notes_ai;
        DROP TRIGGER IF EXISTS notes_ad;
        DROP TRIGGER IF EXISTS notes_au;
        
        CREATE TRIGGER notes_ai AFTER INSERT ON notes BEGIN
            INSERT INTO notes_fts(rowid, title, content) 
            VALUES (new.rowid, new.title, new.content);
        END;
        
        CREATE TRIGGER notes_ad AFTER DELETE ON notes BEGIN
            INSERT INTO notes_fts(notes_fts, rowid, title, content) 
            VALUES('delete', old.rowid, old.title, old.content);
        END;
        
        CREATE TRIGGER notes_au AFTER UPDATE ON notes BEGIN
            INSERT INTO notes_fts(notes_fts, rowid, title, content) 
            VALUES('delete', old.rowid, old.title, old.content);
            INSERT INTO notes_fts(rowid, title, content) 
            VALUES (new.rowid, new.title, new.content);
        END;
        """
        self._conn.executescript(schema)
        self._conn.commit()
    
    # ===== FOLDER OPERATIONS =====
    def create_folder(self, folder: Folder) -> int:
        """Create folder with model validation"""
        cursor = self._conn.execute(
            "INSERT INTO folders (name, parent_id) VALUES (?, ?)",
            (folder.name, folder.parent_id)
        )
        folder.id = cursor.lastrowid
        self._conn.commit()
        return folder.id
    
    def get_folder(self, folder_id: int) -> Optional[Folder]:
        """Get folder by ID"""
        cursor = self._conn.execute(
            "SELECT * FROM folders WHERE id = ?", (folder_id,)
        )
        row = cursor.fetchone()
        return Folder.from_dict(dict(row)) if row else None
    
    def get_folders(self, parent_id: Optional[int] = None) -> List[Folder]:
        """Get folders with hierarchy"""
        query = """
            SELECT * FROM folders 
            WHERE parent_id = ? OR (parent_id IS NULL AND ? IS NULL)
            ORDER BY name
        """
        cursor = self._conn.execute(query, (parent_id, parent_id))
        return [Folder.from_dict(dict(row)) for row in cursor.fetchall()]
    
    def delete_folder(self, folder_id: int, recursive: bool = True):
        """Delete folder and contents"""
        if recursive:
            self._conn.execute("DELETE FROM folders WHERE id = ? OR parent_id = ?", (folder_id, folder_id))
        else:
            self._conn.execute("DELETE FROM folders WHERE id = ?", (folder_id,))
        self._conn.commit()
    
        # ===== DRAG & DROP OPERATIONS =====
    def move_note_to_folder(self, note_id: int, target_folder_id: Optional[int]):
        """Move note to different folder"""
        self._conn.execute(
            "UPDATE notes SET folder_id = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (target_folder_id, note_id)
        )
        self._conn.commit()
    
    def move_folder(self, folder_id: int, target_parent_id: Optional[int]):
        """Move folder to different parent"""
        self._conn.execute(
            "UPDATE folders SET parent_id = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (target_parent_id, folder_id)
        )
        self._conn.commit()
    
    def get_note_parents(self, note_id: int) -> List[int]:
        """Get all parent folder IDs for a note"""
        note = self.get_note(note_id)
        parents = []
        folder_id = note.folder_id
        while folder_id:
            parents.append(folder_id)
            folder = self.get_folder(folder_id)
            folder_id = folder.parent_id
        return parents
    
    # ===== NOTE OPERATIONS =====
    def create_note(self, note: Note) -> int:
        """Create note with model"""
        cursor = self._conn.execute(
            "INSERT INTO notes (title, content, folder_id) VALUES (?, ?, ?)",
            (note.title, note.content, note.folder_id)
        )
        note.id = cursor.lastrowid
        self._conn.commit()
        return note.id
    
    def integrity_check(self):
        """Check database integrity"""
        try:
            self._conn.execute("PRAGMA integrity_check")
            return True
        except:
            return False
    
    def get_note(self, note_id: int) -> Optional[Note]:
        """Get note by ID"""
        cursor = self._conn.execute("SELECT * FROM notes WHERE id = ?", (note_id,))
        row = cursor.fetchone()
        return Note.from_dict(dict(row)) if row else None
    
    def update_note(self, note: Note):
        """Update note"""
        self._conn.execute(
            """UPDATE notes SET title = ?, content = ?, folder_id = ?, 
                       updated_at = CURRENT_TIMESTAMP WHERE id = ?""",
            (note.title, note.content, note.folder_id, note.id)
        )
        self._conn.commit()
    
    def delete_note(self, note_id: int):
        """Delete note"""
        self._conn.execute("DELETE FROM notes WHERE id = ?", (note_id,))
        self._conn.commit()
    
    def get_notes(self, folder_id: Optional[int] = None) -> List[Note]:
        """Get notes by folder"""
        where_clause = "folder_id = ?" if folder_id else "folder_id IS NULL"
        cursor = self._conn.execute(
            f"SELECT * FROM notes WHERE {where_clause} ORDER BY title",
            (folder_id,) if folder_id else ()
        )
        return [Note.from_dict(dict(row)) for row in cursor.fetchall()]
    
    # ===== SEARCH =====
    def search_notes(self, query: str, limit: int = 50) -> List[SearchResult]:
        """Advanced fuzzy search with ranking"""
        if not query.strip():
            return []
        
        cursor = self._conn.execute(
            """SELECT n.*, rank 
               FROM notes_fts() ft 
               JOIN notes n ON ft.rowid = n.rowid 
               WHERE notes_fts MATCH ? 
               ORDER BY rank 
               LIMIT ?""",
            (query + "*", limit)
        )
        
        results = []
        for row in cursor.fetchall():
            note = Note.from_dict(dict(row))
            results.append(SearchResult(note=note, rank=float(row['rank'])))
        
        return results
    
    # ===== HIERARCHY HELPERS =====
    def get_full_hierarchy(self) -> List[Folder]:
        """Get complete folder tree"""
        root_folders = self.get_folders()
        for folder in root_folders:
            self._load_children(folder)
        return root_folders
    
    def _load_children(self, folder: Folder):
        """Recursively load folder children"""
        children = self.get_folders(folder.id)
        folder.children = children
        folder.notes = self.get_notes(folder.id)
        for child in children:
            self._load_children(child)
    
    def close(self):
        """Close connection"""
        if self._conn:
            self._conn.commit()
            self._conn.close()

# Global instance
#db_manager = DatabaseManager()
