from datetime import datetime
import os
from pathlib import Path
import requests

def fetch_png(api_url: str, work_space : Path) -> str:
    """下载 png -> 返回本地绝对路径"""
    try:
        resp = requests.get(api_url, timeout=15)
        resp.raise_for_status()
        fname = f"news_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        with work_space:
            path = work_space / "imgs"
            if not path.exists():
                path.mkdir()
            path = path / fname
            with open(path, "wb") as f:
                f.write(resp.content)
        return str(path.absolute())
    except Exception as e:
        raise RuntimeError(f"下载图片失败：{e}")