import os
from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.middleware.auth_middleware import get_current_user_view, get_current_user_optional
from backend.app.models.user import User

router = APIRouter(tags=["UI Views"])

# Configure Jinja2 templates directory
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates_dir = os.path.join(current_dir, "templates")
templates = Jinja2Templates(directory=templates_dir)
templates.env.cache = None

@router.get("/")
def home_page(request: Request, user: User | None = Depends(get_current_user_optional)):
    return templates.TemplateResponse(request=request, name="home.html", context={"user": user})

@router.get("/login")
def login_page(request: Request, user: User | None = Depends(get_current_user_optional)):
    if user:
        return RedirectResponse(url="/dashboard", status_code=303)
    return templates.TemplateResponse(request=request, name="login.html", context={"user": None})

@router.get("/signup")
def signup_page(request: Request, user: User | None = Depends(get_current_user_optional)):
    if user:
        return RedirectResponse(url="/dashboard", status_code=303)
    return templates.TemplateResponse(request=request, name="signup.html", context={"user": None})

@router.get("/dashboard")
def dashboard_page(request: Request, user = Depends(get_current_user_view)):
    if isinstance(user, RedirectResponse):
        return user
    return templates.TemplateResponse(request=request, name="dashboard.html", context={"user": user})

@router.get("/qa")
def qa_page(request: Request, user = Depends(get_current_user_view)):
    if isinstance(user, RedirectResponse):
        return user
    return templates.TemplateResponse(request=request, name="qa.html", context={"user": user})

@router.get("/explain")
def explain_page(request: Request, user = Depends(get_current_user_view)):
    if isinstance(user, RedirectResponse):
        return user
    return templates.TemplateResponse(request=request, name="explain.html", context={"user": user})

@router.get("/quiz")
def quiz_page(request: Request, user = Depends(get_current_user_view)):
    if isinstance(user, RedirectResponse):
        return user
    return templates.TemplateResponse(request=request, name="quiz.html", context={"user": user})

@router.get("/summary")
def summary_page(request: Request, user = Depends(get_current_user_view)):
    if isinstance(user, RedirectResponse):
        return user
    return templates.TemplateResponse(request=request, name="summary.html", context={"user": user})

@router.get("/roadmap")
def roadmap_page(request: Request, user = Depends(get_current_user_view)):
    if isinstance(user, RedirectResponse):
        return user
    return templates.TemplateResponse(request=request, name="roadmap.html", context={"user": user})

@router.get("/history")
def history_page(request: Request, user = Depends(get_current_user_view)):
    if isinstance(user, RedirectResponse):
        return user
    return templates.TemplateResponse(request=request, name="history.html", context={"user": user})

@router.get("/profile")
def profile_page(request: Request, user = Depends(get_current_user_view)):
    if isinstance(user, RedirectResponse):
        return user
    return templates.TemplateResponse(request=request, name="profile.html", context={"user": user})

