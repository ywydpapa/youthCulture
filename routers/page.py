import re
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from database import get_db, BASE_DIR
import models
from auth import get_current_admin

router = APIRouter(tags=["custom_page"])

TEMPLATES_DIR = BASE_DIR / "templates"
CUSTOM_PAGES_DIR = TEMPLATES_DIR / "custom_pages"

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


def parse_html_content(raw_html: str):
    """업로드된 HTML 문서에서 본문 내용과 스타일 태그를 지능적으로 분리합니다."""
    # style 태그들 추출
    styles = re.findall(r"(<style\b[^>]*>.*?</style>)", raw_html, flags=re.DOTALL | re.IGNORECASE)
    extra_head = "\n".join(styles)

    # body 내용 추출
    body_match = re.search(r"<body\b[^>]*>(.*?)</body>", raw_html, flags=re.DOTALL | re.IGNORECASE)
    if body_match:
        content = body_match.group(1).strip()
    else:
        content = re.sub(r"<!DOCTYPE[^>]*>", "", raw_html, flags=re.IGNORECASE)
        content = re.sub(r"</?html[^>]*>", "", content, flags=re.IGNORECASE)
        content = re.sub(r"<head\b[^>]*>.*?</head>", "", content, flags=re.DOTALL | re.IGNORECASE)
        content = content.strip()

    return content, extra_head


def render_custom_page_response(page: models.CustomPage, request: Request, admin: Optional[models.AdminUser] = None):
    """CustomPage 객체를 기반으로 HTMLResponse를 생성합니다."""
    file_path = CUSTOM_PAGES_DIR / page.stored_filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="업로드된 HTML 파일을 찾을 수 없습니다.")

    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        raw_html = f.read()

    # 모드 B: 단독 독립 모드 (HTML 원본 전체 출력)
    if page.mode == "standalone":
        return HTMLResponse(content=raw_html)

    # 모드 A: 재단 레이아웃 통합 모드 (헤더/메뉴/푸터 포함)
    content, extra_head = parse_html_content(raw_html)

    return templates.TemplateResponse(
        request=request,
        name="custom_pages/custom_base.html",
        context={
            "title": f"{page.title} - IYCF",
            "page_title": page.title,
            "page_content": content,
            "extra_head": extra_head,
            "admin": admin
        }
    )


@router.get("/p/{slug}", response_class=HTMLResponse)
def view_custom_page(
    slug: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """URL 슬러그 기반 커스텀 페이지 렌더링"""
    admin = get_current_admin(request, db)
    page = db.query(models.CustomPage).filter(models.CustomPage.slug == slug.strip().lower()).first()
    if not page:
        raise HTTPException(status_code=404, detail="요청하신 페이지를 찾을 수 없습니다.")

    return render_custom_page_response(page, request, admin)
