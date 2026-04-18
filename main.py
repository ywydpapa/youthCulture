from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"
# FastAPI 앱 초기화
app = FastAPI(title="IYCF Homepage")

# 정적 파일(CSS, JS, 이미지 등) 마운트
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "title": "IYCF - 국제청소년문화재단",
        },
    )

@app.get("/introduction", response_class=HTMLResponse)
async def introduction(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="/mainpages/introduction.html",
        context={
            "title": "IYCF - 국제청소년문화재단",
        },
    )

@app.get("/history", response_class=HTMLResponse)
async def history(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="/mainpages/history.html",
        context={
            "title": "IYCF - 국제청소년문화재단",
        },
    )

@app.get("/artofasso", response_class=HTMLResponse)
async def artofasso(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="/mainpages/artofasso.html",
        context={
            "title": "IYCF - 국제청소년문화재단",
        },
    )

@app.get("/shingo", response_class=HTMLResponse)
async def shingo(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="/mainpages/shingo.html",
        context={
            "title": "IYCF - 국제청소년문화재단",
        },
    )

@app.get("/edu_chy", response_class=HTMLResponse)
async def chy(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="/edu/chy.html",
        context={
            "title": "IYCF - 국제청소년문화재단",
        },
    )

@app.get("/edu_globl", response_class=HTMLResponse)
async def globl(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="/edu/globl.html",
        context={
            "title": "IYCF - 국제청소년문화재단",
        },
    )

@app.get("/edu_main", response_class=HTMLResponse)
async def edumain(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="/edu/edu_main.html",
        context={
            "title": "IYCF - 국제청소년문화재단",
        },
    )