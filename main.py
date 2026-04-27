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


@app.get("/notices", response_class=HTMLResponse)
async def notices(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="/mainpages/notice.html",
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

@app.get("/safe_school", response_class=HTMLResponse)
async def safeschool(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="/edu/sschool.html",
        context={
            "title": "IYCF - 국제청소년문화재단",
        },
    )


@app.get("/equalis", response_class=HTMLResponse)
async def equalis(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="/edu/equalis.html",
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


@app.get("/eventmain", response_class=HTMLResponse)
async def eventmain(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="/events/eventmain.html",
        context={
            "title": "IYCF - 국제청소년문화재단",
        },
    )

@app.get("/k_wellf", response_class=HTMLResponse)
async def kwell(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="/events/kwellf.html",
        context={
            "title": "IYCF - 국제청소년문화재단",
        },
    )


@app.get("/galmer", response_class=HTMLResponse)
async def galmer(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="/events/galmer.html",
        context={
            "title": "IYCF - 국제청소년문화재단",
        },
    )


@app.get("/2025_jagalchi", response_class=HTMLResponse)
async def jagalchi25(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="/events/jagalchi25.html",
        context={
            "title": "IYCF - 국제청소년문화재단",
        },
    )


@app.get("/2025_yeongdo", response_class=HTMLResponse)
async def yeongdo25(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="/events/yeongdo25.html",
        context={
            "title": "IYCF - 국제청소년문화재단",
        },
    )

@app.get("/chy_writer", response_class=HTMLResponse)
async def chy_writer(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="/events/chy_writer.html",
        context={
            "title": "IYCF - 국제청소년문화재단",
        },
    )


@app.get("/safe_goldenbell", response_class=HTMLResponse)
async def safe_goldenbell(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="/events/safe_goldenbell.html",
        context={
            "title": "IYCF - 국제청소년문화재단",
        },
    )


@app.get("/scholarship_delivery", response_class=HTMLResponse)
async def scholarship_delivery(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="/events/scholarship_delivery.html",
        context={
            "title": "IYCF - 국제청소년문화재단",
        },
    )


@app.get("/youth_volunteer", response_class=HTMLResponse)
async def youthv(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="/events/youth_volunteer.html",
        context={
            "title": "IYCF - 국제청소년문화재단",
        },
    )


@app.get("/reporter_notice", response_class=HTMLResponse)
async def reporter_notice(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="/events/reporter_notice.html",
        context={
            "title": "IYCF - 국제청소년문화재단",
        },
    )


@app.get("/young_reporter", response_class=HTMLResponse)
async def youngreporter(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="/events/y_reporter.html",
        context={
            "title": "IYCF - 국제청소년문화재단",
        },
    )


@app.get("/childrensafe", response_class=HTMLResponse)
async def childrensafe(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="/events/childrensafe.html",
        context={
            "title": "IYCF - 국제청소년문화재단",
        },
    )


@app.get("/childrensafe2", response_class=HTMLResponse)
async def childrensafe2(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="/events/childrensafe2.html",
        context={
            "title": "IYCF - 국제청소년문화재단",
        },
    )

@app.get("/env_education", response_class=HTMLResponse)
async def envedu(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="/events/env_education.html",
        context={
            "title": "IYCF - 국제청소년문화재단",
        },
    )

@app.get("/elder_video", response_class=HTMLResponse)
async def eldervideo(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="/events/elder_video.html",
        context={
            "title": "IYCF - 국제청소년문화재단",
        },
    )
