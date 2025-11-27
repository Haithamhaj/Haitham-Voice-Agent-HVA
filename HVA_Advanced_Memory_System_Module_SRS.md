# 🧠 SOFTWARE REQUIREMENTS SPECIFICATION (SRS)
## HVA Advanced Memory & Knowledge System Module

**Version:** 1.0 (Complete - Enhanced & Intelligent)  
**Author:** Haitham  
**Target Platform:** macOS (Apple Silicon)  
**Parent System:** Haitham Voice Agent (HVA)  
**Module Priority:** Phase 3 (After Gmail Module)  
**Language:** English  
**Status:** Ready for Implementation

---

## TABLE OF CONTENTS

1. [Introduction](#1-introduction)
2. [System Overview](#2-system-overview)
3. [Architecture Design](#3-architecture-design)
4. [Functional Requirements](#4-functional-requirements)
5. [Intelligence Layer](#5-intelligence-layer)
6. [Performance Requirements](#6-performance-requirements)
7. [Security & Privacy](#7-security--privacy)
8. [Error Handling](#8-error-handling)
9. [Implementation Constraints](#9-implementation-constraints)
10. [Testing Requirements](#10-testing-requirements)
11. [Acceptance Criteria](#11-acceptance-criteria)
12. [Builder Instructions](#12-builder-instructions)

---

## 1. INTRODUCTION

### 1.1 Purpose

This SRS defines the **complete technical specification** for the HVA Advanced Memory & Knowledge System - a sophisticated personal knowledge management system that transforms scattered conversations, voice notes, and ideas into an organized, searchable, and intelligent external brain.

**Core Purpose:**
To capture, process, classify, store, and retrieve important knowledge generated during:
- ✅ AI conversations (ChatGPT / Gemini / Claude)
- ✅ Voice notes and commands
- ✅ Meetings and discussions
- ✅ Personal reflections
- ✅ Project brainstorming
- ✅ Problem-solving sessions

**What Makes It "Advanced":**
- 🧠 **Intelligent auto-classification** (ML-powered)
- 🕸️ **Knowledge graph** (connects related ideas)
- 🔍 **Semantic search** (find by meaning, not just keywords)
- 🤖 **Context injection** (brings past knowledge into new AI sessions)
- 🔗 **Idea evolution tracking** (see how thoughts develop over time)
- 📊 **Automated insights** (weekly/monthly knowledge reports)

### 1.2 The Problem This Solves

**Current Pain Points:**

1. **ChatGPT/Gemini have no persistent memory**
   - Every new session starts from zero
   - You repeat context every time
   - Important decisions get lost

2. **Scattered knowledge across platforms**
   - Some ideas in ChatGPT
   - Some in voice notes
   - Some in emails
   - No central repository

3. **Manual classification is tedious**
   - Takes time to organize notes
   - Often gets skipped
   - Inconsistent categorization

4. **Can't find past insights**
   - "I remember discussing this, but where?"
   - Keyword search misses semantically similar content
   - No way to see how ideas evolved

**The Solution:**
An intelligent system that automatically captures, processes, organizes, and surfaces relevant knowledge exactly when you need it.

### 1.3 Scope

**In Scope:**
- Multi-modal input capture (text, voice, images, files, URLs)
- Intelligent summarization and classification
- Knowledge graph with auto-linking
- Semantic + keyword + graph-based search
- Context injection for AI sessions
- Conflict detection and resolution
- Periodic maintenance and consolidation
- Multi-format export (Markdown, PDF, Notion, Obsidian)
- Privacy-preserving storage with encryption
- Google Sheets sync (optional, for reporting)

**Out of Scope (Future Versions):**
- Calendar integration
- Email content extraction (covered by Gmail Module)
- Real-time collaboration (multi-user)
- Mobile app (macOS only in v1.0)
- Cloud-hosted version (local-first only)

### 1.4 Integration with HVA

This module is **part of HVA** but can function independently:

```
HVA Core
  ↓
  ├─ Voice Module (STT/TTS)
  ├─ Gmail Module (Email operations)
  └─ Memory Module ← THIS MODULE
      ↓
      ├─ Capture Layer
      ├─ Processing Layer
      ├─ Storage Layer (SQLite + Vector DB + Graph)
      └─ Retrieval Layer
```

**Voice Commands Integration:**
- "احفظ هذه الفكرة للمشروع X"
- "ابحث عن ملاحظاتي عن Stage 08"
- "ايش قررنا بخصوص الـ database؟"
- "اعطني context للـ AI Coach project"

---

## 2. SYSTEM OVERVIEW

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     INPUT SOURCES                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Voice   │  │   Text   │  │  Image   │  │   File   │   │
│  │  Note    │  │  Chat    │  │  Photo   │  │   PDF    │   │
│  └─────┬────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
└────────┼────────────┼─────────────┼─────────────┼──────────┘
         │            │             │             │
         └────────────┴─────────────┴─────────────┘
                      ↓
┌─────────────────────────────────────────────────────────────┐
│              INTELLIGENT PROCESSING LAYER                    │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ 1. Multi-Modal Input Processor                       │   │
│  │    - Transcription (voice → text)                    │   │
│  │    - OCR (image → text)                              │   │
│  │    - Extraction (PDF/URL → text)                     │   │
│  └───────────────────────┬──────────────────────────────┘   │
│                          ↓                                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ 2. Conversation Summarizer (Multi-Level)             │   │
│  │    - Ultra-brief (1 sentence)                        │   │
│  │    - Executive (3-5 bullets)                         │   │
│  │    - Detailed (paragraph per topic)                  │   │
│  │    - Structured extraction (decisions, actions)      │   │
│  └───────────────────────┬──────────────────────────────┘   │
│                          ↓                                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ 3. Smart Classifier (ML-Powered)                     │   │
│  │    - Project detection                               │   │
│  │    - Topic extraction                                │   │
│  │    - Type classification (idea/decision/task/etc)    │   │
│  │    - Auto-tagging                                    │   │
│  │    - Learns from corrections                         │   │
│  └───────────────────────┬──────────────────────────────┘   │
│                          ↓                                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ 4. Knowledge Extractor                               │   │
│  │    - Decisions made                                  │   │
│  │    - Action items                                    │   │
│  │    - Open questions                                  │   │
│  │    - Key insights                                    │   │
│  │    - People mentioned                                │   │
│  │    - Projects referenced                             │   │
│  └───────────────────────┬──────────────────────────────┘   │
│                          ↓                                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ 5. Conflict Detector                                 │   │
│  │    - Find contradicting memories                     │   │
│  │    - Prompt for resolution                           │   │
│  └───────────────────────┬──────────────────────────────┘   │
└──────────────────────────┼──────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                     STORAGE LAYER                            │
│                                                              │
│  ┌─────────────┐     ┌──────────────┐     ┌─────────────┐  │
│  │   SQLite    │     │  Vector DB   │     │ Knowledge   │  │
│  │  Database   │     │  (Chroma/    │     │   Graph     │  │
│  │             │────▶│   FAISS)     │────▶│ (NetworkX)  │  │
│  │ Structured  │     │              │     │             │  │
│  │   Data      │     │  Embeddings  │     │ Connections │  │
│  └─────────────┘     └──────────────┘     └─────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │          Optional: Google Sheets Sync                │   │
│  │          (Backup & Reporting Only)                   │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────────────────┬──────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                   RETRIEVAL LAYER                            │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Smart Retrieval Engine                               │   │
│  │  - Semantic search (meaning-based)                   │   │
│  │  - Keyword search (exact match)                      │   │
│  │  - Graph traversal (related ideas)                   │   │
│  │  - Temporal search (time-based)                      │   │
│  │  - Hybrid ranking                                    │   │
│  └───────────────────────┬──────────────────────────────┘   │
│                          ↓                                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Context Injector                                     │   │
│  │  - Prepares context for new AI sessions              │   │
│  │  - Formats for ChatGPT/Gemini/Claude                 │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────────────────┼──────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                    OUTPUT & SERVICES                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Voice   │  │  Export  │  │ Insights │  │ Context  │   │
│  │Response  │  │ (MD/PDF) │  │ Reports  │  │Injection │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Data Flow

**Capture Flow:**
```
User Input → Process → Classify → Extract → Check Conflicts → 
Store (SQLite + Vector + Graph) → [Optional] Sync to Sheets
```

**Retrieval Flow:**
```
Query → Multi-Strategy Search → Rank Results → 
Format Context → Return to User/AI
```

**Maintenance Flow:**
```
Scheduled Task → Find Duplicates → Consolidate → 
Update Graph → Generate Insights → Archive Old
```

---

## 3. ARCHITECTURE DESIGN

### 3.1 Module Structure

```
haitham_voice_agent/
  tools/
    memory/
      __init__.py
      
      # Core components
      memory_system.py              # Main orchestrator
      
      # Input processing
      input/
        __init__.py
        multimodal_processor.py     # Handle all input types
        voice_transcriber.py        # Voice → text (Whisper)
        image_extractor.py          # Image → text (OCR + Vision)
        file_parser.py              # PDF/Doc parsing
        url_fetcher.py              # Web content extraction
      
      # Intelligence layer
      intelligence/
        __init__.py
        summarizer.py               # Multi-level summarization
        classifier.py               # ML-powered classification
        knowledge_extractor.py      # Extract decisions/actions/insights
        conflict_detector.py        # Find contradictions
        context_injector.py         # Prepare context for AI
      
      # Storage layer
      storage/
        __init__.py
        sqlite_store.py             # Structured data (SQLite)
        vector_store.py             # Embeddings (Chroma/FAISS)
        knowledge_graph.py          # Graph DB (NetworkX)
        sheets_sync.py              # Optional Google Sheets
      
      # Retrieval layer
      retrieval/
        __init__.py
        smart_retrieval.py          # Multi-strategy search
        semantic_search.py          # Vector-based search
        keyword_search.py           # SQL full-text search
        graph_search.py             # Traverse graph
        ranking.py                  # Result ranking & merging
      
      # Maintenance
      maintenance/
        __init__.py
        consolidator.py             # Merge duplicates
        archiver.py                 # Archive old memories
        insights_generator.py       # Weekly/monthly reports
      
      # Export & utilities
      export/
        __init__.py
        markdown_exporter.py
        pdf_exporter.py
        notion_exporter.py
        obsidian_exporter.py
      
      utils/
        __init__.py
        embeddings.py               # Generate embeddings
        text_processing.py          # Text utilities
        validators.py               # Input validation
      
      # Data models
      models/
        __init__.py
        memory.py                   # Memory data model
        classification.py           # Classification schema
        summary.py                  # Summary schema
        query.py                    # Query parameters
      
      # Configuration
      config.py
      exceptions.py
  
  tests/
    test_memory_system.py
    test_classification.py
    test_retrieval.py
    test_knowledge_graph.py
```

### 3.2 Core Data Models

#### 3.2.1 Memory Model

```python
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum

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
    decisions: List[str]              # Decisions made
    action_items: List[str]           # Tasks/next steps
    open_questions: List[str]         # Unresolved questions
    key_insights: List[str]           # Important realizations
    people_mentioned: List[str]       # Names referenced
    projects_mentioned: List[str]     # Projects referenced
    
    # Metadata
    conversation_id: Optional[str]    # If part of longer conversation
    parent_memory_id: Optional[str]   # If this updates/extends another
    related_memory_ids: List[str]     # Connected memories (graph edges)
    
    # Context
    language: str                     # "ar" or "en"
    sentiment: str                    # "positive" | "neutral" | "negative"
    importance: int                   # 1-5 scale
    confidence: float                 # Classification confidence (0-1)
    
    # Access & security
    sensitivity: SensitivityLevel     # Privacy level
    access_count: int                 # How many times retrieved
    last_accessed: Optional[datetime] # Last retrieval time
    
    # System
    embedding: Optional[List[float]]  # Vector embedding (1536-dim)
    version: int                      # Schema version
    created_by: str                   # "HVA v1.0"
    updated_at: Optional[datetime]    # Last modification
    
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
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
```

#### 3.2.2 Query Model

```python
@dataclass
class MemoryQuery:
    """
    Search query parameters
    """
    # Query text
    query_text: str
    
    # Filters
    project: Optional[str] = None
    topic: Optional[str] = None
    type: Optional[MemoryType] = None
    tags: Optional[List[str]] = None
    
    # Date range
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    
    # Search strategy
    search_mode: str = "hybrid"  # "semantic" | "keyword" | "graph" | "hybrid"
    
    # Results
    limit: int = 10
    min_similarity: float = 0.7  # For semantic search
    
    # Context
    include_related: bool = True  # Include graph connections
    max_related: int = 3
```

---

## 4. FUNCTIONAL REQUIREMENTS

### 4.1 Input Capture Operations

#### FR-I1: Capture from Voice

**Description:** Capture memory from voice command

**Voice Commands:**
- "احفظ هذه الفكرة: [content]"
- "سجّل ملاحظة عن [project]: [content]"
- "Save this idea for Mind-Q: [content]"

**Flow:**
1. User speaks command
2. STT transcribes to text
3. Parse project/topic from command
4. Route to processing pipeline
5. Save and confirm

**Inputs:**
```python
{
  "audio": bytes,           # Raw audio
  "language": "ar" | "en"   # Detected language
}
```

**Output:**
```python
{
  "memory_id": str,
  "ultra_brief": str,
  "project": str,
  "confirmation": "تم حفظ الفكرة لمشروع Mind-Q"
}
```

**Performance Target:** < 3 seconds (STT + processing + storage)

---

#### FR-I2: Import ChatGPT Conversation

**Description:** Import exported ChatGPT conversation

**Supported Formats:**
- ChatGPT JSON export (official)
- Plain text copy/paste
- Markdown formatted conversation

**Flow:**
1. User provides conversation (file or text)
2. Parse conversation structure
3. Identify key exchanges
4. Summarize entire conversation
5. Extract per-message insights
6. Create memory entries (one per major topic)
7. Link related entries in knowledge graph

**Inputs:**
```python
{
  "format": "json" | "text" | "markdown",
  "content": str | file_path,
  "metadata": {
    "source": "chatgpt",
    "date": Optional[datetime],
    "title": Optional[str]
  }
}
```

**Output:**
```python
{
  "conversation_id": str,
  "memories_created": List[str],  # Memory IDs
  "summary": str,
  "key_topics": List[str],
  "total_messages": int,
  "processing_time": float
}
```

**Performance Target:** < 10 seconds for 50-message conversation

**Implementation Notes:**

```python
class ChatGPTImporter:
    """
    Import ChatGPT conversations intelligently
    """
    
    async def import_conversation(self, content: str, format: str):
        """
        Main import pipeline
        """
        
        # 1. Parse based on format
        messages = await self.parse(content, format)
        
        # 2. Segment into topics
        # (ChatGPT conversations often cover multiple topics)
        topics = await self.segment_by_topic(messages)
        
        # 3. Process each topic separately
        memories = []
        for topic_segment in topics:
            memory = await self.process_topic(topic_segment)
            memories.append(memory)
        
        # 4. Create conversation-level summary
        conversation_summary = await self.summarize_full_conversation(messages)
        
        # 5. Link related memories in graph
        await self.link_memories(memories)
        
        return {
            "conversation_id": uuid.uuid4(),
            "memories_created": [m.id for m in memories],
            "summary": conversation_summary,
            # ...
        }
    
    async def segment_by_topic(self, messages: List[Message]):
        """
        Detect topic changes in conversation
        Uses embedding similarity to find topic boundaries
        """
        segments = []
        current_segment = [messages[0]]
        
        for i in range(1, len(messages)):
            # Get embeddings for last message and current
            prev_embedding = await self.get_embedding(messages[i-1].text)
            curr_embedding = await self.get_embedding(messages[i].text)
            
            # Calculate similarity
            similarity = cosine_similarity(prev_embedding, curr_embedding)
            
            # If similarity drops significantly, topic changed
            if similarity < 0.6:
                segments.append(current_segment)
                current_segment = [messages[i]]
            else:
                current_segment.append(messages[i])
        
        segments.append(current_segment)
        return segments
```

---

#### FR-I3: Import from Gemini

**Description:** Import Gemini conversation via copy/paste

**Note:** Gemini doesn't have official export yet, so import via:
1. Manual copy/paste
2. Browser extension (future)

**Flow:** Similar to FR-I2 but with Gemini-specific parsing

---

#### FR-I4: Capture from Image

**Description:** Extract text and ideas from images

**Use Cases:**
- Whiteboard photos from meetings
- Screenshots of important text
- Diagrams with annotations
- Handwritten notes

**Flow:**
1. User uploads image
2. OCR extracts text (if any)
3. Vision model (Gemini) analyzes image
4. Combine OCR + vision analysis
5. Process as regular text memory

**Inputs:**
```python
{
  "image": file_path | bytes,
  "context": Optional[str],  # User-provided context
  "project": Optional[str]
}
```

**Performance Target:** < 5 seconds

---

#### FR-I5: Capture from File (PDF/Document)

**Description:** Extract knowledge from documents

**Supported:**
- PDF
- DOCX
- TXT
- Markdown

**Flow:**
1. Extract text from file
2. Chunk if large (> 10 pages)
3. Summarize each chunk
4. Create memory per major section/topic
5. Link in knowledge graph

**Performance Target:** < 10 seconds for 10-page PDF

---

#### FR-I6: Capture from URL

**Description:** Save web content as memory

**Use Cases:**
- Articles
- Blog posts
- Documentation pages
- Twitter threads

**Flow:**
1. Fetch URL content
2. Extract main text (remove ads/navigation)
3. Summarize article
4. Extract key points
5. Save as memory with URL reference

**Performance Target:** < 5 seconds

---

### 4.2 Processing & Intelligence Operations

#### FR-P1: Multi-Level Summarization

**Description:** Generate summaries at 3 levels of detail

**Levels:**
1. **Ultra-brief:** 1 sentence (< 20 words)
2. **Executive:** 3-5 bullet points
3. **Detailed:** 1-2 paragraphs

**Example:**

Input: [Long ChatGPT conversation about Mind-Q database architecture]

Output:
```python
{
  "ultra_brief": "Decided to use PostgreSQL with TimescaleDB for Mind-Q time-series data.",
  
  "executive_summary": [
    "Evaluated SQLite, PostgreSQL, and MongoDB for Mind-Q database",
    "PostgreSQL + TimescaleDB chosen for time-series optimization",
    "Will use connection pooling with PgBouncer",
    "Migration planned for Q2 2025",
    "Expected 10x performance improvement for logistics queries"
  ],
  
  "detailed_summary": "We conducted a comprehensive evaluation of database options for Mind-Q's logistics data platform. After analyzing our query patterns and data volume projections, we determined that PostgreSQL with the TimescaleDB extension provides the best fit for our time-series heavy workload. The decision was based on three factors: native time-series optimization, excellent SQL compatibility for complex analytical queries, and proven scalability to billions of rows. We'll implement connection pooling using PgBouncer to handle concurrent requests efficiently. The migration from our current SQLite-based system is scheduled for Q2 2025, with an expected 10x improvement in query performance for our core logistics analytics."
}
```

**Performance Target:** < 3 seconds for 1000-word input

---

#### FR-P2: Intelligent Classification

**Description:** Auto-classify memory with ML-powered system

**Classification Dimensions:**
1. **Project:** Mind-Q, AI Coach Mastery, Personal, Business, Health, etc.
2. **Topic:** Specific subject within project
3. **Type:** Idea, Decision, Task, Question, Note, Issue, Reflection, Reminder
4. **Tags:** Keyword extraction (5-10 tags)

**How It Works:**

```python
class SmartClassifier:
    """
    ML-powered classification that learns from corrections
    """
    
    def __init__(self):
        # Load pre-trained model or initialize new
        self.model = self.load_model()
        self.correction_buffer = []
    
    async def classify(self, text: str) -> Classification:
        """
        Multi-stage classification
        """
        
        # Stage 1: Rule-based (fast, high-confidence patterns)
        if "mind-q" in text.lower() or "logistics" in text.lower():
            project = "Mind-Q"
            confidence = 0.95
        elif "coaching" in text.lower() or "pcc" in text.lower():
            project = "AI Coach Mastery"
            confidence = 0.95
        else:
            # Stage 2: ML model
            project, confidence = await self.model_predict_project(text)
        
        # If confidence < 0.7, ask user
        if confidence < 0.7:
            project = await self.ask_user_for_project(text)
            confidence = 1.0  # User confirmation = 100% confidence
        
        # Classify type
        type_ = await self.classify_type(text)
        
        # Extract topic
        topic = await self.extract_topic(text)
        
        # Generate tags
        tags = await self.extract_tags(text)
        
        return Classification(
            project=project,
            topic=topic,
            type=type_,
            tags=tags,
            confidence=confidence
        )
    
    async def learn_from_correction(self, original: str, corrected: Classification):
        """
        User corrects classification → system learns
        """
        self.correction_buffer.append({
            "text": original,
            "predicted": self.last_prediction,
            "correct": corrected,
            "timestamp": datetime.now()
        })
        
        # Retrain every 50 corrections
        if len(self.correction_buffer) >= 50:
            await self.retrain_model()
            self.correction_buffer = []
```

**Performance Target:** < 1 second

---

#### FR-P3: Knowledge Extraction

**Description:** Extract structured information from text

**Extracts:**
1. **Decisions:** Clear choices made
2. **Action Items:** Tasks with optional deadlines
3. **Questions:** Open questions needing answers
4. **Insights:** Key realizations or learnings
5. **People:** Names mentioned
6. **Projects:** Projects referenced

**Example:**

Input:
```
"We decided to switch to PostgreSQL for Mind-Q. 
Yazid will handle the migration by end of March.
Still unsure about caching strategy - Redis vs Memcached?
The key insight is that our bottleneck is I/O, not CPU."
```

Output:
```python
{
  "decisions": [
    "Switch to PostgreSQL for Mind-Q database"
  ],
  "action_items": [
    {
      "task": "Handle database migration to PostgreSQL",
      "assignee": "Yazid",
      "deadline": "2025-03-31",
      "priority": "high"
    }
  ],
  "open_questions": [
    "Which caching strategy: Redis or Memcached?"
  ],
  "key_insights": [
    "Performance bottleneck is I/O, not CPU"
  ],
  "people_mentioned": ["Yazid"],
  "projects_mentioned": ["Mind-Q"]
}
```

**Performance Target:** < 2 seconds

---

#### FR-P4: Conflict Detection

**Description:** Detect when new memory contradicts existing knowledge

**How It Works:**

1. When saving new memory, search for semantically similar memories
2. Use LLM to detect if new info contradicts old info
3. If conflict detected, prompt user for resolution

**Example:**

```
Existing Memory (Feb 1):
"Decided to use SQLite for Mind-Q database"

New Memory (Mar 15):
"Decided to use PostgreSQL for Mind-Q database"

→ CONFLICT DETECTED

System: "⚠️ This decision conflicts with previous note from Feb 1.
Previous: 'Use SQLite'
New: 'Use PostgreSQL'

What would you like to do?
[1] Update decision (mark old as outdated)
[2] Keep both (evolution of decision)
[3] Cancel new entry"
```

**Resolution Options:**
1. **Update:** Mark old as `outdated`, keep new
2. **Evolution:** Link as `evolved_from`, keep both
3. **Cancel:** Don't save new

**Performance Target:** < 3 seconds

---

### 4.3 Storage Operations

#### FR-S1: Save Memory

**Description:** Store processed memory in all storage layers

**Flow:**
1. Save to SQLite (structured data)
2. Generate embedding and save to Vector DB
3. Add node to Knowledge Graph
4. Create relationships with similar memories
5. [Optional] Sync to Google Sheets

**Inputs:**
```python
{
  "memory": Memory,  # Complete memory object
  "sync_to_sheets": bool = False
}
```

**Output:**
```python
{
  "memory_id": str,
  "stored_in": ["sqlite", "vector_db", "graph"],
  "relationships_created": int,
  "sync_status": "synced" | "skipped" | "failed"
}
```

**Performance Target:** < 500ms

---

#### FR-S2: Update Memory

**Description:** Modify existing memory

**Use Cases:**
- User corrects classification
- Add new insights to existing memory
- Update status (e.g., task completed)

**Note:** Creates new version, keeps old (version history)

**Performance Target:** < 500ms

---

#### FR-S3: Delete Memory

**Description:** Soft delete (mark as deleted, don't remove)

**Reason:** Maintain graph integrity and allow recovery

**After 90 days:** Permanent deletion (configurable)

---

### 4.4 Retrieval Operations

#### FR-R1: Semantic Search

**Description:** Search by meaning, not exact keywords

**How It Works:**
1. Generate embedding for query
2. Search vector DB for similar embeddings
3. Rank by cosine similarity
4. Return top N results

**Example:**

Query: "What did we decide about the database?"

Finds:
- "Decided to use PostgreSQL for Mind-Q"
- "Database migration planned for Q2"
- "TimescaleDB extension chosen for time-series"

Even though none contain exact phrase "decide about database"

**Inputs:**
```python
{
  "query": str,
  "limit": int = 10,
  "min_similarity": float = 0.7,
  "filters": Optional[dict] = None  # Project, date range, etc.
}
```

**Performance Target:** < 1 second

---

#### FR-R2: Keyword Search

**Description:** Exact text matching using SQL full-text search

**Use Cases:**
- Looking for specific terms
- Technical keywords
- Names

**Performance Target:** < 500ms

---

#### FR-R3: Hybrid Search

**Description:** Combine semantic + keyword + graph search

**Strategy:**
1. Run semantic search (weight: 40%)
2. Run keyword search (weight: 30%)
3. Find graph neighbors (weight: 20%)
4. Consider recency (weight: 10%)
5. Merge and re-rank

**This is the DEFAULT search mode** (most accurate)

**Performance Target:** < 1.5 seconds

---

#### FR-R4: Graph Traversal

**Description:** Find memories connected in knowledge graph

**Operations:**
- **Find related:** Direct connections
- **Find similar:** 2-hop neighbors
- **Trace evolution:** Follow `evolved_from` edges
- **Find dependencies:** Follow `depends_on` edges

**Example:**

```python
# Find all ideas that evolved from original decision
evolution = memory_system.trace_evolution(memory_id="abc123")

# Returns:
{
  "original": Memory(...),
  "evolved_into": [
    Memory(...),  # First evolution
    Memory(...),  # Second evolution
  ],
  "timeline": [
    {"date": "2025-02-01", "summary": "Initial decision: SQLite"},
    {"date": "2025-03-15", "summary": "Evolved to: PostgreSQL"},
  ]
}
```

**Performance Target:** < 1 second

---

#### FR-R5: Filter by Project/Date/Type

**Description:** Standard filtering operations

**Filters:**
- Project
- Topic
- Type
- Tags
- Date range
- Importance level
- Source

**Can be combined with any search mode**

---

### 4.5 Context Injection Operations

#### FR-C1: Prepare Context for AI Session

**Description:** Generate formatted context to paste into new AI chat

**Use Case:**
You're starting a new ChatGPT session and want to inject relevant past knowledge

**Flow:**
1. User provides query or project name
2. System retrieves relevant memories
3. Formats as concise context prompt
4. User copies and pastes into ChatGPT/Gemini

**Example:**

User: "اعطني context للـ Mind-Q Stage 09"

System retrieves 10 relevant memories and formats:

```markdown
# Context from Past Sessions (HVA Memory System)

## Mind-Q Stage 09 - Previous Discussions

**[2025-02-15] Database Architecture Decision**
- Decided: PostgreSQL + TimescaleDB for time-series optimization
- Rationale: Better performance for logistics analytics
- Next: Migration in Q2 2025

**[2025-02-20] API Design Patterns**
- Decided: RESTful API with FastAPI framework
- Authentication: OAuth 2.0 + JWT
- Rate limiting: 1000 requests/hour per user

**[2025-03-01] Frontend Framework Selection**
- Decided: React + TypeScript
- State management: Redux Toolkit
- UI library: Material-UI

**[2025-03-10] Deployment Strategy**
- Decided: Docker containers on AWS ECS
- CI/CD: GitHub Actions
- Monitoring: DataDog

**Key Open Questions:**
- Caching strategy: Redis vs Memcached?
- WebSocket vs Server-Sent Events for real-time?

**Pending Action Items:**
- [ ] Yazid: Complete database migration (due Mar 31)
- [ ] Haitham: Design API authentication flow (due Mar 20)

---

Please consider this context when discussing Mind-Q Stage 09.
```

**User copies this and pastes into new ChatGPT session** → ChatGPT now has full context!

**Performance Target:** < 2 seconds

---

#### FR-C2: Generate Session Summary

**Description:** At end of AI session, save summary to memory

**Voice Command:**
"احفظ ملخص هذه الجلسة"

**Flow:**
1. User copies entire ChatGPT conversation
2. Pastes into HVA
3. HVA summarizes and saves
4. Creates memories for key points

---

### 4.6 Maintenance Operations

#### FR-M1: Find and Merge Duplicates

**Description:** Detect very similar memories and merge them

**How:**
1. Find memories with > 0.9 similarity
2. Review for duplication
3. Merge into single memory with combined metadata
4. Update graph connections

**Runs:** Weekly (scheduled)

---

#### FR-M2: Archive Old Memories

**Description:** Move old, unused memories to archive

**Criteria:**
- Older than 180 days
- Access count = 0
- Not connected to active memories

**Archived memories:**
- Still searchable
- Not in default results
- Can be restored

**Runs:** Monthly (scheduled)

---

#### FR-M3: Generate Insights Report

**Description:** Periodic analysis of your knowledge

**Reports:**
1. **Weekly:**
   - Main focus areas
   - Decisions made
   - Open questions
   - Productivity patterns

2. **Monthly:**
   - Project progress
   - Knowledge growth
   - Common themes
   - Recommendations

**Example Weekly Report:**

```markdown
# Your Week in Knowledge (Mar 11-17, 2025)

## 📊 Overview
- 23 new memories captured
- 8 decisions made
- 15 action items created
- 12 questions asked

## 🎯 Main Focus Areas
1. Mind-Q Stage 09 (12 memories)
2. AI Coach Mastery (6 memories)
3. Personal projects (5 memories)

## ✅ Key Decisions
- Switched to PostgreSQL for Mind-Q database
- Selected React for frontend framework
- Approved new pricing model for AI Coach

## ❓ Open Questions
- Redis vs Memcached for caching?
- Launch date for AI Coach Mastery?
- Should we hire additional developer?

## 📈 Insights
- Your most productive day: Tuesday (9 memories)
- Most discussed topic: Database architecture
- Average time between idea and decision: 3.2 days

## 💡 Recommendations
- Follow up on open caching question (5 days old)
- Review pricing model decision with team
- Schedule database migration planning session
```

**Performance Target:** < 10 seconds to generate

---

### 4.7 Export Operations

#### FR-E1: Export to Markdown

**Description:** Export memories as formatted Markdown

**Options:**
- All memories
- Filtered by project/date
- Single memory with full details

**Output Structure:**
```markdown
# Memory Export - Mind-Q Project

## 2025-03-15: Database Architecture Decision

**Type:** Decision  
**Tags:** database, postgresql, architecture, mind-q

### Summary
We decided to switch from SQLite to PostgreSQL with TimescaleDB extension for Mind-Q's time-series data.

### Key Points
- PostgreSQL provides better performance for analytics
- TimescaleDB optimizes time-series queries
- Migration planned for Q2 2025
- Expected 10x performance improvement

### Decisions
- ✅ Use PostgreSQL + TimescaleDB
- ✅ Implement connection pooling with PgBouncer

### Action Items
- [ ] Yazid: Complete migration by March 31
- [ ] Test performance benchmarks

### Open Questions
- Redis or Memcached for caching?

---

[Continue for other memories...]
```

**Performance Target:** < 3 seconds for 100 memories

---

#### FR-E2: Export to PDF

**Description:** Generate professional PDF report

**Use Cases:**
- Share with team
- Print for review
- Archive

**Performance Target:** < 5 seconds for 100 memories

---

#### FR-E3: Export to Notion

**Description:** Sync memories to Notion database

**Uses Notion API to create/update pages**

---

#### FR-E4: Export to Obsidian

**Description:** Generate Obsidian-compatible Markdown with backlinks

**Features:**
- Wiki-style links: `[[Memory ID]]`
- Frontmatter with metadata
- Tags as `#tag`

---

### 4.8 Voice Command Integration

**All operations accessible via voice:**

| Command (Arabic) | Command (English) | Function |
|------------------|-------------------|----------|
| "احفظ هذه الفكرة لـ [project]" | "Save this idea for [project]" | FR-I1 |
| "استورد محادثة من ChatGPT" | "Import ChatGPT conversation" | FR-I2 |
| "ابحث عن [query]" | "Search for [query]" | FR-R3 |
| "ايش قررنا عن [topic]؟" | "What did we decide about [topic]?" | FR-R3 (decisions only) |
| "اعطني context لـ [project]" | "Give me context for [project]" | FR-C1 |
| "اعرض آخر الملاحظات" | "Show recent notes" | FR-R3 (sorted by date) |
| "صدّر المشروع إلى Markdown" | "Export project to Markdown" | FR-E1 |
| "ايش كانت افكاري الاسبوع الماضي؟" | "What were my ideas last week?" | FR-M3 |

---

## 5. INTELLIGENCE LAYER

### 5.1 Machine Learning Components

#### 5.1.1 Classification Model

**Type:** Multi-label text classification

**Architecture:**
- Option A (Simple): TF-IDF + Logistic Regression
- Option B (Advanced): Fine-tuned BERT/DistilBERT

**Training Data:**
- Initial: Rule-based labels
- Continuous: User corrections

**Re-training Frequency:** Every 50 corrections or monthly

---

#### 5.1.2 Embedding Model

**Used For:** Semantic search

**Model:** OpenAI `text-embedding-3-small` (1536 dimensions)
- OR: Sentence-BERT (open source, local)

**Why:** Balance of quality and speed

---

#### 5.1.3 Summarization

**Model:** Gemini 1.5 Flash (fast + accurate)

**Prompt Engineering:**
```python
SUMMARIZATION_PROMPT = """
You are an expert at distilling information into clear summaries.

Given the following conversation/text, provide THREE levels of summary:

1. ULTRA-BRIEF (one sentence, max 20 words)
2. EXECUTIVE (3-5 bullet points, key takeaways)
3. DETAILED (1-2 paragraphs, comprehensive but concise)

Additionally, extract:
- DECISIONS made
- ACTION ITEMS (with assignee if mentioned)
- OPEN QUESTIONS
- KEY INSIGHTS

Text:
{text}

Respond in JSON format.
"""
```

---

### 5.2 Knowledge Graph Intelligence

#### 5.2.1 Relationship Types

```python
class RelationshipType(Enum):
    EVOLVED_FROM = "evolved_from"        # Idea A evolved into Idea B
    BUILDS_ON = "builds_on"              # B builds on foundation of A
    CONTRADICTS = "contradicts"          # B contradicts A
    ANSWERS = "answers"                  # B answers question A
    IMPLEMENTS = "implements"            # B implements decision A
    REFERENCES = "references"            # B mentions/references A
    DEPENDS_ON = "depends_on"            # B depends on completion of A
    ALTERNATIVE_TO = "alternative_to"    # B is alternative approach to A
```

#### 5.2.2 Auto-Linking Algorithm

```python
async def auto_link_memory(new_memory: Memory):
    """
    Automatically create relationships with existing memories
    """
    
    # 1. Find semantically similar memories
    similar = await vector_db.search(
        new_memory.embedding,
        threshold=0.75,
        limit=10,
        filters={"project": new_memory.project}  # Same project only
    )
    
    # 2. For each similar memory, determine relationship type
    for candidate in similar:
        relationship = await classify_relationship(new_memory, candidate)
        
        if relationship:
            await knowledge_graph.add_edge(
                new_memory.id,
                candidate.id,
                type=relationship,
                weight=similarity_score
            )
    
    # 3. Special cases: explicit references
    # If new memory mentions another by topic/date
    if "we discussed this on" in new_memory.detailed_summary.lower():
        referenced = await find_by_date_and_topic(...)
        if referenced:
            await knowledge_graph.add_edge(
                new_memory.id,
                referenced.id,
                type=RelationshipType.REFERENCES
            )

async def classify_relationship(mem_a: Memory, mem_b: Memory):
    """
    Use LLM to determine relationship type
    """
    prompt = f"""
    Memory A (newer): {mem_a.executive_summary}
    Memory B (older): {mem_b.executive_summary}
    
    What is the relationship from A to B?
    
    Options:
    - evolved_from: A is an evolution/update of idea in B
    - builds_on: A builds upon foundation laid in B
    - contradicts: A contradicts or reverses decision in B
    - answers: A answers question raised in B
    - implements: A describes implementation of decision in B
    - references: A mentions/references B casually
    - none: No meaningful relationship
    
    Respond with just the relationship type or "none".
    """
    
    relationship = await llm_classify(prompt)
    return relationship if relationship != "none" else None
```

---

### 5.3 Smart Ranking

**When multiple search strategies return results, how to rank?**

```python
class SmartRanker:
    """
    Intelligent ranking of search results
    """
    
    def rank(self, results: List[SearchResult], query: MemoryQuery):
        """
        Multi-factor ranking
        """
        
        for result in results:
            score = 0.0
            
            # Factor 1: Relevance (from search)
            score += result.relevance * 0.4
            
            # Factor 2: Recency (newer = better)
            days_old = (datetime.now() - result.memory.timestamp).days
            recency_score = 1.0 / (1.0 + days_old / 30)  # Decay over 30 days
            score += recency_score * 0.2
            
            # Factor 3: Importance (user-assigned)
            score += (result.memory.importance / 5.0) * 0.15
            
            # Factor 4: Access history (frequently accessed = more relevant)
            access_score = min(result.memory.access_count / 10, 1.0)
            score += access_score * 0.1
            
            # Factor 5: Project match (boost if matches current context)
            if query.project and result.memory.project == query.project:
                score += 0.15
            
            result.final_score = score
        
        # Sort by final score
        return sorted(results, key=lambda r: r.final_score, reverse=True)
```

---

## 6. PERFORMANCE REQUIREMENTS

### 6.1 Latency Targets

| Operation | Target | Acceptable | Maximum |
|-----------|--------|------------|---------|
| Voice capture → save | < 3s | < 5s | 8s |
| Import ChatGPT (50 msgs) | < 10s | < 15s | 20s |
| Semantic search | < 1s | < 1.5s | 2s |
| Hybrid search | < 1.5s | < 2s | 3s |
| Save memory | < 500ms | < 800ms | 1s |
| Generate context | < 2s | < 3s | 5s |
| Export to Markdown (100) | < 3s | < 5s | 8s |
| Weekly insights report | < 10s | < 15s | 20s |

### 6.2 Scalability Targets

**Storage:**
- Support ≥ 10,000 memories without performance degradation
- SQLite database < 100 MB for 1,000 memories
- Vector index < 200 MB for 10,000 memories

**Search:**
- Semantic search: < 1s even with 10,000 memories
- Graph traversal: < 1s for 3-hop search

**Memory Usage:**
- Peak RAM: < 500 MB during normal operation
- Peak RAM during import: < 1 GB

### 6.3 Optimization Strategies

**1. Lazy Loading:**
```python
# Don't load full memory objects until needed
class MemoryProxy:
    def __init__(self, memory_id: str):
        self.id = memory_id
        self._full_memory = None
    
    @property
    def full_memory(self):
        if self._full_memory is None:
            self._full_memory = storage.load_full(self.id)
        return self._full_memory
```

**2. Index Optimization:**
```sql
-- SQLite indexes for fast queries
CREATE INDEX idx_project ON memories(project);
CREATE INDEX idx_timestamp ON memories(timestamp);
CREATE INDEX idx_type ON memories(type);
CREATE INDEX idx_project_timestamp ON memories(project, timestamp);

-- Full-text search index
CREATE VIRTUAL TABLE memories_fts USING fts5(
    ultra_brief,
    executive_summary,
    detailed_summary,
    tags
);
```

**3. Caching:**
```python
class MemoryCache:
    """
    LRU cache for frequently accessed memories
    """
    
    def __init__(self, max_size: int = 100):
        self.cache = {}
        self.access_order = []
        self.max_size = max_size
    
    def get(self, memory_id: str):
        if memory_id in self.cache:
            # Move to end (most recently used)
            self.access_order.remove(memory_id)
            self.access_order.append(memory_id)
            return self.cache[memory_id]
        return None
    
    def put(self, memory: Memory):
        if len(self.cache) >= self.max_size:
            # Remove least recently used
            oldest = self.access_order.pop(0)
            del self.cache[oldest]
        
        self.cache[memory.id] = memory
        self.access_order.append(memory.id)
```

---

## 7. SECURITY & PRIVACY

### 7.1 Data Security

**Encryption at Rest:**
```python
from cryptography.fernet import Fernet
import keyring

class EncryptionManager:
    """
    Encrypt sensitive memories
    """
    
    def __init__(self):
        # Store encryption key in macOS Keychain
        key = keyring.get_password("HVA_Memory", "encryption_key")
        if not key:
            key = Fernet.generate_key().decode()
            keyring.set_password("HVA_Memory", "encryption_key", key)
        
        self.cipher = Fernet(key.encode())
    
    def encrypt_memory(self, memory: Memory):
        """
        Encrypt sensitive fields
        """
        if memory.sensitivity in [SensitivityLevel.PRIVATE, SensitivityLevel.CONFIDENTIAL]:
            # Encrypt content fields
            memory.detailed_summary = self.cipher.encrypt(
                memory.detailed_summary.encode()
            ).decode()
            
            if memory.raw_content:
                memory.raw_content = self.cipher.encrypt(
                    memory.raw_content.encode()
                ).decode()
        
        return memory
    
    def decrypt_memory(self, memory: Memory):
        """
        Decrypt when retrieving
        """
        if memory.sensitivity in [SensitivityLevel.PRIVATE, SensitivityLevel.CONFIDENTIAL]:
            memory.detailed_summary = self.cipher.decrypt(
                memory.detailed_summary.encode()
            ).decode()
            
            if memory.raw_content:
                memory.raw_content = self.cipher.decrypt(
                    memory.raw_content.encode()
                ).decode()
        
        return memory
```

### 7.2 Privacy Controls

**Sensitivity Levels:**

```python
# PUBLIC: Can be synced to Google Sheets
# - Work ideas
# - Project plans
# - Technical decisions

# PRIVATE: Local only, encrypted
# - Personal reflections
# - Health notes
# - Financial discussions

# CONFIDENTIAL: Local only, encrypted + auth required
# - Passwords (should never be stored anyway)
# - Personal identifiable information
# - Sensitive business information
```

**Auto-Detection of Sensitive Content:**
```python
async def detect_sensitivity(text: str) -> SensitivityLevel:
    """
    Auto-detect if content is sensitive
    """
    
    # Patterns indicating sensitivity
    sensitive_patterns = [
        r'\b\d{16}\b',  # Credit card
        r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
        r'password',
        r'secret',
        r'confidential',
        r'private',
    ]
    
    for pattern in sensitive_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return SensitivityLevel.CONFIDENTIAL
    
    # Ask LLM for nuanced detection
    sensitivity = await llm_classify_sensitivity(text)
    return sensitivity
```

### 7.3 Data Retention

**Retention Policy:**
- Deleted memories: 90-day grace period (soft delete)
- After 90 days: Permanent deletion
- Archives: Retained indefinitely (until manually deleted)

**User Controls:**
- Manual permanent deletion (bypass grace period)
- Export before deletion
- Bulk deletion by project/date

---

## 8. ERROR HANDLING

### 8.1 Error Types

```python
class MemorySystemError(Exception):
    """Base exception"""
    pass

class ProcessingError(MemorySystemError):
    """Error during summarization/classification"""
    pass

class StorageError(MemorySystemError):
    """Error saving to database"""
    pass

class RetrievalError(MemorySystemError):
    """Error during search/retrieval"""
    pass

class ImportError(MemorySystemError):
    """Error importing conversation"""
    pass

class ConflictError(MemorySystemError):
    """Unresolved conflict detected"""
    pass
```

### 8.2 Error Recovery

```python
from tenacity import retry, stop_after_attempt, wait_exponential

class MemorySystem:
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(min=1, max=10),
        retry=retry_if_exception_type(StorageError)
    )
    async def save_memory(self, memory: Memory):
        """
        Auto-retry on storage failures
        """
        try:
            await self.storage.save(memory)
        except Exception as e:
            logger.error(f"Storage failed: {e}")
            raise StorageError(f"Failed to save memory: {e}")
```

### 8.3 Graceful Degradation

```python
async def search(self, query: MemoryQuery):
    """
    Degrade gracefully if components fail
    """
    
    results = []
    
    # Try semantic search
    try:
        semantic_results = await self.semantic_search(query)
        results.extend(semantic_results)
    except Exception as e:
        logger.warning(f"Semantic search failed: {e}, falling back to keyword")
    
    # Fallback to keyword search
    if not results:
        try:
            keyword_results = await self.keyword_search(query)
            results.extend(keyword_results)
        except Exception as e:
            logger.error(f"All search methods failed: {e}")
            raise RetrievalError("Unable to search memories")
    
    return results
```

---

## 9. IMPLEMENTATION CONSTRAINTS

### 9.1 Technology Stack

**Core:**
```txt
# Python
python>=3.11

# Database
sqlalchemy==2.0.23
aiosqlite==0.19.0

# Vector DB
chromadb==0.4.18
# OR
faiss-cpu==1.7.4

# Graph
networkx==3.2.1

# LLM
openai==1.6.1
google-generativeai==0.3.1

# ML
scikit-learn==1.3.2
sentence-transformers==2.2.2  # If using local embeddings

# Utilities
pydantic==2.5.3
tenacity==8.2.3
```

### 9.2 File Paths

```
~/.hva/
  memory/
    memory.db                    # SQLite database
    vector_store/                # Chroma/FAISS index
    graph.gpickle                # NetworkX graph (serialized)
    classifier_model.pkl         # Trained classification model
    cache/                       # Temporary cache
    exports/                     # Generated exports
    logs/                        # System logs
```

### 9.3 Configuration

```python
# tools/memory/config.py

from pydantic import BaseModel

class MemoryConfig(BaseModel):
    """Memory system configuration"""
    
    # Storage
    db_path: str = "~/.hva/memory/memory.db"
    vector_store_path: str = "~/.hva/memory/vector_store"
    graph_path: str = "~/.hva/memory/graph.gpickle"
    
    # Vector DB
    vector_db_type: str = "chroma"  # or "faiss"
    embedding_model: str = "text-embedding-3-small"
    embedding_dimensions: int = 1536
    
    # Search
    default_search_mode: str = "hybrid"
    semantic_threshold: float = 0.7
    max_search_results: int = 10
    
    # Classification
    enable_ml_classification: bool = True
    retrain_frequency: int = 50  # corrections before retrain
    
    # Maintenance
    duplicate_similarity_threshold: float = 0.9
    archive_after_days: int = 180
    permanent_delete_after_days: int = 90
    
    # Performance
    enable_caching: bool = True
    cache_size: int = 100
    batch_size: int = 50
    
    # Privacy
    default_sensitivity: str = "public"
    auto_detect_sensitive: bool = True
    encrypt_private: bool = True
    
    # Sync
    enable_sheets_sync: bool = False
    sheets_id: Optional[str] = None
    sync_public_only: bool = True
    
    # LLM
    summarization_model: str = "gemini-1.5-flash"
    classification_model: str = "gpt-4o-mini"
```

---

## 10. TESTING REQUIREMENTS

### 10.1 Unit Tests

```python
# tests/test_memory_system.py

import pytest
from tools.memory import MemorySystem, Memory, MemoryType

class TestMemoryCapture:
    
    @pytest.mark.asyncio
    async def test_capture_from_voice(self):
        """Test voice note capture"""
        system = MemorySystem()
        
        result = await system.capture_from_voice(
            text="احفظ فكرة: استخدام PostgreSQL للمشروع",
            language="ar"
        )
        
        assert result["memory_id"] is not None
        assert result["project"] is not None
    
    @pytest.mark.asyncio
    async def test_import_chatgpt_conversation(self):
        """Test ChatGPT import"""
        system = MemorySystem()
        
        conversation = """
        User: What database should we use?
        Assistant: For your use case, PostgreSQL would be ideal...
        """
        
        result = await system.import_conversation(
            content=conversation,
            format="text",
            source="chatgpt"
        )
        
        assert result["memories_created"] > 0

class TestClassification:
    
    @pytest.mark.asyncio
    async def test_project_classification(self):
        """Test project detection"""
        classifier = SmartClassifier()
        
        text = "We need to update the Mind-Q database schema"
        classification = await classifier.classify(text)
        
        assert classification.project == "Mind-Q"
        assert classification.confidence > 0.8
    
    @pytest.mark.asyncio
    async def test_learning_from_correction(self):
        """Test that system learns from corrections"""
        classifier = SmartClassifier()
        
        # Make initial classification
        result1 = await classifier.classify("Update the coaching platform")
        
        # User corrects
        await classifier.learn_from_correction(
            original="Update the coaching platform",
            corrected=Classification(project="AI Coach Mastery", ...)
        )
        
        # Next time should be more accurate
        result2 = await classifier.classify("Update the coaching platform")
        assert result2.confidence > result1.confidence

class TestRetrieval:
    
    @pytest.mark.asyncio
    async def test_semantic_search(self):
        """Test semantic search finds related content"""
        system = MemorySystem()
        
        # Save a memory
        await system.save_memory(Memory(
            ultra_brief="Decided to use PostgreSQL",
            ...
        ))
        
        # Search with different wording
        results = await system.search("What database did we choose?")
        
        assert len(results) > 0
        assert "PostgreSQL" in results[0].ultra_brief
    
    @pytest.mark.asyncio
    async def test_graph_traversal(self):
        """Test knowledge graph connections"""
        system = MemorySystem()
        
        mem1 = await system.save_memory(Memory(
            ultra_brief="Initial idea: use SQLite",
            ...
        ))
        
        mem2 = await system.save_memory(Memory(
            ultra_brief="Evolved to: use PostgreSQL",
            parent_memory_id=mem1.id,
            ...
        ))
        
        evolution = await system.trace_evolution(mem1.id)
        assert mem2.id in [m.id for m in evolution["evolved_into"]]

class TestConflictDetection:
    
    @pytest.mark.asyncio
    async def test_conflict_detected(self):
        """Test system detects contradictions"""
        system = MemorySystem()
        
        await system.save_memory(Memory(
            ultra_brief="Decided to use SQLite",
            type=MemoryType.DECISION,
            ...
        ))
        
        # Try to save conflicting decision
        with pytest.raises(ConflictError):
            await system.save_memory(Memory(
                ultra_brief="Decided to use PostgreSQL",
                type=MemoryType.DECISION,
                ...
            ), auto_resolve=False)
```

### 10.2 Integration Tests

```python
class TestFullWorkflow:
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_complete_flow(self):
        """Test end-to-end workflow"""
        system = MemorySystem()
        
        # 1. Capture from voice
        capture_result = await system.capture_from_voice(
            text="احفظ فكرة: نحتاج قاعدة بيانات جديدة للمشروع",
            language="ar"
        )
        memory_id = capture_result["memory_id"]
        
        # 2. Search for it
        results = await system.search("قاعدة بيانات")
        assert any(r.id == memory_id for r in results)
        
        # 3. Export to Markdown
        markdown = await system.export_to_markdown(
            filters={"project": capture_result["project"]}
        )
        assert memory_id in markdown
        
        # 4. Generate insights
        insights = await system.generate_insights(period="week")
        assert insights["total_memories"] > 0
```

### 10.3 Performance Tests

```python
@pytest.mark.performance
class TestPerformance:
    
    @pytest.mark.asyncio
    async def test_search_latency(self, benchmark):
        """Test search meets < 1s target"""
        system = MemorySystem()
        
        # Populate with 1000 memories
        for i in range(1000):
            await system.save_memory(Memory(...))
        
        # Benchmark search
        result = benchmark(
            lambda: asyncio.run(system.search("database"))
        )
        
        assert result.stats["mean"] < 1.0  # < 1 second
    
    @pytest.mark.asyncio
    async def test_import_performance(self):
        """Test ChatGPT import meets < 10s target"""
        system = MemorySystem()
        
        # Generate 50-message conversation
        conversation = generate_test_conversation(50)
        
        start = time.time()
        await system.import_conversation(conversation, format="text")
        duration = time.time() - start
        
        assert duration < 10.0  # < 10 seconds
```

---

## 11. ACCEPTANCE CRITERIA

The Memory System is **complete and correct** when:

### 11.1 Functional Criteria

- [ ] **Input Capture:**
  - Voice capture works (Arabic + English)
  - ChatGPT import works (JSON + text)
  - Gemini import works (text)
  - Image/file/URL capture works

- [ ] **Processing:**
  - Multi-level summarization accurate
  - Auto-classification ≥ 80% accuracy
  - Knowledge extraction comprehensive
  - Conflict detection reliable

- [ ] **Storage:**
  - SQLite + Vector DB + Graph all working
  - Data integrity maintained
  - Optional Sheets sync works

- [ ] **Retrieval:**
  - Semantic search accurate (≥ 70% relevance)
  - Hybrid search better than individual modes
  - Graph traversal correct
  - Context injection useful

- [ ] **Maintenance:**
  - Duplicate detection works
  - Archiving preserves data
  - Insights reports meaningful

- [ ] **Export:**
  - Markdown export clean
  - PDF professional
  - Notion/Obsidian compatible

### 11.2 Performance Criteria

- [ ] Voice capture → save: **< 3 seconds** (95th percentile)
- [ ] ChatGPT import (50 msgs): **< 10 seconds**
- [ ] Semantic search: **< 1 second** (95th percentile)
- [ ] Hybrid search: **< 1.5 seconds** (95th percentile)
- [ ] Context generation: **< 2 seconds**
- [ ] Export (100 memories): **< 3 seconds**

### 11.3 Intelligence Criteria

- [ ] Auto-classification accuracy: **≥ 80%**
- [ ] Conflict detection: **≥ 90%** recall
- [ ] Related memory suggestions: **≥ 70%** relevance
- [ ] Learning from corrections: Observable improvement

### 11.4 Security Criteria

- [ ] Sensitive content auto-detected
- [ ] Private memories encrypted
- [ ] No plain-text passwords stored
- [ ] Encryption keys in Keychain

### 11.5 Testing Criteria

- [ ] Unit test coverage: **≥ 85%**
- [ ] All integration tests pass
- [ ] Performance benchmarks met
- [ ] Manual testing: ≥ 30 operations successful

---

## 12. BUILDER INSTRUCTIONS

### 12.1 Pre-Implementation Checklist

**Before writing ANY code, the builder MUST:**

1. **Read this entire SRS**
2. **Verify understanding of:**
   - Multi-level summarization strategy
   - Knowledge graph structure
   - Hybrid search approach
   - Conflict detection logic
   - Privacy model

3. **Set up environment:**
   ```bash
   # Create directories
   mkdir -p ~/.hva/memory/{vector_store,cache,exports,logs}
   
   # Activate venv
   source venv/bin/activate
   
   # Install dependencies
   pip install -r requirements_memory.txt
   ```

4. **Create implementation plan:**
   - Write `MEMORY_MODULE_IMPLEMENTATION_PLAN.md`
   - Break down into phases
   - Estimate time per phase
   - **Wait for user approval before coding**

### 12.2 Implementation Phases

**Phase 1: Foundation (Week 1)**
- Data models (`models/`)
- SQLite storage (`storage/sqlite_store.py`)
- Basic CRUD operations
- Configuration

**Phase 2: Intelligence (Week 2)**
- Multi-level summarization
- Smart classification
- Knowledge extraction
- Vector DB integration

**Phase 3: Knowledge Graph (Week 2-3)**
- Graph structure
- Auto-linking algorithm
- Relationship detection
- Graph queries

**Phase 4: Retrieval (Week 3)**
- Semantic search
- Keyword search
- Hybrid search
- Smart ranking

**Phase 5: Advanced Features (Week 4)**
- Context injection
- Conflict detection
- Import/export
- Maintenance tasks

**Phase 6: Testing & Polish (Week 4)**
- Comprehensive tests
- Performance optimization
- Documentation
- Integration with HVA core

### 12.3 Development Guidelines

**Code Style:**
```python
# Type hints everywhere
async def save_memory(
    self,
    memory: Memory,
    sync_to_sheets: bool = False
) -> SaveResult:
    """
    Save memory to all storage layers
    
    Args:
        memory: Complete memory object
        sync_to_sheets: Whether to sync to Google Sheets
    
    Returns:
        SaveResult with memory_id and status
    
    Raises:
        StorageError: If save fails
    """
    pass

# Structured logging
logger.info(
    "memory_saved",
    memory_id=memory.id,
    project=memory.project,
    type=memory.type.value,
    latency_ms=latency
)
```

**Async by Default:**
```python
# All I/O operations async
class MemorySystem:
    async def save_memory(self, memory: Memory):
        # Concurrent saves to different stores
        await asyncio.gather(
            self.sqlite_store.save(memory),
            self.vector_store.save(memory),
            self.knowledge_graph.add_node(memory)
        )
```

**Error Handling:**
```python
try:
    result = await self.save_memory(memory)
except StorageError as e:
    logger.error("Save failed", error=str(e), memory_id=memory.id)
    raise MemorySystemError(
        message=f"Failed to save memory: {e}",
        details={"memory_id": memory.id},
        suggestion="Check disk space and database integrity",
        recoverable=True
    )
```

### 12.4 Testing Protocol

**Run tests before each commit:**
```bash
# Unit tests
pytest tests/test_memory_system.py -v

# Integration tests
pytest tests/ -v -m integration

# Performance tests
pytest tests/ -v -m performance

# Coverage
pytest --cov=tools.memory --cov-report=html --cov-report=term
```

**Coverage requirements:**
- Overall: ≥ 85%
- Critical paths: 100% (save, search, classify)

### 12.5 Documentation Requirements

**Each module:**
- Module docstring
- Class docstrings
- Function docstrings (with examples)
- Inline comments for complex logic

**README.md:**
- Quick start guide
- Configuration options
- Usage examples
- Troubleshooting
- Architecture diagram

### 12.6 Final Checklist

Before marking as complete:

- [ ] All functional requirements implemented
- [ ] All performance targets met
- [ ] All security measures in place
- [ ] Test coverage ≥ 85%
- [ ] Documentation complete
- [ ] Voice commands tested (Arabic + English)
- [ ] ChatGPT import tested with real conversations
- [ ] Knowledge graph visualized (sanity check)
- [ ] Manual testing: ≥ 30 operations
- [ ] Integration with HVA core verified
- [ ] Code reviewed
- [ ] Performance profiled

---

## APPENDIX A: Example Conversation Import

**Input (ChatGPT Conversation):**
```
User: I'm thinking about the database architecture for Mind-Q. What would you recommend?