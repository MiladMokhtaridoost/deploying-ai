from pydantic import BaseModel, Field
from typing import List

class WeatherSummary(BaseModel):
    location: str
    date: str
    summary: str
    high_c: float
    low_c: float
    advice: str

class SemanticAnswer(BaseModel):
    query: str
    top_passages: List[str]
    answer: str

class ToolResult(BaseModel):
    tool: str = Field(..., description="Name of the executed tool")
    result: str

