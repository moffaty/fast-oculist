import json
from typing import List, Optional

import cv2
import numpy as np
from models import Object
from fastapi import File, Form, Depends, FastAPI, UploadFile, HTTPException
from database import engine, db_session, create_session
from pydantic import BaseModel
from sqlmodel import Session, select


app = FastAPI(title="Object Management Service")


# Инициализация базы данных при запуске приложения
@app.on_event("startup")
async def startup_event():
    from sqlmodel import SQLModel

    SQLModel.metadata.create_all(engine)


# Модели для запросов API
class ObjectCreate(BaseModel):
    name: str
    x_coord: float
    y_coord: float
    description: Optional[str] = None


class ObjectResponse(BaseModel):
    id: int
    name: str
    x_coord: float
    y_coord: float
    description: Optional[str] = None


class ObjectUpdate(BaseModel):
    name: Optional[str] = None
    x_coord: Optional[float] = None
    y_coord: Optional[float] = None
    description: Optional[str] = None


# Класс для извлечения признаков из изображений
class FeatureExtractor:
    def __init__(self):
        # Для CPU-оптимизированного варианта используем более легкую модель
        # Вместо глубоких нейросетей используем HOG + SIFT для признаков
        self.hog = cv2.HOGDescriptor()
        self.sift = cv2.SIFT_create()

    def extract_features(self, image):
        """Извлечение признаков из изображения объекта"""
        # Преобразование в оттенки серого
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        # Изменение размера для стандартизации
        resized = cv2.resize(gray, (128, 128))

        # Извлечение HOG признаков
        hog_features = self.hog.compute(resized).flatten()

        # Извлечение SIFT признаков
        keypoints, descriptors = self.sift.detectAndCompute(resized, None)

        # Если нет SIFT признаков, используем только HOG
        if descriptors is None:
            return hog_features

        # Сжатие SIFT признаков до управляемого размера
        if len(keypoints) > 0:
            descriptors_mean = np.mean(descriptors, axis=0)
        else:
            descriptors_mean = np.zeros(128)  # Размерность SIFT

        # Объединение признаков
        combined_features = np.concatenate([hog_features, descriptors_mean])

        return combined_features


# Инициализация экстрактора признаков
feature_extractor = FeatureExtractor()


@app.get("/objects", response_model=List[ObjectResponse])
async def get_objects(skip: int = 0, limit: int = 100, session: Session = Depends(db_session)):
    """Получение списка всех объектов"""
    objects = session.exec(select(Object).offset(skip).limit(limit)).all()
    return objects


@app.post("/objects", response_model=ObjectResponse)
async def create_object(object_data: ObjectCreate, session: Session = Depends(db_session)):
    """Создание нового объекта без изображения"""
    db_object = Object(
        name=object_data.name,
        x_coord=object_data.x_coord,
        y_coord=object_data.y_coord,
        description=object_data.description,
    )
    session.add(db_object)
    session.commit()
    session.refresh(db_object)
    return db_object


@app.post("/objects/with-image", response_model=ObjectResponse)
async def create_object_with_image(
    name: str = Form(...),
    x_coord: float = Form(...),
    y_coord: float = Form(...),
    description: Optional[str] = Form(None),
    image: UploadFile = File(...),
    session: Session = Depends(db_session),
):
    """Создание нового объекта с изображением и извлечением признаков"""
    # Чтение и обработка изображения
    content = await image.read()
    nparr = np.frombuffer(content, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if img is None:
        raise HTTPException(status_code=400, detail="Невозможно декодировать изображение")

    # Извлечение признаков
    features = feature_extractor.extract_features(img)

    # Сохранение признаков в формате JSON
    features_json = json.dumps(features.tolist())

    # Создание объекта в базе данных
    db_object = Object(name=name, x_coord=x_coord, y_coord=y_coord, description=description, features=features_json)

    session.add(db_object)
    session.commit()
    session.refresh(db_object)

    return db_object


@app.get("/objects/{object_id}", response_model=ObjectResponse)
async def get_object(object_id: int, session: Session = Depends(db_session)):
    """Получение информации об объекте по ID"""
    object = session.get(Object, object_id)
    if not object:
        raise HTTPException(status_code=404, detail="Объект не найден")
    return object


@app.patch("/objects/{object_id}", response_model=ObjectResponse)
async def update_object(object_id: int, object_data: ObjectUpdate, session: Session = Depends(db_session)):
    """Обновление информации об объекте"""
    db_object = session.get(Object, object_id)
    if not db_object:
        raise HTTPException(status_code=404, detail="Объект не найден")

    # Обновление полей, только если они предоставлены
    for key, value in object_data.dict(exclude_unset=True).items():
        setattr(db_object, key, value)

    session.add(db_object)
    session.commit()
    session.refresh(db_object)

    return db_object


@app.delete("/objects/{object_id}")
async def delete_object(object_id: int, session: Session = Depends(db_session)):
    """Удаление объекта"""
    object = session.get(Object, object_id)
    if not object:
        raise HTTPException(status_code=404, detail="Объект не найден")

    session.delete(object)
    session.commit()

    return {"status": "success", "message": f"Объект {object_id} удален"}


@app.post("/objects/{object_id}/update-image")
async def update_object_image(object_id: int, image: UploadFile = File(...), session: Session = Depends(db_session)):
    """Обновление изображения объекта и его признаков"""
    db_object = session.get(Object, object_id)
    if not db_object:
        raise HTTPException(status_code=404, detail="Объект не найден")

    # Чтение и обработка изображения
    content = await image.read()
    nparr = np.frombuffer(content, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if img is None:
        raise HTTPException(status_code=400, detail="Невозможно декодировать изображение")

    # Извлечение новых признаков
    features = feature_extractor.extract_features(img)

    # Обновление признаков в базе данных
    db_object.features = json.dumps(features.tolist())

    session.add(db_object)
    session.commit()
    session.refresh(db_object)

    return {"status": "success", "message": f"Изображение объекта {object_id} обновлено"}


@app.post("/objects/batch-upload")
async def batch_upload_objects(objects_file: UploadFile = File(...), session: Session = Depends(db_session)):
    """Загрузка множества объектов из JSON-файла"""
    content = await objects_file.read()
    try:
        objects_data = json.loads(content)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Неверный формат JSON")

    created_objects = []
    for obj_data in objects_data:
        try:
            db_object = Object(
                name=obj_data["name"],
                x_coord=obj_data["x_coord"],
                y_coord=obj_data["y_coord"],
                description=obj_data.get("description"),
            )
            session.add(db_object)
            session.commit()
            session.refresh(db_object)
            created_objects.append(db_object)
        except KeyError:
            # Пропускаем объекты с отсутствующими обязательными полями
            continue

    return {"status": "success", "created_objects": len(created_objects)}


@app.get("/objects/search/by-coordinates")
async def search_objects_by_coordinates(
    x: float, y: float, radius: float = 0.1, session: Session = Depends(db_session)
):
    """Поиск объектов по координатам в заданном радиусе"""
    objects = session.exec(select(Object)).all()

    results = []
    for obj in objects:
        # Вычисление евклидова расстояния
        distance = ((obj.x_coord - x) ** 2 + (obj.y_coord - y) ** 2) ** 0.5
        if distance <= radius:
            results.append(
                {
                    "id": obj.id,
                    "name": obj.name,
                    "x_coord": obj.x_coord,
                    "y_coord": obj.y_coord,
                    "description": obj.description,
                    "distance": distance,
                }
            )

    # Сортировка по расстоянию
    results.sort(key=lambda x: x["distance"])

    return results


@app.get("/objects/search/by-name")
async def search_objects_by_name(name: str, session: Session = Depends(db_session)):
    """Поиск объектов по имени (частичное совпадение)"""
    objects = session.exec(select(Object).where(Object.name.contains(name))).all()

    return objects


@app.post("/objects/compare-image")
async def compare_image_with_objects(
    image: UploadFile = File(...), top_n: int = 5, session: Session = Depends(db_session)
):
    """Сравнение загруженного изображения с объектами в базе данных"""
    content = await image.read()
    nparr = np.frombuffer(content, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if img is None:
        raise HTTPException(status_code=400, detail="Невозможно декодировать изображение")

    # Извлечение признаков из загруженного изображения
    query_features = feature_extractor.extract_features(img)

    # Получение всех объектов с признаками
    objects = session.exec(select(Object).where(Object.features != None)).all()

    results = []
    for obj in objects:
        try:
            # Загрузка признаков объекта
            obj_features = np.array(json.loads(obj.features))

            # Вычисление косинусного расстояния
            if len(query_features) == len(obj_features):
                similarity = np.dot(query_features, obj_features) / (
                    np.linalg.norm(query_features) * np.linalg.norm(obj_features)
                )
            else:
                # Если размерности не совпадают, пропускаем
                continue

            results.append(
                {
                    "id": obj.id,
                    "name": obj.name,
                    "similarity": float(similarity),
                    "x_coord": obj.x_coord,
                    "y_coord": obj.y_coord,
                }
            )
        except (json.JSONDecodeError, ValueError):
            # Пропускаем объекты с невалидными признаками
            continue

    # Сортировка по убыванию сходства и выбор top_n результатов
    results.sort(key=lambda x: x["similarity"], reverse=True)
    top_results = results[:top_n]

    return top_results


@app.get("/objects/export")
async def export_objects():
    """Экспорт всех объектов в JSON-формате"""
    with create_session() as session:
        objects = session.exec(select(Object)).all()

        objects_data = []
        for obj in objects:
            objects_data.append(
                {
                    "id": obj.id,
                    "name": obj.name,
                    "x_coord": obj.x_coord,
                    "y_coord": obj.y_coord,
                    "description": obj.description,
                }
            )

        return objects_data


@app.post("/objects/reset-database")
async def reset_database():
    with create_session() as session:
        objects = session.exec(select(Object)).all()
        for obj in objects:
            session.delete(obj)
        session.commit()

    return {"status": "success", "message": "База данных объектов сброшена"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
