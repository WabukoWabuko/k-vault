import { app, BrowserWindow, ipcMain, shell } from 'electron';
import { join } from 'path';
import { electronPath } from 'electron';
import Database from 'better-sqlite3';
import { initDatabase } from './db/schema';
import { DatabaseQueries } from './db/queries';
import type { Note, Folder, SearchResult } from '../types';

console.log('🚀 K-Vault Main Process Starting...');

let mainWindow: BrowserWindow | null = null;
let db: Database | null = null;
let dbQueries: DatabaseQueries | null = null;

// Database path (persists in user data)
const getDatabasePath = () => {
  if (process.env.NODE_ENV === 'development') {
    return join(process.cwd(), 'kvault-dev.db');
  }
  return join(app.getPath('userData'), 'kvault.db');
};

// Replace the createWindow function with this:
async function createWindow() {
  console.log('📱 Creating main window...');
  
  mainWindow = new BrowserWindow({
    height: 900,
    width: 1200,
    webPreferences: {
      preload: join(__dirname, '../preload.js'),
      nodeIntegration: false,
      contextIsolation: true,
      webSecurity: false, // Allow localhost in dev
    },
    show: false,
    titleBarStyle: 'hiddenInset',
    backgroundColor: '#1a1a1a',
  });

  if (process.env.NODE_ENV === 'development') {
    // Dev mode - load from vite dev server
    await mainWindow.loadURL('http://localhost:5173');
    mainWindow.webContents.openDevTools();
  } else {
    // Production - load built files
    await mainWindow.loadFile(join(__dirname, '../renderer/index.html'));
  }

  mainWindow.once('ready-to-show', () => {
    mainWindow?.show();
    console.log('✅ Main window ready!');
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

// ===== DATABASE SETUP =====
function initializeDatabase() {
  console.log('💾 Initializing SQLite database...');
  db = new Database(getDatabasePath());
  initDatabase(db);
  dbQueries = new DatabaseQueries(db);
  
  // Create root folder if doesn't exist
  const rootFolder = dbQueries!.createFolder('All Notes');
  console.log('✅ Database initialized with root folder');
}

// ===== IPC HANDLERS =====
function setupIPC() {
  if (!dbQueries) return;

  // Test connection
  ipcMain.handle('db:test', () => {
    return { status: 'connected', timestamp: Date.now() };
  });

  // Folders
  ipcMain.handle('folder:create', (_, name: string, parentId?: number) => {
    return dbQueries!.createFolder(name, parentId || null);
  });

  ipcMain.handle('folder:getAll', () => {
    return dbQueries!.getFolders();
  });

  ipcMain.handle('folder:rename', (_, id: number, name: string) => {
    dbQueries!.renameFolder(id, name);
    return { success: true };
  });

  ipcMain.handle('folder:delete', (_, id: number) => {
    dbQueries!.deleteFolder(id);
    return { success: true };
  });

  // Notes
  ipcMain.handle('note:create', (_, title: string, content?: string, folderId?: number) => {
    return dbQueries!.createNote(title, content || '', folderId || null);
  });

  ipcMain.handle('note:get', (_, id: number) => {
    return dbQueries!.getNote(id);
  });

  ipcMain.handle('note:update', (_, id: number, title: string, content: string) => {
    return dbQueries!.updateNote(id, title, content);
  });

  ipcMain.handle('note:delete', (_, id: number) => {
    dbQueries!.deleteNote(id);
    return { success: true };
  });

  ipcMain.handle('note:getInFolder', (_, folderId: number) => {
    return dbQueries!.getNotesInFolder(folderId);
  });

  // Search (THE MAGIC!)
  ipcMain.handle('search:notes', async (_, query: string) => {
    console.log(`🔍 Searching for: "${query}"`);
    return dbQueries!.searchNotes(query);
  });
}

// ===== APP LIFECYCLE =====
app.whenReady().then(async () => {
  initializeDatabase();
  setupIPC();
  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

// Graceful shutdown
app.on('before-quit', () => {
  console.log('👋 Shutting down K-Vault...');
  db?.close();
});
