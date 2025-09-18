from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, Literal

class FeedbackIn(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    type: Literal["bug","idea","question"]
    description: Optional[str] = None
    page_url: Optional[HttpUrl] = None
    user_agent: Optional[str] = None

class StatusIn(BaseModel):
    status: Literal["open","review","resolved","rejected"]
