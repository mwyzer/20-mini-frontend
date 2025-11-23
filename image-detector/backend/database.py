from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import aiosqlite

DB_PATH = Path(__file__).resolve().parent / "detections.db"


async def init_db() -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS detections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                objects_json TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        await db.commit()


def _row_to_detection(row: aiosqlite.Row) -> dict[str, Any]:
    return {
        "id": row["id"],
        "filename": row["filename"],
        "objects": json.loads(row["objects_json"]),
        "created_at": row["created_at"],
    }


async def get_db_connection() -> aiosqlite.Connection:
    db = await aiosqlite.connect(DB_PATH)
    db.row_factory = aiosqlite.Row
    return db


async def insert_detection(db: aiosqlite.Connection, filename: str, objects: list[dict[str, Any]], created_at: str) -> int:
    cursor = await db.execute(
        "INSERT INTO detections (filename, objects_json, created_at) VALUES (?, ?, ?)",
        (filename, json.dumps(objects), created_at),
    )
    await db.commit()
    return cursor.lastrowid


async def list_detections(db: aiosqlite.Connection) -> list[dict[str, Any]]:
    cursor = await db.execute(
        "SELECT id, filename, objects_json, created_at FROM detections ORDER BY datetime(created_at) DESC"
    )
    rows = await cursor.fetchall()
    return [_row_to_detection(row) for row in rows]


async def get_detection(db: aiosqlite.Connection, detection_id: int) -> dict[str, Any] | None:
    cursor = await db.execute(
        "SELECT id, filename, objects_json, created_at FROM detections WHERE id = ?",
        (detection_id,),
    )
    row = await cursor.fetchone()
    if not row:
        return None
    return _row_to_detection(row)


async def update_detection(
    db: aiosqlite.Connection,
    detection_id: int,
    filename: str,
    objects: list[dict[str, Any]],
) -> int:
    cursor = await db.execute(
        "UPDATE detections SET filename = ?, objects_json = ? WHERE id = ?",
        (filename, json.dumps(objects), detection_id),
    )
    await db.commit()
    return cursor.rowcount


async def delete_detection(db: aiosqlite.Connection, detection_id: int) -> int:
    cursor = await db.execute("DELETE FROM detections WHERE id = ?", (detection_id,))
    await db.commit()
    return cursor.rowcount
