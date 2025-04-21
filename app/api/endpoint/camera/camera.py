from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from core.settings import APP_SETTINGS
from core.log_config import logger


router = APIRouter(tags=["Camera"])


@router.websocket("/camera/{camera_id}")
async def camera_connection(websocket: WebSocket, camera_id: str) -> None:
    if camera_id not in APP_SETTINGS.CAMERAS:
        await websocket.close(code=1008)
        return

    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"[Camera {camera_id}] Received: {data}")
    except WebSocketDisconnect:
        logger.info(f"Camera {camera_id} disconnected")
