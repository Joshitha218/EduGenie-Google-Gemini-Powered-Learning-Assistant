from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import json
from typing import List

from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.models.query import UserQuery
from backend.app.models.response import AIResponse
from backend.app.schemas.history import QueryHistoryItem, HistoryDetail, DashboardStats
from backend.app.middleware.auth_middleware import get_current_user_api

router = APIRouter(prefix="/api/history", tags=["History & Dashboard"])

@router.get("", response_model=List[QueryHistoryItem])
def get_user_history(
    current_user: User = Depends(get_current_user_api),
    db: Session = Depends(get_db)
):
    # Fetch queries sorted by creation time (newest first)
    queries = (
        db.query(UserQuery)
        .filter(UserQuery.UserID == current_user.UserID)
        .order_by(UserQuery.CreatedAt.desc())
        .all()
    )
    
    history_items = []
    for q in queries:
        # Get associated AI response to show model used and a preview
        model_used = "Unknown"
        preview = ""
        if q.ai_response:
            model_used = q.ai_response.ModelUsed
            try:
                # Attempt to extract text or preview from response
                data = json.loads(q.ai_response.ResponseText)
                if q.QueryType == "qa":
                    preview = data.get("Answer", "")[:100]
                elif q.QueryType == "explain":
                    preview = data.get("Definition", "")[:100]
                elif q.QueryType == "quiz":
                    preview = f"Generated Quiz with {len(data.get('Quizzes', []))} questions"
                elif q.QueryType == "summarize":
                    preview = data.get("Summary", "")[:100]
                elif q.QueryType == "learn":
                    preview = f"Learning path for '{data.get('Topic', q.QueryText)}'"
            except Exception:
                preview = q.ai_response.ResponseText[:100]
                
        history_items.append(
            QueryHistoryItem(
                QueryID=q.QueryID,
                QueryType=q.QueryType,
                QueryText=q.QueryText,
                CreatedAt=q.CreatedAt,
                ModelUsed=model_used,
                ResponsePreview=preview
            )
        )
    return history_items

@router.get("/{query_id}", response_model=HistoryDetail)
def get_history_detail(
    query_id: int,
    current_user: User = Depends(get_current_user_api),
    db: Session = Depends(get_db)
):
    query = (
        db.query(UserQuery)
        .filter(UserQuery.QueryID == query_id, UserQuery.UserID == current_user.UserID)
        .first()
    )
    if not query:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="History record not found."
        )
        
    response_text = ""
    model_used = ""
    details_dict = {}
    
    if query.ai_response:
        response_text = query.ai_response.ResponseText
        model_used = query.ai_response.ModelUsed
        try:
            details_dict = json.loads(query.ai_response.ResponseText)
        except Exception:
            details_dict = {"response": query.ai_response.ResponseText}
            
    return HistoryDetail(
        QueryID=query.QueryID,
        QueryType=query.QueryType,
        QueryText=query.QueryText,
        CreatedAt=query.CreatedAt,
        ResponseText=response_text,
        ModelUsed=model_used,
        Details=details_dict
    )

@router.get("/dashboard/stats", response_model=DashboardStats)
def get_dashboard_stats(
    current_user: User = Depends(get_current_user_api),
    db: Session = Depends(get_db)
):
    # Get total query count
    total_queries = db.query(UserQuery).filter(UserQuery.UserID == current_user.UserID).count()
    
    # Get query counts by type
    types = ["qa", "explain", "quiz", "summarize", "learn"]
    counts_by_type = {}
    for t in types:
        count = db.query(UserQuery).filter(UserQuery.UserID == current_user.UserID, UserQuery.QueryType == t).count()
        counts_by_type[t] = count
        
    # Get recent queries (limit 5)
    recent_queries = (
        db.query(UserQuery)
        .filter(UserQuery.UserID == current_user.UserID)
        .order_by(UserQuery.CreatedAt.desc())
        .limit(5)
        .all()
    )
    
    recent_items = []
    for q in recent_queries:
        model_used = "Unknown"
        preview = ""
        if q.ai_response:
            model_used = q.ai_response.ModelUsed
            try:
                data = json.loads(q.ai_response.ResponseText)
                if q.QueryType == "qa":
                    preview = data.get("Answer", "")[:100]
                elif q.QueryType == "explain":
                    preview = data.get("Definition", "")[:100]
                elif q.QueryType == "quiz":
                    preview = f"Generated Quiz with {len(data.get('Quizzes', []))} questions"
                elif q.QueryType == "summarize":
                    preview = data.get("Summary", "")[:100]
                elif q.QueryType == "learn":
                    preview = f"Learning path for '{data.get('Topic', q.QueryText)}'"
            except Exception:
                preview = q.ai_response.ResponseText[:100]
                
        recent_items.append(
            QueryHistoryItem(
                QueryID=q.QueryID,
                QueryType=q.QueryType,
                QueryText=q.QueryText,
                CreatedAt=q.CreatedAt,
                ModelUsed=model_used,
                ResponsePreview=preview
            )
        )
        
    return DashboardStats(
        total_queries=total_queries,
        queries_by_type=counts_by_type,
        recent_activity=recent_items
    )
