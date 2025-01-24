from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str
    VERSION: str
    DEBUG: bool
    PORT: int

    ROOT_DIR: Path = Path(__file__).parent.parent

    class Config:
        env_file = ".env"


APP_SETTINGS = Settings()
