# curd.py
import pyodbc
from shared.conn import DEFAULT_CONN_STR

class UserCURD:
    def __init__(self, conn_str: str = None):
        self.conn_str = conn_str or DEFAULT_CONN_STR

    def _get_conn(self):
        # 文档：上下文管理器封装
        return pyodbc.connect(self.conn_str, autocommit=True)

    def ensure_table(self):
        sql = """
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='users' AND xtype='U')
        CREATE TABLE users (
            id INT IDENTITY(1,1) PRIMARY KEY,
            qq VARCHAR(20) NOT NULL,
            nickname NVARCHAR(100),
            create_time DATETIME2 DEFAULT SYSUTCDATETIME(),
            update_time DATETIME2 DEFAULT SYSUTCDATETIME()
        )
        """
        with self._get_conn() as conn:
            conn.execute(sql)

    # ---------- CRUD ----------
    def add(self, qq: str, nickname: str):
        with self._get_conn() as conn:
            conn.execute(
                "INSERT INTO users (qq, nickname) VALUES (?, ?)",
                qq, nickname
            )

    def delete(self, qq: str):
        with self._get_conn() as conn:
            conn.execute("DELETE FROM users WHERE qq=?", qq)

    def update(self, qq: str, nickname: str):
        with self._get_conn() as conn:
            conn.execute(
                "UPDATE users SET nickname=?, update_time=SYSUTCDATETIME() WHERE qq=?",
                nickname, qq
            )

    def list_all(self):
        with self._get_conn() as conn:
            rows = conn.execute(
                "SELECT qq, nickname, create_time, update_time FROM users ORDER BY id"
            ).fetchall()
        return rows

    def find(self, qq: str):
        with self._get_conn() as conn:
            return conn.execute(
                "SELECT 1 FROM users WHERE qq=?", qq
            ).fetchone()
