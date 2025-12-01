from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum
import uuid

class MemoryType(Enum):
    """Type of memory entry"""
    IDEA = "idea"
    DECISION = "decision"
    QUESTION = "question"
    TASK = "task"
    NOTE = "note"
    ISSUE = "issue"
    REFLECTION = "reflection"
    REMINDER = "reminder"
    INSIGHT = "insight"
    PROJECT = "project"

class MemorySource(Enum):
    """Source of memory"""
    VOICE = "voice"
    CHAT_GPT = "chatgpt"
    GEMINI = "gemini"
    CLAUDE = "claude"
    MANUAL = "manual"
    EMAIL = "email"
    FILE = "file"
    IMAGE = "image"
    URL = "url"

class SensitivityLevel(Enum):
    """Privacy/security level"""
    PUBLIC = "public"          # Can sync to Sheets
    PRIVATE = "private"        # Encrypted locally, no sync
    CONFIDENTIAL = "confidential"  # Encrypted + auth required

@dataclass
class Memory:
    """
    Complete memory entry with all metadata
    """
    # Core fields
    id: str                           # UUID
    timestamp: datetime               # When captured
    source: MemorySource              # Where it came from
    
    # Classification
    project: str                      # Mind-Q, AI Coach, Personal, etc.
    topic: str                        # Specific topic/subject
    type: MemoryType                  # Type of entry
    tags: List[str]                   # Keywords
    
    # Content (multi-level)
    ultra_brief: str                  # 1-sentence summary
    executive_summary: List[str]      # 3-5 bullet points
    detailed_summary: str             # Paragraph(s)
    raw_content: Optional[str]        # Original text (if available)
    
    # Extracted knowledge
    decisions: List[str] = field(default_factory=list)
    action_items: List[str] = field(default_factory=list)
    open_questions: List[str] = field(default_factory=list)
    key_insights: List[str] = field(default_factory=list)
    people_mentioned: List[str] = field(default_factory=list)
    projects_mentioned: List[str] = field(default_factory=list)
    
    # Metadata
    conversation_id: Optional[str] = None
    parent_memory_id: Optional[str] = None
    related_memory_ids: List[str] = field(default_factory=list)
    
    # Context
    language: str = "en"
    sentiment: str = "neutral"
    importance: int = 3
    confidence: float = 1.0
    
    # Access & security
    sensitivity: SensitivityLevel = SensitivityLevel.PRIVATE
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    
    # System
    embedding: Optional[List[float]] = None
    version: int = 1
    created_by: str = "HVA v1.0"
    updated_at: Optional[datetime] = None
    
    # Intelligence Upgrade v1.1
    status: str = "active"
    structured_data: Dict[str, Any] = field(default_factory=dict)
    
    # Intelligence Upgrade v1.2
    nag_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "source": self.source.value,
            "project": self.project,
            "topic": self.topic,
            "type": self.type.value,
            "tags": self.tags,
            "ultra_brief": self.ultra_brief,
            "executive_summary": self.executive_summary,
            "detailed_summary": self.detailed_summary,
            "raw_content": self.raw_content,
            "decisions": self.decisions,
            "action_items": self.action_items,
            "open_questions": self.open_questions,
            "key_insights": self.key_insights,
            "people_mentioned": self.people_mentioned,
            "projects_mentioned": self.projects_mentioned,
            "conversation_id": self.conversation_id,
            "parent_memory_id": self.parent_memory_id,
            "related_memory_ids": self.related_memory_ids,
            "language": self.language,
            "sentiment": self.sentiment,
            "importance": self.importance,
            "confidence": self.confidence,
            "sensitivity": self.sensitivity.value,
            "access_count": self.access_count,
            "last_accessed": self.last_accessed.isoformat() if self.last_accessed else None,
            "version": self.version,
            "created_by": self.created_by,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "status": self.status,
            "structured_data": self.structured_data,
            "nag_count": self.nag_count
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Memory':
        """Create Memory instance from dictionary"""
        return cls(
            id=data["id"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            source=MemorySource(data["source"]),
            project=data["project"],
            topic=data["topic"],
            type=MemoryType(data["type"]),
            tags=data["tags"],
            ultra_brief=data["ultra_brief"],
            executive_summary=data["executive_summary"],
            detailed_summary=data["detailed_summary"],
            raw_content=data.get("raw_content"),
            decisions=data.get("decisions", []),
            action_items=data.get("action_items", []),
            open_questions=data.get("open_questions", []),
            key_insights=data.get("key_insights", []),
            people_mentioned=data.get("people_mentioned", []),
            projects_mentioned=data.get("projects_mentioned", []),
            conversation_id=data.get("conversation_id"),
            parent_memory_id=data.get("parent_memory_id"),
            related_memory_ids=data.get("related_memory_ids", []),
            language=data.get("language", "en"),
            sentiment=data.get("sentiment", "neutral"),
            importance=data.get("importance", 3),
            confidence=data.get("confidence", 1.0),
            sensitivity=SensitivityLevel(data.get("sensitivity", "private")),
            access_count=data.get("access_count", 0),
            last_accessed=datetime.fromisoformat(data["last_accessed"]) if data.get("last_accessed") else None,
            embedding=data.get("embedding"),
            version=data.get("version", 1),
            created_by=data.get("created_by", "HVA v1.0"),
            updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else None,
            status=data.get("status", "active"),
            structured_data=data.get("structured_data", {}),
            nag_count=data.get("nag_count", 0)
        )
