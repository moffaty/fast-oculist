import time
from typing import Any

from onvif import ONVIFCamera


# Настройки камеры


class CameraController:
    def __init__(self) -> None:
        """
        Инициализация камеры и подключение к ней.
        """
        self.ip = "192.168.1.68"
        self.port = 80
        self.username = "admin"
        self.password = "aa123456"
        self.cam = ONVIFCamera(self.ip, self.port, self.username, self.password)
        self.media_service = self.cam.create_media_service()
        self.ptz_service = self.cam.create_ptz_service()
        self.profile = self._get_profile()

    def _get_profile(self) -> Any:
        """
        Получение профиля камеры.
        """
        profiles = self.media_service.GetProfiles()
        return profiles[0]  # Используем первый профиль

    def continuous_move(self, step_pan: float, step_tilt: float, duration: int = 2) -> None:
        """
        Выполнение движения с короткими рывками.

        :param step_pan: Шаг для панорамирования (горизонтальное движение).
        :param step_tilt: Шаг для наклона (вертикальное движение).
        :param duration: Общая длительность движения в секундах.
        """
        # Определяем скорость для панорамирования (PanTilt)
        velocity = {"PanTilt": {"x": step_pan, "y": step_tilt}, "Zoom": {"x": 0}}

        # Создаем запрос для ContinuousMove
        request = self.ptz_service.create_type("ContinuousMove")
        request.ProfileToken = self.profile.token
        request.Velocity = velocity

        # Выполняем несколько коротких рывков
        start_time = time.time()
        while time.time() - start_time < duration:  # Длительность движения
            self.ptz_service.ContinuousMove(request)
            time.sleep(0.5)  # Ожидаем между рывками (по 0.5 секунды)

        # Останавливаем движение
        self.ptz_service.Stop({"ProfileToken": self.profile.token})

    def stop(self) -> None:
        """
        Остановка всех движений камеры.
        """
        self.ptz_service.Stop({"ProfileToken": self.profile.token})


# Пример использования класса
if __name__ == "__main__":
    # Создание экземпляра контроллера камеры
    camera = CameraController()

    camera.continuous_move(-0.08, -0.0, duration=2)

    # Остановка камеры после завершения работы
    camera.stop()
