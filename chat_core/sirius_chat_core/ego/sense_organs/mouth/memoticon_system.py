import hashlib
from io import BytesIO
from pathlib import Path
import random
import sqlite3
import os
import base64
from typing import Optional
from PIL import Image

from ....models.memoticon_model import MemoticonModel

class MemoticonSystem:
    def __init__(self, work_path: Path, model: MemoticonModel, db_path: str = "memoticon.db", img_dir: str = "memoticon_images"):
        self._work_path = work_path
        self._db_path = work_path / db_path
        self._img_dir = work_path / img_dir
        self._model = model
        os.makedirs(self._img_dir, exist_ok=True)
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self._db_path)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS memoticon (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hash TEXT UNIQUE,
                tags TEXT,
                description TEXT
            )
        ''')
        conn.commit()
        conn.close()
    
    def judge_img(self, img_base64: str) -> Optional[str]:
        """判断图片是否为表情包"""
        img_base64 = self._resize_image(img_base64)
        img_hash = hashlib.sha256(img_base64.encode()).hexdigest()
        conn = sqlite3.connect(self._db_path)
        c = conn.cursor()
        c.execute('SELECT hash FROM memoticon WHERE hash=?', (img_hash,))
        if c.fetchone():
            conn.close()
            return None
        result = self._model.judge_meme(img_base64)
        if result["is_meme"]:
            if result["meme_type"]:
                return self.save_image(img_base64, tags=",".join(result["meme_type"]), description=result["desp"])
        return None
    
    def _resize_image(self,img_path: str, max_edge: int = 128) -> str:
        """缩放图片，确保其在QQ内显示大小合理，返回base64编码"""
        # 打开图片
        img = Image.open(BytesIO(base64.b64decode(img_path)))
        w, h = img.size
        scale = min(max_edge / max(w, h), 1.0)
        # 计算新尺寸
        new_size = (int(w * scale), int(h * scale))
        # 缩放图片
        img_resized = img.resize(new_size, Image.Resampling.NEAREST)
        # 再编码为 base64
        buffer = BytesIO()
        img_resized.save(buffer, format=img.format or "jpg")
        return base64.b64encode(buffer.getvalue()).decode("utf-8")
    

    def save_image(self, base64_str: str, tags: str = "", description: str = "") -> Optional[str]:
        tags = tags.replace("可爱", "喜悦")
        # 计算图片哈希
        img_hash = hashlib.sha256(base64_str.encode()).hexdigest()
        img_path = os.path.join(self._img_dir, f"{img_hash}.jpg")
        try:
            conn = sqlite3.connect(self._db_path)
            c = conn.cursor()
            c.execute('SELECT hash FROM memoticon WHERE hash=?', (img_hash,))
            if c.fetchone():
                conn.close()
                return None
            # 保存图片到本地
            with open(img_path, "wb") as f:
                f.write(base64.b64decode(base64_str))
            # 保存属性到数据库
            c.execute('''
                INSERT OR REPLACE INTO memoticon (hash, tags, description)
                VALUES (?, ?, ?)
            ''', (img_hash, tags, description))
            conn.commit()
            conn.close()
            result_msg = f"保存表情包成功，哈希值: {img_hash}，标签: {tags}，描述: {description}，路径: {img_path}"
            return result_msg
        except Exception as e:
            raise ValueError(f"保存表情包失败: {e}")

    def get_image(self, tag: str) -> Optional[str]:
        conn = sqlite3.connect(self._db_path)
        c = conn.cursor()
        c.execute('SELECT hash FROM memoticon WHERE tags LIKE ?', (f"%{tag}%",))
        rows = c.fetchall()
        conn.close()
        if rows:
            img = random.choice(rows)
            img_path = os.path.join(self._img_dir, f"{img[0]}.jpg")
            return img_path
            # if os.path.exists(img_path):
            #     with open(img_path, "rb") as f:
            #         return base64.b64encode(f.read()).decode("utf-8")
        return None

    def get_info(self, hash: str) -> Optional[dict]:
        conn = sqlite3.connect(self._db_path)
        c = conn.cursor()
        c.execute('SELECT hash, tags, description FROM memoticon WHERE hash=?', (hash,))
        row = c.fetchone()
        conn.close()
        if row:
            return {
                "hash": row[0],
                "tags": row[1],
                "description": row[2]
            }
        return None

    def list_memoticons(self) -> list:
        conn = sqlite3.connect(self._db_path)
        c = conn.cursor()
        c.execute('SELECT hash FROM memoticon')
        rows = c.fetchall()
        conn.close()
        return [r[0] for r in rows]