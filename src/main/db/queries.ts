import Database from 'better-sqlite3';
import type { Note, Folder, SearchResult } from '../../types';

export class DatabaseQueries {
  private db: Database;

  constructor(db: Database) {
    this.db = db;
  }

  // ===== FOLDERS =====
  createFolder(name: string, parentId: number | null = null): Folder {
    const stmt = this.db.prepare(`
      INSERT INTO folders (name, parent_id, created_at) 
      VALUES (?, ?, strftime('%s', 'now'))
    `);
    const result = stmt.run(name, parentId);
    return {
      id: result.lastInsertRowid as number,
      name,
      parentId,
      createdAt: Date.now()
    };
  }

  getFolders(): Folder[] {
    const stmt = this.db.prepare(`
      SELECT id, name, parent_id as parentId, created_at as createdAt 
      FROM folders 
      ORDER BY name
    `);
    return stmt.all() as Folder[];
  }

  renameFolder(id: number, newName: string): void {
    const stmt = this.db.prepare('UPDATE folders SET name = ? WHERE id = ?');
    stmt.run(newName, id);
  }

  deleteFolder(id: number): void {
    const stmt = this.db.prepare('DELETE FROM folders WHERE id = ?');
    stmt.run(id);
  }

  // ===== NOTES =====
  createNote(title: string, content: string = '', folderId: number | null = null): Note {
    const stmt = this.db.prepare(`
      INSERT INTO notes (title, content, folder_id, created_at, updated_at)
      VALUES (?, ?, ?, strftime('%s', 'now'), strftime('%s', 'now'))
    `);
    const result = stmt.run(title, content, folderId);
    
    // Add to FTS table
    this.addToSearchIndex(result.lastInsertRowid as number, title, content);
    
    return {
      id: result.lastInsertRowid as number,
      title,
      content,
      folderId,
      createdAt: Date.now(),
      updatedAt: Date.now()
    };
  }

  getNote(id: number): Note | null {
    const stmt = this.db.prepare(`
      SELECT id, title, content, folder_id as folderId, 
             created_at as createdAt, updated_at as updatedAt
      FROM notes WHERE id = ?
    `);
    const row = stmt.get(id) as Note | undefined;
    return row || null;
  }

  updateNote(id: number, title: string, content: string): Note {
    const now = Date.now();
    const stmt = this.db.prepare(`
      UPDATE notes 
      SET title = ?, content = ?, updated_at = ?
      WHERE id = ?
    `);
    stmt.run(title, content, Math.floor(now / 1000), id);
    
    // Update search index
    this.addToSearchIndex(id, title, content);
    
    return {
      id,
      title,
      content,
      folderId: null, // Will be updated separately if needed
      createdAt: now,
      updatedAt: now
    };
  }

  deleteNote(id: number): void {
    const stmt = this.db.prepare('DELETE FROM notes WHERE id = ?');
    stmt.run(id);
    
    // Remove from search index
    const ftsDelete = this.db.prepare('DELETE FROM notes_fts WHERE rowid = ?');
    ftsDelete.run(id);
  }

  getNotesInFolder(folderId: number): Note[] {
    const stmt = this.db.prepare(`
      SELECT id, title, content, folder_id as folderId, 
             created_at as createdAt, updated_at as updatedAt
      FROM notes 
      WHERE folder_id = ? OR folder_id IS NULL
      ORDER BY updated_at DESC
    `);
    return stmt.all(folderId) as Note[];
  }

  // ===== SEARCH (FTS5 MAGIC!) =====
  searchNotes(query: string): SearchResult[] {
    if (!query.trim()) return [];
    
    const stmt = this.db.prepare(`
      SELECT notes.id, notes.title, 
             snippet(notes_fts, 1, '<b>', '</b>', '...', 64) as contentPreview,
             bm25(notes_fts) as score
      FROM notes_fts 
      JOIN notes ON notes_fts.rowid = notes.id
      WHERE notes_fts MATCH ?
      ORDER BY score DESC
      LIMIT 50
    `);
    
    return stmt.all(query + '*') as SearchResult[];
  }

  private addToSearchIndex(id: number, title: string, content: string): void {
    const stmt = this.db.prepare(`
      INSERT INTO notes_fts(rowid, title, content) 
      VALUES (?, ?, ?)
    `);
    stmt.run(id, title, content);
  }

  private updateSearchIndex(id: number, title: string, content: string): void {
    this.addToSearchIndex(id, title, content);
  }
}
