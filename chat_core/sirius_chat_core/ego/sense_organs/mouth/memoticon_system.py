from pathlib import Path
import sqlite3
import os
import base64
from typing import Optional

class MemoticonSystem:
    def __init__(self, work_path: Path, db_path: str = "memoticon.db", img_dir: str = "memoticon_images"):
        self._work_path = work_path
        self._db_path = work_path / db_path
        self._img_dir = work_path / img_dir
        os.makedirs(self._img_dir, exist_ok=True)
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self._db_path)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS memoticon (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                hash TEXT UNIQUE,
                path TEXT,
                tags TEXT,
                description TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def save_image(self, name: str, base64_str: str, tags: str = "", description: str = "") -> bool:
        img_path = os.path.join(self.img_dir, f"{name}.png")
        try:
            # 保存图片到本地
            with open(img_path, "wb") as f:
                f.write(base64.b64decode(base64_str))
            # 保存属性到数据库
            conn = sqlite3.connect(self._db_path)
            c = conn.cursor()
            c.execute('''
                INSERT OR REPLACE INTO memoticon (name, path, tags, description)
                VALUES (?, ?, ?, ?)
            ''', (name, img_path, tags, description))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"保存图片失败: {e}")
            return False

    def get_image(self, name: str) -> Optional[str]:
        conn = sqlite3.connect(self._db_path)
        c = conn.cursor()
        c.execute('SELECT path FROM memoticon WHERE name=?', (name,))
        row = c.fetchone()
        conn.close()
        if row:
            img_path = row[0]
            if os.path.exists(img_path):
                with open(img_path, "rb") as f:
                    return base64.b64encode(f.read()).decode("utf-8")
        return None

    def get_info(self, name: str) -> Optional[dict]:
        conn = sqlite3.connect(self._db_path)
        c = conn.cursor()
        c.execute('SELECT name, path, tags, description FROM memoticon WHERE name=?', (name,))
        row = c.fetchone()
        conn.close()
        if row:
            return {
                "name": row[0],
                "path": row[1],
                "tags": row[2],
                "description": row[3]
            }
        return None

    def list_memoticons(self) -> list:
        conn = sqlite3.connect(self._db_path)
        c = conn.cursor()
        c.execute('SELECT name FROM memoticon')
        rows = c.fetchall()
        conn.close()
        return [r[0] for r in rows]