import urllib.parse
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from database import get_db, BASE_DIR
import models
from auth import get_current_admin

router = APIRouter(tags=["notice"])

TEMPLATES_DIR = BASE_DIR / "templates"
UPLOAD_DIR = BASE_DIR / "static" / "uploads"

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


@router.get("/notices", response_class=HTMLResponse)
def notice_list(
    request: Request,
    page: int = 1,
    q: Optional[str] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """공지사항 목록 페이지"""
    admin = get_current_admin(request, db)
    page_size = 10
    query = db.query(models.Post)

    if category and category.strip():
        query = query.filter(models.Post.category == category.strip())
    if q and q.strip():
        query = query.filter(models.Post.title.contains(q.strip()) | models.Post.content.contains(q.strip()))

    total_count = query.count()
    total_pages = max(1, (total_count + page_size - 1) // page_size)
    if page < 1:
        page = 1
    elif page > total_pages:
        page = total_pages

    posts = query.order_by(models.Post.id.desc()).offset((page - 1) * page_size).limit(page_size).all()

    return templates.TemplateResponse(
        request=request,
        name="mainpages/notice.html",
        context={
            "title": "알림게시판 - IYCF 국제청소년문화재단",
            "posts": posts,
            "current_page": page,
            "total_pages": total_pages,
            "total_count": total_count,
            "q": q or "",
            "category": category or "",
            "admin": admin
        }
    )


@router.get("/notices/{post_id}", response_class=HTMLResponse)
def notice_detail(
    post_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """공지사항 상세 보기 페이지"""
    admin = get_current_admin(request, db)
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")

    # 조회수 증가
    post.hit_count = (post.hit_count or 0) + 1
    db.commit()

    # 이전글 / 다음글 조회
    prev_post = db.query(models.Post).filter(models.Post.id < post_id).order_by(models.Post.id.desc()).first()
    next_post = db.query(models.Post).filter(models.Post.id > post_id).order_by(models.Post.id.asc()).first()

    return templates.TemplateResponse(
        request=request,
        name="mainpages/notice_detail.html",
        context={
            "title": f"{post.title} - IYCF 알림게시판",
            "post": post,
            "prev_post": prev_post,
            "next_post": next_post,
            "admin": admin
        }
    )


@router.get("/download/{attachment_id}")
def download_attachment(
    attachment_id: int,
    db: Session = Depends(get_db)
):
    """첨부파일 다운로드"""
    attachment = db.query(models.Attachment).filter(models.Attachment.id == attachment_id).first()
    if not attachment:
        raise HTTPException(status_code=404, detail="첨부파일을 찾을 수 없습니다.")

    file_path = UPLOAD_DIR / attachment.stored_filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="서버에 파일이 존재하지 않습니다.")

    # 한글 파일명 인코딩 (RFC 5987)
    encoded_filename = urllib.parse.quote(attachment.original_filename)

    headers = {
        "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"
    }

    return FileResponse(
        path=str(file_path),
        filename=attachment.original_filename,
        headers=headers
    )
