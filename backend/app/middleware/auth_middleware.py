from fastapi import Request, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.utils.security import decode_access_token
from backend.app.models.user import User

async def get_current_user_optional(request: Request, db: Session = Depends(get_db)) -> User | None:
    """
    Extracts user from JWT token in cookies or headers, if present.
    """
    token = request.cookies.get("access_token")
    
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            
    if not token:
        return None
        
    payload = decode_access_token(token)
    if not payload:
        return None
        
    user_id = payload.get("user_id")
    if not user_id:
        return None
        
    user = db.query(User).filter(User.UserID == user_id).first()
    return user

async def get_current_user_api(user: User | None = Depends(get_current_user_optional)) -> User:
    """
    Enforces authentication for JSON API endpoints, raising a 401 error.
    """
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials, please log in."
        )
    return user

async def get_current_user_view(request: Request, user: User | None = Depends(get_current_user_optional)):
    """
    Enforces authentication for template views. Redirects to /login if not authenticated.
    """
    if not user:
        path = request.url.path
        if path not in ["/", "/login", "/signup"]:
            # Use HTTP 303 See Other to ensure the browser performs a GET redirect.
            return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    return user
