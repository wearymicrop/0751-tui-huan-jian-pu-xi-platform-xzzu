import sqlite3
from contextlib import contextmanager
import json
from app.config import database_path
from app.errors import BusinessError
from app.manifest import canonical


@contextmanager
def connection():
    path = database_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path, timeout=10)
    try:
        with db:
            db.execute("""CREATE TABLE IF NOT EXISTS runs (
                id TEXT PRIMARY KEY, payload TEXT NOT NULL,
                created TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )""")
            yield db
    finally:
        db.close()


def save(record):
    with connection() as db:
        cursor = db.execute("INSERT INTO runs(id, payload) VALUES (?, ?) ON CONFLICT(id) DO NOTHING",
                            (record["id"], canonical(record)))
        return cursor.rowcount == 0


def get(run_id):
    with connection() as db:
        row = db.execute("SELECT payload FROM runs WHERE id = ?", (run_id,)).fetchone()
    if row is None:
        raise BusinessError("UNKNOWN_RUN", "找不到该追溯凭证", 404)
    return json.loads(row[0])


def recent():
    with connection() as db:
        rows = db.execute("SELECT id, created, json_extract(payload, '$.query.batch') FROM runs "
                          "ORDER BY created DESC, rowid DESC LIMIT 30").fetchall()
    return [dict(id=row[0], created=row[1], batch=row[2]) for row in rows]
