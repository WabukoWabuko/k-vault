import Database from 'better-sqlite3';

export function initDatabase(db: Database) {
  // Create folders table (hierarchical)
  db.exec(`
    CREATE TABLE IF NOT EXISTS folders (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      parent_id INTEGER,
      created_at INTEGER NOT NULL DEFAULT (strftime('%s', 'now')),
      FOREIGN KEY (parent_id) REFERENCES folders(id) ON DELETE CASCADE
    )
  `);

  // Create notes table
  db.exec(`
    CREATE TABLE IF NOT EXISTS notes (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      title TEXT NOT NULL,
      content TEXT NOT NULL,
      folder_id INTEGER,
      created_at INTEGER NOT NULL DEFAULT (strftime('%s', 'now')),
      updated_at INTEGER NOT NULL DEFAULT (strftime('%s', 'now')),
      FOREIGN KEY (folder_id) REFERENCES folders(id) ON DELETE SET NULL
    )
  `);

  // Create FTS5 virtual table for FAST fuzzy search
  db.exec(`
    CREATE VIRTUAL TABLE IF NOT EXISTS notes_fts USING fts5(
      title, 
      content, 
      content='notes', 
      tokenize='porter'
    )
  `);

  // Create indexes for performance
  db.exec('CREATE INDEX IF NOT EXISTS idx_notes_folder ON notes(folder_id)');
  db.exec('CREATE INDEX IF NOT EXISTS idx_folders_parent ON folders(parent_id)');
}
