import hashlib
import hmac
import secrets
from typing import Optional
from fastapi import Request, Depends
from sqlalchemy.orm import Session
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

from database import get_db
import models

SECRET_KEY = "iycf-youth-culture-auth-secret-key-change-in-prod"
COOKIE_NAME = "admin_session"

serializer = URLSafeTimedSerializer(SECRET_KEY, salt="iycf-auth-salt")


def hash_password(password: str) -> str:
    """비밀번호를 PBKDF2-HMAC-SHA256 알고리즘으로 안전하게 해시합니다."""
    salt = secrets.token_hex(16)
    pw_hash = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100_000).hex()
    return f"{salt}:{pw_hash}"


def verify_password(stored_password: str, provided_password: str) -> bool:
    """저장된 해시와 입력된 비밀번호를 비교합니다."""
    try:
        salt, pw_hash = stored_password.split(":")
        check_hash = hashlib.pbkdf2_hmac("sha256", provided_password.encode("utf-8"), salt.encode("utf-8"), 100_000).hex()
        return hmac.compare_digest(pw_hash, check_hash)
    except Exception:
        return False


def create_session_token(username: str) -> str:
    """사용자 이름이 서명된 세션 토큰을 생성합니다."""
    return serializer.dumps({"sub": username})


def decode_session_token(token: str, max_age: int = 60 * 60 * 24 * 7) -> Optional[str]:
    """세션 토큰을 검증하고 사용자 이름을 반환합니다. (기본 유효기간: 7일)"""
    try:
        data = serializer.loads(token, max_age=max_age)
        return data.get("sub")
    except (BadSignature, SignatureExpired, Exception):
        return None


def get_current_admin(request: Request, db: Session = Depends(get_db)) -> Optional[models.AdminUser]:
    """쿠키에서 관리자 세션을 확인하여 관리자 객체를 반환합니다 (미인증 시 None)."""
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        return None
    username = decode_session_token(token)
    if not username:
        return None
    admin = db.query(models.AdminUser).filter(models.AdminUser.username == username).first()
    return admin
