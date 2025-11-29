from dataclasses import dataclass, field, asdict
from typing import Literal, Optional, List, Dict, Any
from datetime import datetime
import uuid

TaskStatus = Literal["open", "in_progress", "completed", "cancelled"]

@dataclass
class Project:
    id: str                # slug, e.g. "mind_q"
    name: str              # "Mind-Q"
    type: str              # "ai_coach", "personal", etc.
    created_at: str        # ISO format
    updated_at: str        # ISO format
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Project':
        return cls(**data)

@dataclass
class Task:
    id: str
    user_id: str           # e.g. "haitham-local"
    project_id: Optional[str]   # link to Project.id
    title: str
    description: str
    status: TaskStatus
    created_at: str        # ISO format
    updated_at: str        # ISO format
    language: Literal["ar", "en"]
    due_date: Optional[str] = None # ISO format
    notes: str = ""
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        return cls(**data)

@dataclass
class MemoryNote:
    id: str
    user_id: str
    project_id: Optional[str]
    source: Literal["voice", "chat", "gmail"]
    raw_text: str
    normalized_text: str
    decisions: List[str]
    next_actions: List[str]
    created_at: str        # ISO format
    language: Literal["ar", "en"]
    summary: Optional[str] = None
    file_path: Optional[str] = None  # Markdown file path under HVA_Workspace
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MemoryNote':
        return cls(**data)
