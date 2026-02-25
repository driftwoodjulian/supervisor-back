from pydantic import BaseModel, Field, field_validator, ValidationInfo
from typing import List, Optional
from enum import Enum

class ScoreEnum(str, Enum):
    GREAT = "great"
    GOOD = "good"
    NEUTRAL = "neutral"
    BAD = "bad"
    HORRIBLE = "horrible"

class EvaluationSubmission(BaseModel):
    chat_id: int
    score: ScoreEnum
    reason: str = Field(default="", max_length=500, description="Spanish text explaining the choice.")
    improvement: str = Field(default="", max_length=1000, description="Spanish text on how the operator can improve.")
    key_messages: Optional[List[int]] = Field(default=[], description="Indices of Support Agent messages that directly triggered this score.")

    @field_validator('key_messages')
    @classmethod
    def check_key_messages(cls, v: List[int], info: ValidationInfo) -> List[int]:
        values = info.data
        score = values.get('score')
        
        # Mandatory test: If score is 'bad' or 'horrible', 'key_messages' MUST contain at least one message index.
        if score in [ScoreEnum.BAD, ScoreEnum.HORRIBLE]:
            if not v or len(v) == 0:
                raise ValueError("Key messages are mandatory for 'Bad' or 'Horrible' scores.")
        
        return v

class ChatCurationResponse(BaseModel):
    id: int
    finished_at: Optional[str] # ISO format
    raw_payload: str # The exact text sent to AI
