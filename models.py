from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class AdminUser(Base):
    __tablename__ = "admin_users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.now)


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String(50), default="공지사항", index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    author = Column(String(50), default="관리자")
    hit_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now, index=True)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    attachments = relationship("Attachment", back_populates="post", cascade="all, delete-orphan", order_by="Attachment.id")


class Attachment(Base):
    __tablename__ = "attachments"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), nullable=False, index=True)
    original_filename = Column(String(255), nullable=False)
    stored_filename = Column(String(255), nullable=False)
    file_size = Column(Integer, default=0)  # 단위: bytes
    created_at = Column(DateTime, default=datetime.now)

    post = relationship("Post", back_populates="attachments")


class CustomPage(Base):
    __tablename__ = "custom_pages"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(100), unique=True, nullable=False, index=True)  # URL 명칭 (예: jangsan)
    title = Column(String(200), nullable=False)                          # 관리용 페이지 제목
    stored_filename = Column(String(255), nullable=False)               # 저장된 파일명
    original_filename = Column(String(255), nullable=False)             # 원본 파일명
    mode = Column(String(20), default="integrated")                     # "integrated" (재단 레이아웃 내 삽입) 또는 "standalone" (독립 전체 페이지)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class MediaFile(Base):
    __tablename__ = "media_files"

    id = Column(Integer, primary_key=True, index=True)
    original_filename = Column(String(255), nullable=False)
    stored_filename = Column(String(255), nullable=False)
    file_size = Column(Integer, default=0)  # 단위: bytes
    file_url = Column(String(255), nullable=False)  # 웹에서 접근 가능한 경로 (/static/uploads/images/...)
    created_at = Column(DateTime, default=datetime.now)
