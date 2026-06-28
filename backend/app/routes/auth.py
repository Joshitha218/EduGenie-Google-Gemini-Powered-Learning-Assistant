from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.schemas.auth import UserCreate, UserLogin, UserResponse, Token
from backend.app.utils.security import verify_password, get_password_hash, create_access_token
from backend.app.middleware.auth_middleware import get_current_user_api, get_current_user_optional

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def signup(user_in: UserCreate, db: Session = Depends(get_db)):
    # Check if email is already taken
    existing_user = db.query(User).filter(User.Email == user_in.Email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists."
        )
    
    # Hash password and create user
    hashed_password = get_password_hash(user_in.Password)
    db_user = User(
        UserName=user_in.UserName,
        Email=user_in.Email,
        PasswordHash=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.post("/login", response_model=Token)
def login(response: Response, user_in: UserLogin, db: Session = Depends(get_db)):
    # Verify credentials
    user = db.query(User).filter(User.Email == user_in.Email).first()
    if not user or not verify_password(user_in.Password, user.PasswordHash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Generate JWT token
    access_token = create_access_token(data={"sub": user.Email, "user_id": user.UserID})
    
    # Set HTTP-only cookie for secure browser sessions
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=120 * 60,  # 120 minutes in seconds
        expires=120 * 60,
        samesite="lax",
        secure=False  # Set to True in production with HTTPS
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/logout")
def logout(response: Response):
    # Clear JWT cookie
    response.delete_cookie("access_token", path="/")
    return {"detail": "Logged out successfully."}

@router.get("/logout-redirect")
def logout_redirect(response: Response):
    # Logout and redirect to login page for templates
    response.delete_cookie("access_token", path="/")
    return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user_api)):
    return current_user
