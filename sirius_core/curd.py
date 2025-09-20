from typing import LiteralString, Optional
import pyodbc
class SqlCURD:
    def __init__(self, conn_str : str):
        self.conn_str = conn_str
        try:
            self.ensure_table()
        except:
            raise Exception("SqlCURD初始化失败")
        

    def _get_conn(self):
        return pyodbc.connect(self.conn_str, autocommit=True)

    def ensure_table(self):
        sql = """
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='subscriptions' AND xtype='U')
        CREATE TABLE subscriptions (
            plugin_name VARCHAR(50) NOT NULL,
            id  VARCHAR(30) NOT NULL,
            target  VARCHAR(30) NOT NULL,
            create_time DATETIME2 DEFAULT SYSUTCDATETIME(),
            PRIMARY KEY (plugin_name, id, target)
        )
        """
        with self._get_conn() as conn:
            conn.execute(sql)

    # ---------- 增删查 ----------
    def add_sub(self, plugin: str, id : str, target : str):
        with self._get_conn() as conn:
            conn.execute(
                """MERGE subscriptions AS target
                  USING (SELECT ?, ?, ?) AS source(plugin_name, id, target)
                  ON target.plugin_name = source.plugin_name AND target.id = source.id AND target.target = source.target
                  WHEN NOT MATCHED THEN
                      INSERT (plugin_name, id, target) VALUES (source.plugin_name, source.id, source.target);""",
                plugin, id, target
            )

    def remove_sub(self, plugin: str, id: str, target: str):
        with self._get_conn() as conn:
            conn.execute(
                "DELETE FROM subscriptions WHERE plugin_name=? AND id=? AND target=?",
                plugin, id, target
            )
    
    def list_by_plugin(self, plugin: str, target: Optional[LiteralString] = None):
        with self._get_conn() as conn:
            if target in ("group", "private"):
                rows = conn.execute(
                    "SELECT id, target FROM subscriptions WHERE plugin_name=? AND target=? ORDER BY create_time",
                    plugin, target
                ).fetchall()
                return [r[0] for r in rows]
            else:
                rows = conn.execute(
                    "SELECT id, target FROM subscriptions WHERE plugin_name=? ORDER BY create_time",
                    plugin
                ).fetchall()
                return [(r[0], r[1]) for r in rows]

    def list_by_target_id(self, id: str, target : str):
        with self._get_conn() as conn:
            rows = conn.execute(
                "SELECT plugin_name FROM subscriptions WHERE id=? AND target=? ORDER BY create_time",
                id, target
            ).fetchall()
        return [r[0] for r in rows]
