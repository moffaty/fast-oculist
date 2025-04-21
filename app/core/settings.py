from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str
    VERSION: str
    DEBUG: bool
    PORT: int
    CAMERAS: list[str]

    ROOT_DIR: Path = Path(__file__).parent.parent
    STATIC_DIR: Path = ROOT_DIR / "static"
    TEMPLATE_DIR: Path = ROOT_DIR / "templates"

    class Config:
        env_file = ".env"


APP_SETTINGS = Settings()
