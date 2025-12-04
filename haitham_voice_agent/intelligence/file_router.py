import logging
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from haitham_voice_agent.tools.projects import project_manager

logger = logging.getLogger(__name__)

@dataclass
class FileProjectCandidate:
    project_id: str
    score: float
    reason: str

@dataclass
class FileRoutingResult:
    path: str
    candidates: List[FileProjectCandidate]
    predicted_type: Optional[str]
    confidence: float

class FileRouter:
    """
    Routes files to projects based on heuristics and semantics.
    """
    
    def __init__(self):
        pass
        
    async def classify_file(self, path: str) -> FileRoutingResult:
        """Classify a file against critical projects"""
        file_path = Path(path)
        filename = file_path.name.lower()
        
        # Get critical projects
        projects = await project_manager.list_critical_projects()
        candidates = []
        
        for project in projects:
            score = 0.0
            reasons = []
            
            # 1. Heuristic: Name Match
            # Check if project name or ID is in filename
            p_name = project["name"].lower()
            p_id = project["id"].lower()
            
            if p_name in filename or p_id in filename:
                score += 0.8
                reasons.append(f"Filename contains project name '{p_name}'")
            else:
                # Check for parts of the name (if multi-word)
                parts = p_name.split()
                if len(parts) > 1:
                    match_count = 0
                    for part in parts:
                        if len(part) > 2 and part in filename: # Ignore short words
                            match_count += 1
                    
                    if match_count > 0:
                        score += 1.0 * (match_count / len(parts))
                        reasons.append(f"Filename contains parts of project name")

            # Check tags
            for tag in project.get("tags", []):
                if tag.lower() in filename:
                    score += 0.4
                    reasons.append(f"Filename contains tag '{tag}'")
            
            # 2. Semantic: (Placeholder for now, would use Vector Store)
            # In a real implementation, we'd generate embedding for file content 
            # and compare with project profile embedding.
            
            if score > 0:
                # Cap score at 1.0
                final_score = min(score, 1.0)
                candidates.append(FileProjectCandidate(
                    project_id=project["id"],
                    score=final_score,
                    reason=", ".join(reasons)
                ))
        
        # Sort candidates
        candidates.sort(key=lambda x: x.score, reverse=True)
        
        # Determine confidence
        confidence = candidates[0].score if candidates else 0.0
        
        # Predict type
        predicted_type = self._predict_type(file_path)
        
        return FileRoutingResult(
            path=path,
            candidates=candidates,
            predicted_type=predicted_type,
            confidence=confidence
        )
        
    def _predict_type(self, path: Path) -> str:
        ext = path.suffix.lower()
        if ext in ['.pdf', '.doc', '.docx']: return "document"
        if ext in ['.jpg', '.png', '.jpeg']: return "image"
        if ext in ['.py', '.js', '.html', '.css']: return "code"
        if ext in ['.txt', '.md']: return "note"
        return "unknown"

# Singleton
file_router = FileRouter()
