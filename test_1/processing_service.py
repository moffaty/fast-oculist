import json
import time
from typing import List
import asyncio

import cv2
import numpy as np
from models import Object, Detection, RTSPSource
from fastapi import Depends, FastAPI, WebSocket, HTTPException, WebSocketDisconnect
from database import engine, db_session, create_session
from sqlmodel import Session, select

# Оптимизированная реализация обнаружения объектов для CPU
import onnxruntime as ort


app = FastAPI(title="Object Detection Processing Service")

# Глобальные переменные для хранения RTSP-соединений и состояния обработки
active_connections = {}
processing_tasks = {}


# Класс для хранения RTSP-соединений
class RTSPConnection:
    def __init__(self, url: str, source_id: int):
        self.url = url
        self.source_id = source_id
        self.cap = None
        self.is_processing = False
        self.connected_clients = set()

    async def connect(self):
        """Подключение к RTSP потоку"""
        if self.cap is None or not self.cap.isOpened():
            self.cap = cv2.VideoCapture(self.url)
            if not self.cap.isOpened():
                raise Exception(f"Не удалось подключиться к потоку: {self.url}")
        return self.cap

    def disconnect(self):
        """Отключение от RTSP потока"""
        if self.cap and self.cap.isOpened():
            self.cap.release()
            self.cap = None

    def add_client(self, client_id):
        """Добавление клиента к потоку"""
        self.connected_clients.add(client_id)

    def remove_client(self, client_id):
        """Удаление клиента из потока"""
        if client_id in self.connected_clients:
            self.connected_clients.remove(client_id)

        # Если больше нет подключенных клиентов, отключаемся от потока
        if not self.connected_clients and not self.is_processing:
            self.disconnect()


# Модуль обнаружения объектов (CPU-оптимизированный)
class ObjectDetector:
    def __init__(self):
        # Инициализация ONNX Runtime с оптимизациями для CPU
        self.session_options = ort.SessionOptions()
        self.session_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        self.session_options.intra_op_num_threads = 4  # Настройте под свой CPU

        # Загрузка предварительно обученной модели YOLOv5 (или другой оптимизированной для CPU)
        # В продакшене следует использовать полный путь к файлу
        self.model_path = "models/yolov5s.onnx"  # Предполагаем, что модель уже конвертирована в ONNX
        self.session = ort.InferenceSession(self.model_path, self.session_options)

        # Получаем имена входного и выходного слоя
        self.input_name = self.session.get_inputs()[0].name
        self.output_name = self.session.get_outputs()[0].name

        # Предобработка и параметры
        self.input_shape = (640, 640)  # Стандартный размер входа для YOLOv5
        self.conf_threshold = 0.5
        self.iou_threshold = 0.45

    def preprocess(self, img):
        """Предобработка изображения для модели"""
        # Изменение размера и нормализация
        img = cv2.resize(img, self.input_shape)
        img = img.astype(np.float32) / 255.0
        img = np.transpose(img, (2, 0, 1))  # HWC -> CHW
        img = np.expand_dims(img, axis=0)  # Добавляем размерность пакета
        return img

    async def detect_objects(self, frame, session: Session):
        """Обнаружение объектов на кадре"""
        # Предобработка кадра
        input_tensor = self.preprocess(frame)

        # Запуск вывода модели
        detections = self.session.run([self.output_name], {self.input_name: input_tensor})[0]

        # Обработка результатов
        results = []
        if len(detections) > 0:
            # Фильтрация по порогу достоверности
            mask = detections[0][:, 4] > self.conf_threshold
            filtered_detections = detections[0][mask]

            # Получение данных (class_id, confidence, x, y, width, height)
            if len(filtered_detections) > 0:
                timestamp = time.time()
                frame_id = int(timestamp * 1000)  # Простой ID кадра на основе времени

                for det in filtered_detections:
                    x, y, w, h = det[0], det[1], det[2], det[3]
                    conf = det[4]
                    class_id = int(det[5])

                    # Сопоставление с объектами из базы данных
                    matched_object = await self.match_with_database(x, y, session)

                    # Создание записи о детекции
                    detection = Detection(
                        confidence=float(conf),
                        x_coord=float(x),
                        y_coord=float(y),
                        timestamp=timestamp,
                        frame_id=frame_id,
                        object_id=matched_object.id if matched_object else None,
                    )

                    session.add(detection)
                    session.commit()
                    session.refresh(detection)

                    results.append(
                        {
                            "detection_id": detection.id,
                            "object_id": detection.object_id,
                            "object_name": matched_object.name if matched_object else "Unknown",
                            "confidence": detection.confidence,
                            "x": detection.x_coord,
                            "y": detection.y_coord,
                        }
                    )

        return results

    async def match_with_database(self, x: float, y: float, session: Session):
        """Сопоставление обнаруженного объекта с объектами в базе данных"""
        # Простой алгоритм: поиск ближайшего объекта по координатам
        # В продакшене должен быть более сложный алгоритм сопоставления с учетом признаков
        objects = session.exec(select(Object)).all()

        min_distance = float("inf")
        closest_object = None

        for obj in objects:
            distance = ((obj.x_coord - x) ** 2 + (obj.y_coord - y) ** 2) ** 0.5
            if distance < min_distance:
                min_distance = distance
                closest_object = obj

        # Если ближайший объект слишком далеко, считаем что совпадения нет
        distance_threshold = 0.2  # Настраиваемый порог
        if min_distance > distance_threshold:
            return None

        return closest_object


# Инициализация детектора
detector = ObjectDetector()


@app.on_event("startup")
async def startup_event():
    """Действия при запуске приложения"""
    # Инициализация базы данных
    from sqlmodel import SQLModel

    SQLModel.metadata.create_all(engine)

    # Загрузка активных RTSP-источников из базы данных
    with create_session() as session:
        sources = session.exec(select(RTSPSource).where(RTSPSource.is_active == True)).all()
        for source in sources:
            active_connections[source.id] = RTSPConnection(source.url, source.id)


@app.on_event("shutdown")
async def shutdown_event():
    """Действия при завершении работы приложения"""
    # Закрытие всех активных соединений
    for conn in active_connections.values():
        conn.disconnect()


@app.get("/sources", response_model=List[dict])
async def get_sources(session: Session = Depends(db_session)):
    """Получение списка RTSP-источников"""
    sources = session.exec(select(RTSPSource)).all()
    return [
        {"id": source.id, "name": source.name, "url": source.url, "is_active": source.is_active} for source in sources
    ]


@app.post("/sources", response_model=dict)
async def add_source(name: str, url: str, session: Session = Depends(db_session)):
    """Добавление нового RTSP-источника"""
    source = RTSPSource(name=name, url=url, is_active=True)
    session.add(source)
    session.commit()
    session.refresh(source)

    # Добавление в активные соединения
    active_connections[source.id] = RTSPConnection(source.url, source.id)

    return {"id": source.id, "name": source.name, "url": source.url, "is_active": source.is_active}


@app.delete("/sources/{source_id}")
async def delete_source(source_id: int, session: Session = Depends(db_session)):
    """Удаление RTSP-источника"""
    source = session.exec(select(RTSPSource).where(RTSPSource.id == source_id)).first()
    if not source:
        raise HTTPException(status_code=404, detail="Источник не найден")

    # Удаление из активных соединений
    if source_id in active_connections:
        active_connections[source_id].disconnect()
        del active_connections[source_id]

    session.delete(source)
    session.commit()

    return {"status": "success", "message": f"Источник {source_id} удален"}


@app.post("/start_processing/{source_id}")
async def start_processing(source_id: int, session: Session = Depends(db_session)):
    """Запуск обработки видеопотока"""
    # Проверка существования источника
    source = session.exec(select(RTSPSource).where(RTSPSource.id == source_id)).first()
    if not source:
        raise HTTPException(status_code=404, detail="Источник не найден")

    # Проверка, что источник не обрабатывается
    if source_id in processing_tasks and processing_tasks[source_id].is_processing:
        return {"status": "warning", "message": "Обработка уже запущена"}

    # Получение или создание соединения
    if source_id not in active_connections:
        active_connections[source_id] = RTSPConnection(source.url, source_id)

    connection = active_connections[source_id]

    # Запуск задачи обработки в фоне
    connection.is_processing = True
    processing_tasks[source_id] = asyncio.create_task(process_video_stream(source_id))

    return {"status": "success", "message": f"Обработка источника {source_id} запущена"}


@app.post("/stop_processing/{source_id}")
async def stop_processing(source_id: int):
    """Остановка обработки видеопотока"""
    if source_id not in processing_tasks:
        raise HTTPException(status_code=404, detail="Задача обработки не найдена")

    # Отмена задачи
    task = processing_tasks[source_id]
    task.cancel()

    # Обновление состояния соединения
    if source_id in active_connections:
        active_connections[source_id].is_processing = False

    return {"status": "success", "message": f"Обработка источника {source_id} остановлена"}


@app.websocket("/ws/{source_id}")
async def websocket_endpoint(websocket: WebSocket, source_id: int):
    """WebSocket для получения результатов обработки в реальном времени"""
    await websocket.accept()

    # Генерация ID для клиента
    client_id = f"client_{time.time()}"

    try:
        # Проверка существования источника
        with create_session() as session:
            source = session.exec(select(RTSPSource).where(RTSPSource.id == source_id)).first()
            if not source:
                await websocket.close(code=1008, reason="Источник не найден")
                return

        # Регистрация клиента
        if source_id not in active_connections:
            active_connections[source_id] = RTSPConnection(source.url, source_id)

        connection = active_connections[source_id]
        connection.add_client(client_id)

        # Если обработка еще не запущена, запускаем
        if not connection.is_processing and source_id not in processing_tasks:
            connection.is_processing = True
            processing_tasks[source_id] = asyncio.create_task(process_video_stream(source_id))

        # Основной цикл обработки сообщений от клиента
        while True:
            # Ожидание сообщений от клиента для управления потоком
            data = await websocket.receive_text()
            command = json.loads(data)

            if command.get("action") == "get_detections":
                # Клиент запрашивает текущие обнаружения
                with create_session() as session:
                    # Получаем последние обнаружения для этого источника
                    # В продакшене нужно добавить фильтрацию по source_id
                    recent_detections = session.exec(
                        select(Detection).order_by(Detection.timestamp.desc()).limit(10)
                    ).all()

                    results = []
                    for detection in recent_detections:
                        object_data = None
                        if detection.object_id:
                            obj = session.get(Object, detection.object_id)
                            if obj:
                                object_data = {"id": obj.id, "name": obj.name, "description": obj.description}

                        results.append(
                            {
                                "detection_id": detection.id,
                                "object": object_data,
                                "confidence": detection.confidence,
                                "x": detection.x_coord,
                                "y": detection.y_coord,
                                "timestamp": detection.timestamp,
                            }
                        )

                    await websocket.send_json({"type": "detections", "data": results})

    except WebSocketDisconnect:
        # Обработка отключения клиента
        if source_id in active_connections:
            active_connections[source_id].remove_client(client_id)
    except Exception as e:
        # Обработка других ошибок
        print(f"WebSocket error: {e!s}")
        if source_id in active_connections:
            active_connections[source_id].remove_client(client_id)


async def process_video_stream(source_id: int):
    """Фоновая задача обработки видеопотока"""
    if source_id not in active_connections:
        print(f"Соединение для источника {source_id} не найдено")
        return

    connection = active_connections[source_id]

    try:
        # Подключение к потоку
        cap = await connection.connect()

        # Цикл обработки кадров
        while connection.is_processing:
            try:
                # Чтение кадра из потока
                ret, frame = cap.read()
                if not ret:
                    print(f"Не удалось прочитать кадр из потока {source_id}")
                    await asyncio.sleep(1)  # Пауза перед повторной попыткой
                    continue

                # Выполняем обнаружение объектов
                with create_session() as session:
                    detections = await detector.detect_objects(frame, session)

                # Отправляем результаты всем подключенным клиентам
                for client_id in connection.connected_clients:
                    # В реальном приложении здесь нужно получить WebSocket для клиента
                    # и отправить ему результаты
                    # websocket = get_client_websocket(client_id)  # Пример
                    # await websocket.send_json({"type": "detections", "data": detections})
                    pass

                # Небольшая пауза для снижения нагрузки на CPU
                await asyncio.sleep(0.03)  # ~30 FPS

            except Exception as e:
                print(f"Ошибка при обработке кадра: {e!s}")
                await asyncio.sleep(1)

    except asyncio.CancelledError:
        # Обработка отмены задачи
        connection.is_processing = False
        print(f"Обработка потока {source_id} отменена")

    except Exception as e:
        # Обработка других ошибок
        connection.is_processing = False
        print(f"Ошибка при обработке потока {source_id}: {e!s}")

    finally:
        # Обновление состояния
        connection.is_processing = False


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
