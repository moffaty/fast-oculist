from pydantic import BaseModel


class ONVIFCameraInfo(BaseModel):
    model: str
    manufacturer: str
    serial_number: str
    hardware_id: str
    firmware_version: str
