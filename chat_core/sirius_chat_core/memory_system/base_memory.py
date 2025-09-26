from pathlib import Path
import sqlite3


class BaseMemory:
    def __init__(self, work_path: Path):
        self._work_path = work_path
        self._work_db = work_path / "memory" / "memory.db"
        self._table_init_sql = ""

    def _init_db(self):
        conn = sqlite3.connect(self._work_db)
        c = conn.cursor()
        c.execute(self._table_init_sql)
        conn.commit()
        conn.close()