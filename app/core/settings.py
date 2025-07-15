from pathlib import Path

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class CameraSettings(BaseModel):
    camera_id: int
    name: str
    rtsp_url: str


CAMERA_1 = CameraSettings(camera_id=0, name="Камера 1", rtsp_url="rtsp://admin:aa123456@192.168.1.68:554/video1")
CAMERA_2 = CameraSettings(camera_id=1, name="Камера 2", rtsp_url="rtsp://admin:aa123456@192.168.1.69:554/video1")
CAMERAS = [CAMERA_1, CAMERA_2]


class Settings(BaseSettings):
    PROJECT_NAME: str = Field("Oculist")
    VERSION: str = Field("0.1.0")
    DEBUG: bool = Field(True)
    PORT: int = Field(3000)

    ROOT_DIR: Path = Path(__file__).parent.parent
    STATIC_DIR: Path = ROOT_DIR / "static"
    TEMPLATE_DIR: Path = ROOT_DIR / "templates"


APP_SETTINGS = Settings()
