from index import router as index_router
from fastapi import FastAPI
import uvicorn
from core.settings import APP_SETTINGS
from core.log_config import LOG_CONFIG
from fastapi.responses import ORJSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware

from api import router as api_router


app = FastAPI(
    title=APP_SETTINGS.PROJECT_NAME,
    version=APP_SETTINGS.VERSION,
    docs_url="/api/openapi" if APP_SETTINGS.DEBUG else None,
    openapi_url="/api/openapi.json" if APP_SETTINGS.DEBUG else None,
    default_response_class=ORJSONResponse,
    middleware=[
        Middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        ),
        Middleware(
            ProxyHeadersMiddleware,  # type: ignore
            trusted_hosts=["*"],
        ),
    ],
)

app.mount("/static", StaticFiles(directory=APP_SETTINGS.STATIC_DIR), name="static")
app.include_router(api_router.router, prefix="/api")
app.include_router(index_router, prefix="/index")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        log_config=LOG_CONFIG,
        port=APP_SETTINGS.PORT,
        proxy_headers=True,
        reload=True,
    )
