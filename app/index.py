from fastapi import Request, APIRouter
from core.settings import APP_SETTINGS
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates


router = APIRouter(tags=["index"])
templates = Jinja2Templates(directory=APP_SETTINGS.TEMPLATE_DIR)


@router.get("/", response_class=HTMLResponse)
async def read_root(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("index.html", {"request": request})
