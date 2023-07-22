from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

templates = Jinja2Templates(directory="client/build")

router = APIRouter()


@router.get("/app", response_class=HTMLResponse)
async def serve_app(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
