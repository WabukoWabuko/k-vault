#!/usr/bin/env python3
"""
K-Vault Data Models
Type-safe classes for Note and Folder with validation
"""
from datetime import datetime
from typing import Optional, List
from dataclasses import dataclass, asdict, field
from enum import Enum

class ItemType(Enum):
    """Folder or Note"""
    FOLDER = "folder"
    NOTE = "note"

@dataclass
class Folder:
    """Folder model with hierarchy support"""
    id: Optional[int] = None
    name: str = ""
    parent_id: Optional[int] = None
    created_at: Optional[datetime] = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = field(default_factory=datetime.now)
    children: List['Folder'] = field(default_factory=list)
    notes: List['Note'] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        """Convert to dict for database"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict):
        """Create from database row"""
        folder = cls(
            id=data['id'],
            name=data['name'],
            parent_id=data.get('parent_id'),
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else datetime.now(),
            updated_at=datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else datetime.now()
        )
        return folder
    
    def is_root(self) -> bool:
        """Check if root folder"""
        return self.parent_id is None

@dataclass
class Note:
    """Note model with Markdown content"""
    id: Optional[int] = None
    title: str = ""
    content: str = ""
    folder_id: Optional[int] = None
    created_at: Optional[datetime] = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = field(default_factory=datetime.now)
    
    def to_dict(self) -> dict:
        """Convert to dict for database"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict):
        """Create from database row"""
        note = cls(
            id=data['id'],
            title=data['title'],
            content=data['content'],
            folder_id=data.get('folder_id'),
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else datetime.now(),
            updated_at=datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else datetime.now()
        )
        return note
    
    def has_links(self) -> bool:
        """Check if note contains [[links]]"""
        return '[[' in self.content and ']]' in self.content
    
    @property
    def preview(self) -> str:
        """First 100 chars as preview"""
        return (self.content[:100] + "...").strip()

@dataclass
class SearchResult:
    """Search result with relevance score"""
    note: Note
    rank: float = 0.0
    highlights: List[str] = field(default_factory=list)
    
    def __lt__(self, other):
        """Sort by relevance"""
        return self.rank > other.rank
