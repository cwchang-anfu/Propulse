"""
API Dependencies
API 依賴與認證中間件
"""
from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError
from app.database import get_db
from app.models.user import User
from app.utils.security import decode_access_token
from app.schemas.user import TokenData

# OAuth2 密碼流
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    """
    取得當前已認證的使用者

    Args:
        db: 資料庫 Session
        token: JWT Token

    Returns:
        當前使用者

    Raises:
        HTTPException: 當 Token 無效或使用者不存在時
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # 解碼 Token
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    email: str = payload.get("sub")
    if email is None:
        raise credentials_exception

    # 查詢使用者
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception

    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    取得當前活躍的使用者（可擴展為檢查帳號是否被停用）

    Args:
        current_user: 當前使用者

    Returns:
        當前活躍使用者
    """
    # 未來可以在這裡加入帳號狀態檢查
    return current_user


def check_subscription_tier(required_tier: str):
    """
    檢查使用者訂閱等級的依賴工廠

    Args:
        required_tier: 所需的最低訂閱等級

    Returns:
        依賴函數
    """
    tier_hierarchy = {
        "free": 0,
        "pro": 1,
        "business": 2,
        "enterprise": 3
    }

    def check_tier(current_user: User = Depends(get_current_active_user)) -> User:
        user_tier_level = tier_hierarchy.get(current_user.subscription_tier.value, 0)
        required_tier_level = tier_hierarchy.get(required_tier, 0)

        if user_tier_level < required_tier_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"This feature requires {required_tier} subscription or higher"
            )

        return current_user

    return check_tier
