from typing import Dict

from fastapi import Request, APIRouter, WebSocket, WebSocketDisconnect
from controls import CameraController
from core.settings import CAMERAS, APP_SETTINGS
from core.log_config import logger
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates


camera_control = CameraController()
router = APIRouter(tags=["index"])
templates = Jinja2Templates(directory=APP_SETTINGS.TEMPLATE_DIR)


def calculate_ptz_coordinates(x: int, y: int, image_width: int = 1920, image_height: int = 1080) -> tuple:
    # Вычисляем отклонение от центра
    center_x = image_width / 2
    center_y = image_height / 2

    # Нормализуем отклонение в диапазон [-1, 1]
    deviation_x = (x - center_x) / center_x  # Влево -1, вправо +1
    deviation_y = (center_y - y) / center_y  # Вверх +1, вниз -1 (инвертируем оси Y)

    # Масштабируем отклонение в зависимости от чувствительности камеры
    # Значение может потребовать настройки
    pan_speed = deviation_x * 1.0  # Регулировка скорости поворота
    tilt_speed = deviation_y * 1.0  # Регулировка скорости наклона

    return pan_speed, tilt_speed


@router.get("/", response_class=HTMLResponse)
async def read_root(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("index.html", {"request": request, "cameras": CAMERAS})


@router.websocket("/")
async def control(websocket: WebSocket) -> None:
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()

            # Проверяем, является ли это командой остановки
            if data.get("command") == "stop":
                camera_control.stop()
                await websocket.send_json({"status": "success", "message": "Camera movement stopped"})
                continue  # Продолжаем цикл вместо выхода из функции

            # Только если это не команда остановки, обрабатываем координаты
            if "centerX" in data and "centerY" in data:
                pan_speed, tilt_speed = calculate_ptz_coordinates(data["centerX"], data["centerY"])
                logger.info(data)
                logger.info(f"pan_speed: {pan_speed:.2f}; tilt_speed: {tilt_speed:.2f}")

                if abs(pan_speed) > 0.1 or abs(tilt_speed) > 0.1:
                    camera_control.continuous_move(pan_speed, tilt_speed, 1)
                    camera_control.stop()

                # Отправляем подтверждение
                await websocket.send_text(f"Received: {data}")
            else:
                # Если данные не содержат необходимых полей, отправляем ошибку
                await websocket.send_json(
                    {"status": "error", "message": "Invalid data format. Expected centerX and centerY coordinates."}
                )

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    except Exception as e:  # noqa: BLE001
        logger.error(f"Error in WebSocket connection: {e!s}")
        try:
            await websocket.close()
        except:  # noqa: E722, S110
            pass


# Дополнительный маршрут для остановки движения камеры
@router.post("/stop")
async def stop_camera() -> Dict[str, str]:
    camera_control.stop()
    return {"status": "success", "message": "Camera movement stopped"}
