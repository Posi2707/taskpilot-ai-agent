"""SQLite-backed task and note memory."""
import sqlite3
from pathlib import Path
from typing import Any


class MemoryStore:
    def __init__(self, path: str = "agent_memory.sqlite3") -> None:
        self.path = str(path)
        self._memory_connection = sqlite3.connect(":memory:") if self.path == ":memory:" else None
        Path(self.path).parent.mkdir(parents=True, exist_ok=True) if self.path != ":memory:" else None
        with self._connect() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                priority TEXT NOT NULL CHECK(priority IN ('low','medium','high')),
                status TEXT NOT NULL DEFAULT 'open' CHECK(status IN ('open','done')),
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )""")
            db.execute("""CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )""")

    def _connect(self) -> sqlite3.Connection:
        db = self._memory_connection or sqlite3.connect(self.path)
        db.row_factory = sqlite3.Row
        return db

    def add_task(self, title: str, priority: str = "medium") -> dict[str, Any]:
        with self._connect() as db:
            cur = db.execute("INSERT INTO tasks(title, priority) VALUES (?, ?)", (title, priority))
            row = db.execute("SELECT * FROM tasks WHERE id=?", (cur.lastrowid,)).fetchone()
            return dict(row)

    def list_tasks(self, status: str = "all") -> list[dict[str, Any]]:
        sql = "SELECT * FROM tasks"
        params: tuple[Any, ...] = ()
        if status != "all":
            sql += " WHERE status=?"
            params = (status,)
        sql += " ORDER BY CASE priority WHEN 'high' THEN 0 WHEN 'medium' THEN 1 ELSE 2 END, id"
        with self._connect() as db:
            return [dict(row) for row in db.execute(sql, params).fetchall()]

    def complete_task(self, task_id: int) -> dict[str, Any] | None:
        with self._connect() as db:
            db.execute("UPDATE tasks SET status='done' WHERE id=?", (task_id,))
            row = db.execute("SELECT * FROM tasks WHERE id=?", (task_id,)).fetchone()
            return dict(row) if row else None

    def add_note(self, content: str) -> None:
        with self._connect() as db:
            db.execute("INSERT INTO notes(content) VALUES (?)", (content,))

    def search_memory(self, query: str) -> list[str]:
        pattern = f"%{query}%"
        with self._connect() as db:
            tasks = db.execute("SELECT title FROM tasks WHERE title LIKE ? LIMIT 10", (pattern,)).fetchall()
            notes = db.execute("SELECT content FROM notes WHERE content LIKE ? LIMIT 10", (pattern,)).fetchall()
        return [r[0] for r in tasks] + [r[0] for r in notes]
