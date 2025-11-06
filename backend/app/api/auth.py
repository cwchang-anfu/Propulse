"""
Authentication API
使用者認證相關 API
"""
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, Token
from app.utils.security import verify_password, get_password_hash, create_access_token
from app.api.deps import get_current_active_user
from app.config import settings

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    """
    註冊新使用者

    Args:
        user_in: 使用者註冊資料
        db: 資料庫 Session

    Returns:
        建立的使用者資料

    Raises:
        HTTPException: 當 email 已被使用時
    """
    # 檢查 email 是否已存在
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # 建立新使用者
    user = User(
        email=user_in.email,
        password_hash=get_password_hash(user_in.password),
        full_name=user_in.full_name
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@router.post("/login", response_model=Token)
def login(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    使用者登入

    Args:
        db: 資料庫 Session
        form_data: OAuth2 密碼表單（username 為 email）

    Returns:
        JWT Access Token

    Raises:
        HTTPException: 當 email 或密碼錯誤時
    """
    # 查詢使用者
    user = db.query(User).filter(User.email == form_data.username).first()

    # 驗證密碼
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 建立 Access Token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )

    # 更新最後登入時間
    from sqlalchemy import func
    user.last_login = func.now()
    db.commit()

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """
    取得當前使用者資訊

    Args:
        current_user: 當前已認證的使用者

    Returns:
        使用者資料
    """
    return current_user
