import os
import re
import uuid
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, Request, Depends, Form, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from database import get_db, BASE_DIR
import models
from auth import verify_password, hash_password, create_session_token, get_current_admin, COOKIE_NAME

router = APIRouter(prefix="/admin", tags=["admin"])

TEMPLATES_DIR = BASE_DIR / "templates"
UPLOAD_DIR = BASE_DIR / "static" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
CUSTOM_PAGES_DIR = TEMPLATES_DIR / "custom_pages"
CUSTOM_PAGES_DIR.mkdir(parents=True, exist_ok=True)
MEDIA_DIR = UPLOAD_DIR / "images"
MEDIA_DIR.mkdir(parents=True, exist_ok=True)
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".bmp"}

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# 보안: 업로드 차단 확장자 및 최대 파일 크기 (30MB)
BLOCKED_EXTENSIONS = {".exe", ".bat", ".cmd", ".sh", ".php", ".phtml", ".js", ".vbs", ".py", ".ps1", ".jar", ".msi", ".dll"}
MAX_FILE_SIZE = 30 * 1024 * 1024  # 30 MB


def validate_upload_file(file: UploadFile) -> Optional[str]:
    """업로드 파일의 확장자 및 유효성을 검사합니다."""
    if not file or not file.filename or not file.filename.strip():
        return None
    ext = Path(file.filename).suffix.lower()
    if ext in BLOCKED_EXTENSIONS:
        return f"보안상 실행 가능 파일({ext})은 업로드할 수 없습니다."
    return None


# -----------------------------
# 로그인 / 로그아웃
# -----------------------------
@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request, db: Session = Depends(get_db)):
    admin = get_current_admin(request, db)
    if admin:
        return RedirectResponse(url="/admin/posts", status_code=302)
    return templates.TemplateResponse(
        request=request,
        name="admin/login.html",
        context={"title": "관리자 로그인 - IYCF", "error": None}
    )


@router.post("/login", response_class=HTMLResponse)
def login_action(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    admin = db.query(models.AdminUser).filter(models.AdminUser.username == username.strip()).first()
    if not admin or not verify_password(admin.password_hash, password):
        return templates.TemplateResponse(
            request=request,
            name="admin/login.html",
            context={
                "title": "관리자 로그인 - IYCF",
                "error": "아이디 또는 비밀번호가 올바르지 않습니다.",
                "username": username
            },
            status_code=400
        )

    response = RedirectResponse(url="/admin/posts", status_code=302)
    token = create_session_token(admin.username)
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        httponly=True,
        samesite="lax",
        max_age=60 * 60 * 24 * 7  # 7일
    )
    return response


@router.get("/logout")
def logout_action():
    response = RedirectResponse(url="/", status_code=302)
    response.delete_cookie(COOKIE_NAME)
    return response


# -----------------------------
# 비밀번호 변경
# -----------------------------
@router.get("/change-password", response_class=HTMLResponse)
def change_password_page(request: Request, db: Session = Depends(get_db)):
    admin = get_current_admin(request, db)
    if not admin:
        return RedirectResponse(url="/admin/login", status_code=302)

    return templates.TemplateResponse(
        request=request,
        name="admin/change_password.html",
        context={"title": "비밀번호 변경 - IYCF 관리자", "admin": admin, "error": None, "success": None}
    )


@router.post("/change-password", response_class=HTMLResponse)
def change_password_action(
    request: Request,
    current_password: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...),
    db: Session = Depends(get_db)
):
    admin = get_current_admin(request, db)
    if not admin:
        return RedirectResponse(url="/admin/login", status_code=302)

    if not verify_password(admin.password_hash, current_password):
        return templates.TemplateResponse(
            request=request,
            name="admin/change_password.html",
            context={"title": "비밀번호 변경 - IYCF 관리자", "admin": admin, "error": "현재 비밀번호가 일치하지 않습니다.", "success": None},
            status_code=400
        )

    if len(new_password) < 6:
        return templates.TemplateResponse(
            request=request,
            name="admin/change_password.html",
            context={"title": "비밀번호 변경 - IYCF 관리자", "admin": admin, "error": "새 비밀번호는 최소 6자 이상이어야 합니다.", "success": None},
            status_code=400
        )

    if new_password != confirm_password:
        return templates.TemplateResponse(
            request=request,
            name="admin/change_password.html",
            context={"title": "비밀번호 변경 - IYCF 관리자", "admin": admin, "error": "새 비밀번호와 확인 비밀번호가 일치하지 않습니다.", "success": None},
            status_code=400
        )

    admin.password_hash = hash_password(new_password)
    db.commit()

    return templates.TemplateResponse(
        request=request,
        name="admin/change_password.html",
        context={"title": "비밀번호 변경 - IYCF 관리자", "admin": admin, "error": None, "success": "비밀번호가 성공적으로 변경되었습니다."}
    )


# -----------------------------
# 게시글 관리 (목록)
# -----------------------------
@router.get("/posts", response_class=HTMLResponse)
def admin_posts_list(
    request: Request,
    page: int = 1,
    q: Optional[str] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    admin = get_current_admin(request, db)
    if not admin:
        return RedirectResponse(url="/admin/login", status_code=302)

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
        name="admin/posts.html",
        context={
            "title": "게시글 관리 - IYCF 관리자",
            "posts": posts,
            "current_page": page,
            "total_pages": total_pages,
            "total_count": total_count,
            "q": q or "",
            "category": category or "",
            "admin": admin
        }
    )


# -----------------------------
# 게시글 등록
# -----------------------------
@router.get("/posts/new", response_class=HTMLResponse)
def admin_post_new_form(request: Request, db: Session = Depends(get_db)):
    admin = get_current_admin(request, db)
    if not admin:
        return RedirectResponse(url="/admin/login", status_code=302)

    return templates.TemplateResponse(
        request=request,
        name="admin/post_form.html",
        context={
            "title": "새 게시글 작성 - IYCF 관리자",
            "post": None,
            "is_edit": False,
            "admin": admin,
            "error": None
        }
    )


@router.post("/posts/new")
def admin_post_create(
    request: Request,
    title: str = Form(...),
    category: str = Form("공지사항"),
    content: str = Form(...),
    files: List[UploadFile] = File([]),
    db: Session = Depends(get_db)
):
    admin = get_current_admin(request, db)
    if not admin:
        return RedirectResponse(url="/admin/login", status_code=302)

    # 파일 확장자 검사
    for uploaded_file in files:
        err = validate_upload_file(uploaded_file)
        if err:
            return templates.TemplateResponse(
                request=request,
                name="admin/post_form.html",
                context={
                    "title": "새 게시글 작성 - IYCF 관리자",
                    "post": None,
                    "is_edit": False,
                    "admin": admin,
                    "error": err
                },
                status_code=400
            )

    new_post = models.Post(
        title=title.strip(),
        category=category.strip(),
        content=content.strip(),
        author=admin.username
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    # 첨부파일 저장
    for uploaded_file in files:
        if uploaded_file and uploaded_file.filename and uploaded_file.filename.strip():
            orig_name = uploaded_file.filename
            ext = Path(orig_name).suffix
            stored_name = f"{uuid.uuid4().hex}{ext}"
            file_dest = UPLOAD_DIR / stored_name

            file_content = uploaded_file.file.read()
            if len(file_content) > MAX_FILE_SIZE:
                continue

            with open(file_dest, "wb") as f:
                f.write(file_content)

            attachment = models.Attachment(
                post_id=new_post.id,
                original_filename=orig_name,
                stored_filename=stored_name,
                file_size=len(file_content)
            )
            db.add(attachment)

    db.commit()
    return RedirectResponse(url="/admin/posts", status_code=302)


# -----------------------------
# 게시글 수정
# -----------------------------
@router.get("/posts/{post_id}/edit", response_class=HTMLResponse)
def admin_post_edit_form(post_id: int, request: Request, db: Session = Depends(get_db)):
    admin = get_current_admin(request, db)
    if not admin:
        return RedirectResponse(url="/admin/login", status_code=302)

    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")

    return templates.TemplateResponse(
        request=request,
        name="admin/post_form.html",
        context={
            "title": f"게시글 수정 (#{post.id}) - IYCF 관리자",
            "post": post,
            "is_edit": True,
            "admin": admin,
            "error": None
        }
    )


@router.post("/posts/{post_id}/edit")
def admin_post_update(
    post_id: int,
    request: Request,
    title: str = Form(...),
    category: str = Form("공지사항"),
    content: str = Form(...),
    delete_attachments: List[int] = Form([]),
    files: List[UploadFile] = File([]),
    db: Session = Depends(get_db)
):
    admin = get_current_admin(request, db)
    if not admin:
        return RedirectResponse(url="/admin/login", status_code=302)

    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")

    # 파일 확장자 검사
    for uploaded_file in files:
        err = validate_upload_file(uploaded_file)
        if err:
            return templates.TemplateResponse(
                request=request,
                name="admin/post_form.html",
                context={
                    "title": f"게시글 수정 (#{post.id}) - IYCF 관리자",
                    "post": post,
                    "is_edit": True,
                    "admin": admin,
                    "error": err
                },
                status_code=400
            )

    post.title = title.strip()
    post.category = category.strip()
    post.content = content.strip()

    # 삭제 체크된 첨부파일 제거
    if delete_attachments:
        attachments_to_delete = db.query(models.Attachment).filter(
            models.Attachment.id.in_(delete_attachments),
            models.Attachment.post_id == post_id
        ).all()
        for att in attachments_to_delete:
            stored_file = UPLOAD_DIR / att.stored_filename
            if stored_file.exists():
                try:
                    stored_file.unlink()
                except Exception:
                    pass
            db.delete(att)

    # 신규 추가된 첨부파일 저장
    for uploaded_file in files:
        if uploaded_file and uploaded_file.filename and uploaded_file.filename.strip():
            orig_name = uploaded_file.filename
            ext = Path(orig_name).suffix
            stored_name = f"{uuid.uuid4().hex}{ext}"
            file_dest = UPLOAD_DIR / stored_name

            file_content = uploaded_file.file.read()
            if len(file_content) > MAX_FILE_SIZE:
                continue

            with open(file_dest, "wb") as f:
                f.write(file_content)

            attachment = models.Attachment(
                post_id=post.id,
                original_filename=orig_name,
                stored_filename=stored_name,
                file_size=len(file_content)
            )
            db.add(attachment)

    db.commit()
    return RedirectResponse(url="/admin/posts", status_code=302)


# -----------------------------
# 게시글 삭제
# -----------------------------
@router.post("/posts/{post_id}/delete")
def admin_post_delete(post_id: int, request: Request, db: Session = Depends(get_db)):
    admin = get_current_admin(request, db)
    if not admin:
        return RedirectResponse(url="/admin/login", status_code=302)

    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if post:
        for att in post.attachments:
            stored_file = UPLOAD_DIR / att.stored_filename
            if stored_file.exists():
                try:
                    stored_file.unlink()
                except Exception:
                    pass
        db.delete(post)
        db.commit()

    return RedirectResponse(url="/admin/posts", status_code=302)


# -----------------------------
# 커스텀 HTML 페이지 관리
# -----------------------------
@router.get("/pages", response_class=HTMLResponse)
def admin_pages_list(request: Request, db: Session = Depends(get_db)):
    admin = get_current_admin(request, db)
    if not admin:
        return RedirectResponse(url="/admin/login", status_code=302)

    pages = db.query(models.CustomPage).order_by(models.CustomPage.id.desc()).all()

    return templates.TemplateResponse(
        request=request,
        name="admin/pages.html",
        context={
            "title": "HTML 페이지 관리 - IYCF 관리자",
            "pages": pages,
            "admin": admin
        }
    )


@router.get("/pages/new", response_class=HTMLResponse)
def admin_page_new_form(request: Request, db: Session = Depends(get_db)):
    admin = get_current_admin(request, db)
    if not admin:
        return RedirectResponse(url="/admin/login", status_code=302)

    return templates.TemplateResponse(
        request=request,
        name="admin/page_form.html",
        context={
            "title": "새 HTML 페이지 업로드 - IYCF 관리자",
            "page": None,
            "is_edit": False,
            "admin": admin,
            "error": None
        }
    )


@router.post("/pages/new")
def admin_page_create(
    request: Request,
    title: str = Form(...),
    slug: str = Form(...),
    mode: str = Form("integrated"),
    html_file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    admin = get_current_admin(request, db)
    if not admin:
        return RedirectResponse(url="/admin/login", status_code=302)

    clean_slug = slug.strip().lower()
    if not re.match(r"^[a-z0-9_-]+$", clean_slug):
        return templates.TemplateResponse(
            request=request,
            name="admin/page_form.html",
            context={
                "title": "새 HTML 페이지 업로드 - IYCF 관리자",
                "page": None,
                "is_edit": False,
                "admin": admin,
                "error": "페이지 경로명(Slug)은 영문 소문자, 숫자, 하이픈(-), 밑줄(_)만 가능합니다."
            },
            status_code=400
        )

    # 중복 slug 검사
    existing = db.query(models.CustomPage).filter(models.CustomPage.slug == clean_slug).first()
    if existing:
        return templates.TemplateResponse(
            request=request,
            name="admin/page_form.html",
            context={
                "title": "새 HTML 페이지 업로드 - IYCF 관리자",
                "page": None,
                "is_edit": False,
                "admin": admin,
                "error": f"경로명 '{clean_slug}'는 이미 사용 중입니다. 다른 명칭을 지정해 주세요."
            },
            status_code=400
        )

    # 파일 확장자 검사
    if not html_file or not html_file.filename:
        return templates.TemplateResponse(
            request=request,
            name="admin/page_form.html",
            context={
                "title": "새 HTML 페이지 업로드 - IYCF 관리자",
                "page": None,
                "is_edit": False,
                "admin": admin,
                "error": "HTML 파일을 선택해 주세요."
            },
            status_code=400
        )

    orig_name = html_file.filename
    ext = Path(orig_name).suffix.lower()
    if ext not in [".html", ".htm"]:
        return templates.TemplateResponse(
            request=request,
            name="admin/page_form.html",
            context={
                "title": "새 HTML 페이지 업로드 - IYCF 관리자",
                "page": None,
                "is_edit": False,
                "admin": admin,
                "error": "업로드 파일은 .html 또는 .htm 형식이어야 합니다."
            },
            status_code=400
        )

    # 파일 저장
    stored_name = f"{uuid.uuid4().hex}.html"
    dest = CUSTOM_PAGES_DIR / stored_name
    file_bytes = html_file.file.read()
    with open(dest, "wb") as f:
        f.write(file_bytes)

    new_page = models.CustomPage(
        title=title.strip(),
        slug=clean_slug,
        mode=mode.strip(),
        stored_filename=stored_name,
        original_filename=orig_name
    )
    db.add(new_page)
    db.commit()

    return RedirectResponse(url="/admin/pages", status_code=302)


@router.get("/pages/{page_id}/edit", response_class=HTMLResponse)
def admin_page_edit_form(page_id: int, request: Request, db: Session = Depends(get_db)):
    admin = get_current_admin(request, db)
    if not admin:
        return RedirectResponse(url="/admin/login", status_code=302)

    page = db.query(models.CustomPage).filter(models.CustomPage.id == page_id).first()
    if not page:
        raise HTTPException(status_code=404, detail="페이지를 찾을 수 없습니다.")

    return templates.TemplateResponse(
        request=request,
        name="admin/page_form.html",
        context={
            "title": f"HTML 페이지 수정 (#{page.id}) - IYCF 관리자",
            "page": page,
            "is_edit": True,
            "admin": admin,
            "error": None
        }
    )


@router.post("/pages/{page_id}/edit")
def admin_page_update(
    page_id: int,
    request: Request,
    title: str = Form(...),
    slug: str = Form(...),
    mode: str = Form("integrated"),
    html_file: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    admin = get_current_admin(request, db)
    if not admin:
        return RedirectResponse(url="/admin/login", status_code=302)

    page = db.query(models.CustomPage).filter(models.CustomPage.id == page_id).first()
    if not page:
        raise HTTPException(status_code=404, detail="페이지를 찾을 수 없습니다.")

    clean_slug = slug.strip().lower()
    if not re.match(r"^[a-z0-9_-]+$", clean_slug):
        return templates.TemplateResponse(
            request=request,
            name="admin/page_form.html",
            context={
                "title": f"HTML 페이지 수정 (#{page.id}) - IYCF 관리자",
                "page": page,
                "is_edit": True,
                "admin": admin,
                "error": "페이지 경로명(Slug)은 영문 소문자, 숫자, 하이픈(-), 밑줄(_)만 가능합니다."
            },
            status_code=400
        )

    # 중복 slug 검사 (자신 제외)
    existing = db.query(models.CustomPage).filter(models.CustomPage.slug == clean_slug, models.CustomPage.id != page_id).first()
    if existing:
        return templates.TemplateResponse(
            request=request,
            name="admin/page_form.html",
            context={
                "title": f"HTML 페이지 수정 (#{page.id}) - IYCF 관리자",
                "page": page,
                "is_edit": True,
                "admin": admin,
                "error": f"경로명 '{clean_slug}'는 이미 사용 중입니다."
            },
            status_code=400
        )

    page.title = title.strip()
    page.slug = clean_slug
    page.mode = mode.strip()

    # 신규 파일 업로드 시 교체
    if html_file and html_file.filename and html_file.filename.strip():
        ext = Path(html_file.filename).suffix.lower()
        if ext in [".html", ".htm"]:
            # 기존 파일 삭제
            old_file = CUSTOM_PAGES_DIR / page.stored_filename
            if old_file.exists():
                try:
                    old_file.unlink()
                except Exception:
                    pass

            stored_name = f"{uuid.uuid4().hex}.html"
            dest = CUSTOM_PAGES_DIR / stored_name
            with open(dest, "wb") as f:
                f.write(html_file.file.read())

            page.stored_filename = stored_name
            page.original_filename = html_file.filename

    db.commit()
    return RedirectResponse(url="/admin/pages", status_code=302)


@router.post("/pages/{page_id}/delete")
def admin_page_delete(page_id: int, request: Request, db: Session = Depends(get_db)):
    admin = get_current_admin(request, db)
    if not admin:
        return RedirectResponse(url="/admin/login", status_code=302)

    page = db.query(models.CustomPage).filter(models.CustomPage.id == page_id).first()
    if page:
        old_file = CUSTOM_PAGES_DIR / page.stored_filename
        if old_file.exists():
            try:
                old_file.unlink()
            except Exception:
                pass
        db.delete(page)
        db.commit()

    return RedirectResponse(url="/admin/pages", status_code=302)


@router.get("/pages/{page_id}/code", response_class=HTMLResponse)
def admin_page_code_editor(page_id: int, request: Request, db: Session = Depends(get_db)):
    admin = get_current_admin(request, db)
    if not admin:
        return RedirectResponse(url="/admin/login", status_code=302)

    page = db.query(models.CustomPage).filter(models.CustomPage.id == page_id).first()
    if not page:
        raise HTTPException(status_code=404, detail="페이지를 찾을 수 없습니다.")

    file_path = CUSTOM_PAGES_DIR / page.stored_filename
    html_code = ""
    if file_path.exists():
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            html_code = f.read()

    return templates.TemplateResponse(
        request=request,
        name="admin/page_code_editor.html",
        context={
            "title": f"HTML 코드 직접 편집 ({page.title}) - IYCF 관리자",
            "page": page,
            "html_code": html_code,
            "admin": admin,
            "success": None,
            "error": None
        }
    )


@router.post("/pages/{page_id}/code", response_class=HTMLResponse)
def admin_page_code_save(
    page_id: int,
    request: Request,
    html_code: str = Form(...),
    db: Session = Depends(get_db)
):
    admin = get_current_admin(request, db)
    if not admin:
        return RedirectResponse(url="/admin/login", status_code=302)

    page = db.query(models.CustomPage).filter(models.CustomPage.id == page_id).first()
    if not page:
        raise HTTPException(status_code=404, detail="페이지를 찾을 수 없습니다.")

    file_path = CUSTOM_PAGES_DIR / page.stored_filename
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html_code)

    return templates.TemplateResponse(
        request=request,
        name="admin/page_code_editor.html",
        context={
            "title": f"HTML 코드 직접 편집 ({page.title}) - IYCF 관리자",
            "page": page,
            "html_code": html_code,
            "admin": admin,
            "success": "HTML 소스코드가 성공적으로 저장되었습니다.",
            "error": None
        }
    )


# -----------------------------
# 미디어 / 이미지 관리 (Media Manager)
# -----------------------------
@router.get("/media", response_class=HTMLResponse)
def admin_media_list(
    request: Request,
    page: int = 1,
    q: Optional[str] = None,
    db: Session = Depends(get_db)
):
    admin = get_current_admin(request, db)
    if not admin:
        return RedirectResponse(url="/admin/login", status_code=302)

    page_size = 12
    query = db.query(models.MediaFile)
    if q and q.strip():
        query = query.filter(models.MediaFile.original_filename.contains(q.strip()))

    total_count = query.count()
    total_pages = max(1, (total_count + page_size - 1) // page_size)
    if page < 1:
        page = 1
    elif page > total_pages:
        page = total_pages

    media_files = query.order_by(models.MediaFile.id.desc()).offset((page - 1) * page_size).limit(page_size).all()

    return templates.TemplateResponse(
        request=request,
        name="admin/media.html",
        context={
            "title": "이미지 미디어 관리 - IYCF 관리자",
            "media_files": media_files,
            "current_page": page,
            "total_pages": total_pages,
            "total_count": total_count,
            "q": q or "",
            "admin": admin,
            "message": None,
            "error": None
        }
    )


@router.post("/media/upload")
def admin_media_upload(
    request: Request,
    images: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    admin = get_current_admin(request, db)
    if not admin:
        return RedirectResponse(url="/admin/login", status_code=302)

    uploaded_count = 0
    for img in images:
        if not img or not img.filename or not img.filename.strip():
            continue

        orig_name = img.filename
        ext = Path(orig_name).suffix.lower()
        if ext not in ALLOWED_IMAGE_EXTENSIONS:
            continue

        stored_name = f"{uuid.uuid4().hex}{ext}"
        dest = MEDIA_DIR / stored_name
        file_bytes = img.file.read()

        if len(file_bytes) > MAX_FILE_SIZE:
            continue

        with open(dest, "wb") as f:
            f.write(file_bytes)

        file_url = f"/static/uploads/images/{stored_name}"
        media = models.MediaFile(
            original_filename=orig_name,
            stored_filename=stored_name,
            file_size=len(file_bytes),
            file_url=file_url
        )
        db.add(media)
        uploaded_count += 1

    if uploaded_count > 0:
        db.commit()

    return RedirectResponse(url="/admin/media", status_code=302)


@router.post("/media/{media_id}/delete")
def admin_media_delete(media_id: int, request: Request, db: Session = Depends(get_db)):
    admin = get_current_admin(request, db)
    if not admin:
        return RedirectResponse(url="/admin/login", status_code=302)

    media = db.query(models.MediaFile).filter(models.MediaFile.id == media_id).first()
    if media:
        file_path = MEDIA_DIR / media.stored_filename
        if file_path.exists():
            try:
                file_path.unlink()
            except Exception:
                pass
        db.delete(media)
        db.commit()

    return RedirectResponse(url="/admin/media", status_code=302)

