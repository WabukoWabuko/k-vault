import { contextBridge, ipcRenderer } from 'electron';
import type { Note, Folder, SearchResult } from './types';

// Expose SAFE APIs to renderer (security!)
contextBridge.exposeInMainWorld('kvaultAPI', {
  // Test
  testDB: () => ipcRenderer.invoke('db:test'),

  // Folders
  createFolder: (name: string, parentId?: number) => 
    ipcRenderer.invoke('folder:create', name, parentId),
  getAllFolders: () => ipcRenderer.invoke('folder:getAll'),
  renameFolder: (id: number, name: string) => 
    ipcRenderer.invoke('folder:rename', id, name),
  deleteFolder: (id: number) => 
    ipcRenderer.invoke('folder:delete', id),

  // Notes
  createNote: (title: string, content?: string, folderId?: number) => 
    ipcRenderer.invoke('note:create', title, content, folderId),
  getNote: (id: number) => ipcRenderer.invoke('note:get', id),
  updateNote: (id: number, title: string, content: string) => 
    ipcRenderer.invoke('note:update', id, title, content),
  deleteNote: (id: number) => ipcRenderer.invoke('note:delete', id),
  getNotesInFolder: (folderId: number) => 
    ipcRenderer.invoke('note:getInFolder', folderId),

  // Search
  searchNotes: (query: string) => ipcRenderer.invoke('search:notes', query),
});

// TypeScript definitions for renderer
declare global {
  interface Window {
    kvaultAPI: {
      testDB: () => Promise<{ status: string; timestamp: number }>;
      createFolder: (name: string, parentId?: number) => Promise<Folder>;
      getAllFolders: () => Promise<Folder[]>;
      renameFolder: (id: number, name: string) => Promise<{ success: boolean }>;
      deleteFolder: (id: number) => Promise<{ success: boolean }>;
      createNote: (title: string, content?: string, folderId?: number) => Promise<Note>;
      getNote: (id: number) => Promise<Note | null>;
      updateNote: (id: number, title: string, content: string) => Promise<Note>;
      deleteNote: (id: number) => Promise<{ success: boolean }>;
      getNotesInFolder: (folderId: number) => Promise<Note[]>;
      searchNotes: (query: string) => Promise<SearchResult[]>;
    };
  }
}
