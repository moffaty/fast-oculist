from typing import Any, Callable, Optional

from onvif import ONVIFCamera, ONVIFService
from fastapi import HTTPException, status
from core.log_config import logger
from onvif.exceptions import ONVIFError

from .schemas.onvif_camera_info import ONVIFCameraInfo


def handle_onvif_function(func: Callable[..., Any]) -> Callable[..., Any]:
    def wrapper(*args: Any, **kwargs: Any) -> None:
        try:
            func(*args, **kwargs)
        except ONVIFError as e:
            logger.exception(f"Ошибка работы с камерой: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Ошибка работы с камерой.")
        except (ValueError, TypeError) as e:
            logger.exception(f"Ошибка с форматом данных: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Ошибка с форматом данных.")

    return wrapper


class ONVIFCameraController:
    def __init__(self, ip: str, port: str, username: str, password: str) -> None:
        self.ip = ip
        self.port = port
        self.username = username
        self.password = password
        self.camera: ONVIFCamera

    @handle_onvif_function
    def connect(self) -> None:
        self.camera = ONVIFCamera(self.ip, self.port, self.username, self.password)
        logger.info("Успешное подключение к камере.")

    @handle_onvif_function
    def get_device_info(self) -> Optional[ONVIFCameraInfo]:
        if self.camera:
            device_info = self.camera.devicemgmt.GetDeviceInformation()
            onvif_camera_info = ONVIFCameraInfo(
                model=device_info.Model,
                manufacturer=device_info.Manufacturer,
                serial_number=device_info.SerialNumber,
                hardware_id=device_info.HardwareId,
                firmware_version=device_info.FirmwareVersion,
            )
            return onvif_camera_info
        else:
            return None

    @handle_onvif_function
    def get_profile_token(self, media_service: Optional[ONVIFService]) -> Optional[str]:
        if self.camera:
            if media_service is None:
                media_service = self.camera.create_media_service()

            profiles = media_service.GetProfiles()
            profile_token: str = profiles[0].token
            return profile_token
        else:
            return None

    @handle_onvif_function
    def get_ptz_service(self) -> Optional[ONVIFService]:
        if self.camera:
            ptz_service = self.camera.create_ptz_service()
            return ptz_service
        else:
            return None

    @handle_onvif_function
    def move_ptz(self, pan: float, tilt: float, zoom: float) -> None:
        ptz_service = self.get_ptz_service()
        profile_token = self.get_profile_token()

        if ptz_service:
            move_request = {"ProfileToken": profile_token, "Velocity": {"PanTilt": {"x": pan, "y": tilt}, "Zoom": zoom}}
            ptz_service.ContinuousMove(move_request)
            logger.info("PTZ команда отправлена.")
        else:
            logger.error("PTZ сервис недоступен.")

    @handle_onvif_function
    def get_stream_uri(self) -> Optional[str]:
        if self.camera:
            media_service = self.camera.create_media_service()
            profile_token = self.get_profile_token(media_service)
            stream = media_service.GetStreamUri(
                {"StreamSetup": {"Stream": "RTP-Unicast", "Transport": "RTSP"}, "ProfileToken": profile_token}
            )
            stream_uri: str = stream.Uri
            return stream_uri
        else:
            return None
