from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

BASE_DIR = Path(__file__).resolve().parent
DATABASE_URL = f"sqlite:///{BASE_DIR / 'youth_culture.db'}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """데이터베이스 테이블 생성 및 초기 기본 관리자 계정을 설정합니다."""
    import models
    from auth import hash_password

    # 테이블 생성
    Base.metadata.create_all(bind=engine)

    # 기본 관리자 계정 확인 및 생성
    db = SessionLocal()
    try:
        existing_admin = db.query(models.AdminUser).filter(models.AdminUser.username == "admin").first()
        if not existing_admin:
            default_admin = models.AdminUser(
                username="admin",
                password_hash=hash_password("admin1234!")
            )
            db.add(default_admin)
            db.commit()
            print("[INFO] 기본 관리자 계정이 생성되었습니다. (아이디: admin / 초기비밀번호: admin1234!)")
    finally:
        db.close()
