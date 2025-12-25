from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Literal

class Message(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str

class ChatRecord(BaseModel):
    messages: List[Message]
    bucket: Literal[
        "ambiguity_handling", 
        "error_correction_dialogues", 
        "numeric_discipline", 
        "refuse_to_guess_source_needed", 
        "grounded_summaries"
    ]
    tags: List[str] = Field(default_factory=list)
    expected_check: Optional[Dict] = None 
