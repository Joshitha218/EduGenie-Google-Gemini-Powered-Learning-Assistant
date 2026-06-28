from datetime import datetime
from pydantic import BaseModel
from typing import List, Any, Dict

class QueryHistoryItem(BaseModel):
    QueryID: int
    QueryType: str
    QueryText: str
    CreatedAt: datetime
    ModelUsed: str | None = None
    ResponsePreview: str | None = None

    class Config:
        from_attributes = True

class HistoryDetail(BaseModel):
    QueryID: int
    QueryType: str
    QueryText: str
    CreatedAt: datetime
    ResponseText: str
    ModelUsed: str
    Details: Dict[str, Any] = {}

    class Config:
        from_attributes = True

class DashboardStats(BaseModel):
    total_queries: int
    queries_by_type: Dict[str, int]
    recent_activity: List[QueryHistoryItem]
