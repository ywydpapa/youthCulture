from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from database import BASE_DIR, init_db, get_db
import models
from auth import get_current_admin
from routers import admin as admin_router
from routers import notice as notice_router
from routers import page as page_router

STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 앱 시작 시 DB 테이블 및 초기 관리자 계정 생성
    init_db()
    yield


# FastAPI 앱 초기화
app = FastAPI(title="IYCF Homepage", lifespan=lifespan)

# 정적 파일 마운트
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# 관리자, 게시판, 커스텀 페이지 라우터 등록
app.include_router(admin_router.router)
app.include_router(notice_router.router)
app.include_router(page_router.router)


def render_page(template_name: str, request: Request, admin: Optional[models.AdminUser] = None, **kwargs):
    context = {
        "request": request,
        "title": "IYCF - 국제청소년문화재단",
        "admin": admin,
        **kwargs
    }
    return templates.TemplateResponse(
        request=request,
        name=template_name,
        context=context
    )


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, db: Session = Depends(get_db)):
    admin = get_current_admin(request, db)
    latest_posts = db.query(models.Post).order_by(models.Post.id.desc()).limit(4).all()
    return render_page("index.html", request, admin, latest_posts=latest_posts)


@app.get("/home", response_class=HTMLResponse)
async def read_home(request: Request, db: Session = Depends(get_db)):
    admin = get_current_admin(request, db)
    latest_posts = db.query(models.Post).order_by(models.Post.id.desc()).limit(4).all()
    return render_page("index.html", request, admin, latest_posts=latest_posts)


@app.get("/introduction", response_class=HTMLResponse)
async def introduction(request: Request, db: Session = Depends(get_db)):
    admin = get_current_admin(request, db)
    return render_page("/mainpages/introduction.html", request, admin)


@app.get("/history", response_class=HTMLResponse)
async def history(request: Request, db: Session = Depends(get_db)):
    admin = get_current_admin(request, db)
    return render_page("/mainpages/history.html", request, admin)


@app.get("/artofasso", response_class=HTMLResponse)
async def artofasso(request: Request, db: Session = Depends(get_db)):
    admin = get_current_admin(request, db)
    return render_page("/mainpages/artofasso.html", request, admin)


@app.get("/shingo", response_class=HTMLResponse)
async def shingo(request: Request, db: Session = Depends(get_db)):
    admin = get_current_admin(request, db)
    return render_page("/mainpages/shingo.html", request, admin)


@app.get("/edu_chy", response_class=HTMLResponse)
async def chy(request: Request, db: Session = Depends(get_db)):
    admin = get_current_admin(request, db)
    return render_page("/edu/chy.html", request, admin)


@app.get("/edu_globl", response_class=HTMLResponse)
async def globl(request: Request, db: Session = Depends(get_db)):
    admin = get_current_admin(request, db)
    return render_page("/edu/globl.html", request, admin)


@app.get("/safe_school", response_class=HTMLResponse)
async def safeschool(request: Request, db: Session = Depends(get_db)):
    admin = get_current_admin(request, db)
    return render_page("/edu/sschool.html", request, admin)


@app.get("/equalis", response_class=HTMLResponse)
async def equalis(request: Request, db: Session = Depends(get_db)):
    admin = get_current_admin(request, db)
    return render_page("/edu/equalis.html", request, admin)


@app.get("/edu_main", response_class=HTMLResponse)
async def edumain(request: Request, db: Session = Depends(get_db)):
    admin = get_current_admin(request, db)
    return render_page("/edu/edu_main.html", request, admin)


@app.get("/eventmain", response_class=HTMLResponse)
async def eventmain(request: Request, db: Session = Depends(get_db)):
    admin = get_current_admin(request, db)
    return render_page("/events/eventmain.html", request, admin)


@app.get("/k_wellf", response_class=HTMLResponse)
async def kwell(request: Request, db: Session = Depends(get_db)):
    admin = get_current_admin(request, db)
    return render_page("/events/kwellf.html", request, admin)


@app.get("/galmer", response_class=HTMLResponse)
async def galmer(request: Request, db: Session = Depends(get_db)):
    admin = get_current_admin(request, db)
    return render_page("/events/galmer.html", request, admin)


@app.get("/2025_jagalchi", response_class=HTMLResponse)
async def jagalchi25(request: Request, db: Session = Depends(get_db)):
    admin = get_current_admin(request, db)
    return render_page("/events/jagalchi25.html", request, admin)


@app.get("/2025_yeongdo", response_class=HTMLResponse)
async def yeongdo25(request: Request, db: Session = Depends(get_db)):
    admin = get_current_admin(request, db)
    return render_page("/events/yeongdo25.html", request, admin)


@app.get("/chy_writer", response_class=HTMLResponse)
async def chy_writer(request: Request, db: Session = Depends(get_db)):
    admin = get_current_admin(request, db)
    return render_page("/events/chy_writer.html", request, admin)


@app.get("/safe_goldenbell", response_class=HTMLResponse)
async def safe_goldenbell(request: Request, db: Session = Depends(get_db)):
    admin = get_current_admin(request, db)
    return render_page("/events/safe_goldenbell.html", request, admin)


@app.get("/scholarship_delivery", response_class=HTMLResponse)
async def scholarship_delivery(request: Request, db: Session = Depends(get_db)):
    admin = get_current_admin(request, db)
    return render_page("/events/scholarship_delivery.html", request, admin)


@app.get("/youth_volunteer", response_class=HTMLResponse)
async def youthv(request: Request, db: Session = Depends(get_db)):
    admin = get_current_admin(request, db)
    return render_page("/events/youth_volunteer.html", request, admin)


@app.get("/reporter_notice", response_class=HTMLResponse)
async def reporter_notice(request: Request, db: Session = Depends(get_db)):
    admin = get_current_admin(request, db)
    return render_page("/events/reporter_notice.html", request, admin)


@app.get("/young_reporter", response_class=HTMLResponse)
async def youngreporter(request: Request, db: Session = Depends(get_db)):
    admin = get_current_admin(request, db)
    return render_page("/events/y_reporter.html", request, admin)


@app.get("/childrensafe", response_class=HTMLResponse)
async def childrensafe(request: Request, db: Session = Depends(get_db)):
    admin = get_current_admin(request, db)
    return render_page("/events/childrensafe.html", request, admin)


@app.get("/childrensafe2", response_class=HTMLResponse)
async def childrensafe2(request: Request, db: Session = Depends(get_db)):
    admin = get_current_admin(request, db)
    return render_page("/events/childrensafe2.html", request, admin)


@app.get("/env_education", response_class=HTMLResponse)
async def envedu(request: Request, db: Session = Depends(get_db)):
    admin = get_current_admin(request, db)
    return render_page("/events/env_education.html", request, admin)


@app.get("/elder_video", response_class=HTMLResponse)
async def eldervideo(request: Request, db: Session = Depends(get_db)):
    admin = get_current_admin(request, db)
    return render_page("/events/elder_video.html", request, admin)


@app.get("/jangsan", response_class=HTMLResponse)
async def jangsan(request: Request, db: Session = Depends(get_db)):
    admin = get_current_admin(request, db)
    # 관리자가 업로드한 커스텀 'jangsan' HTML 페이지가 있으면 우선 렌더링
    custom_page = db.query(models.CustomPage).filter(models.CustomPage.slug == "jangsan").first()
    if custom_page:
        return page_router.render_custom_page_response(custom_page, request, admin)
    return render_page("/mainpages/jangsan.html", request, admin)

