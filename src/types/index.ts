// Shared TypeScript types for Notes and Folders
export interface Note {
  id: number;
  title: string;
  content: string;
  folderId?: number | null;
  createdAt: number;
  updatedAt: number;
}

export interface Folder {
  id: number;
  name: string;
  parentId?: number | null;
  createdAt: number;
}

export interface SearchResult {
  id: number;
  title: string;
  contentPreview: string;
  folderName?: string;
  score: number;
}
