from typing import List, Optional

from sqlmodel import Field, SQLModel, Relationship


class ObjectBase(SQLModel):
    name: str
    x_coord: float
    y_coord: float
    description: Optional[str] = None


class Object(ObjectBase, table=True):
    __tablename__ = "objects"

    id: Optional[int] = Field(default=None, primary_key=True)
    features: Optional[str] = None  # Сохраненные признаки объекта в формате JSON

    # Отношения
    detections: List["Detection"] = Relationship(back_populates="object")


class DetectionBase(SQLModel):
    confidence: float
    x_coord: float
    y_coord: float
    timestamp: float
    frame_id: int


class Detection(DetectionBase, table=True):
    __tablename__ = "detections"

    id: Optional[int] = Field(default=None, primary_key=True)
    object_id: Optional[int] = Field(default=None, foreign_key="objects.id")

    # Отношения
    object: Optional[Object] = Relationship(back_populates="detections")


class RTSPSource(SQLModel, table=True):
    __tablename__ = "rtsp_sources"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    url: str
    is_active: bool = True
    description: Optional[str] = None
