from __future__ import annotations

import hashlib
import random
from datetime import datetime
from typing import AsyncGenerator, List

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from database import (
    delete_detection,
    get_db_connection,
    get_detection,
    init_db,
    insert_detection,
    list_detections,
    update_detection,
)
from schemas import DetectionResponse, DetectionUpdate, DetectedObject

app = FastAPI(title="Async Image Detection API")

ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def on_startup() -> None:
    await init_db()


async def get_db() -> AsyncGenerator:
    db = await get_db_connection()
    try:
        yield db
    finally:
        await db.close()


def _generate_mock_detections(image_bytes: bytes) -> List[DetectedObject]:
    labels = ["cat", "dog", "car", "person", "bicycle"]
    seed = int(hashlib.sha256(image_bytes).hexdigest()[:8], 16)
    rng = random.Random(seed)
    objects: List[DetectedObject] = []
    count = rng.randint(1, 3)
    for _ in range(count):
        label = rng.choice(labels)
        x = rng.uniform(5, 60)
        y = rng.uniform(5, 60)
        width = rng.uniform(15, 40)
        height = rng.uniform(15, 40)
        confidence = round(rng.uniform(0.5, 0.99), 2)
        objects.append(
            DetectedObject(
                label=label,
                bbox={"x": x, "y": y, "width": width, "height": height},
                confidence=confidence,
            )
        )
    return objects


@app.post("/detect-image", response_model=DetectionResponse)
async def detect_image(file: UploadFile = File(...), db=Depends(get_db)):
    image_bytes = await file.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="File is empty")

    objects = _generate_mock_detections(image_bytes)
    created_at = datetime.utcnow().isoformat()

    detection_id = await insert_detection(
        db=db,
        filename=file.filename,
        objects=[obj.model_dump() for obj in objects],
        created_at=created_at,
    )

    return DetectionResponse(
        id=detection_id,
        filename=file.filename,
        objects=objects,
        created_at=created_at,
    )


@app.get("/detections", response_model=List[DetectionResponse])
async def fetch_detections(db=Depends(get_db)):
    records = await list_detections(db)
    return [DetectionResponse(**record) for record in records]


@app.get("/detections/{detection_id}", response_model=DetectionResponse)
async def fetch_detection(detection_id: int, db=Depends(get_db)):
    record = await get_detection(db, detection_id)
    if not record:
        raise HTTPException(status_code=404, detail="Detection not found")
    return DetectionResponse(**record)


@app.put("/detections/{detection_id}", response_model=DetectionResponse)
async def update_detection_record(
    detection_id: int, payload: DetectionUpdate, db=Depends(get_db)
):
    existing = await get_detection(db, detection_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Detection not found")

    filename = payload.filename or existing["filename"]
    objects_payload = payload.objects if payload.objects is not None else existing["objects"]

    if isinstance(objects_payload, list) and objects_payload and isinstance(objects_payload[0], DetectedObject):
        objects = [obj.model_dump() for obj in objects_payload]
    elif isinstance(objects_payload, list) and (not objects_payload or isinstance(objects_payload[0], dict)):
        # Already a list of dictionaries or an empty list supplied by client
        objects = objects_payload
    else:
        raise HTTPException(status_code=400, detail="Format objek tidak dikenali")

    updated = await update_detection(db, detection_id=detection_id, filename=filename, objects=objects)
    if not updated:
        raise HTTPException(status_code=404, detail="Detection not found")

    return DetectionResponse(
        id=detection_id,
        filename=filename,
        objects=objects,
        created_at=existing["created_at"],
    )


@app.delete("/detections/{detection_id}")
async def delete_detection_record(detection_id: int, db=Depends(get_db)):
    deleted = await delete_detection(db, detection_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Detection not found")
    return {"status": "deleted", "id": detection_id}


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
