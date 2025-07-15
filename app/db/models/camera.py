from uuid import UUID
from typing import Optional

from sqlmodel import Field, SQLModel


class Camera(SQLModel, table=True):  # type: ignore
    id: Optional[UUID] = Field(primary_key=True)
    name: str
