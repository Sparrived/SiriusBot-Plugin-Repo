from pathlib import Path
import sqlite3

from ..utils import MessageUnit
from .base_memory import BaseMemory

class HistoryMemory(BaseMemory):
    def __init__(self, work_path: Path):
        self._table_init_sql = '''
            CREATE TABLE IF NOT EXISTS history_memory (
                id INTEGER PRIMARY KEY,
                user_nickname TEXT,
                user_id INTEGER,
                message TEXT,
                time TEXT,
                target TEXT,
                user_card TEXT
            )
        '''
        super().__init__(work_path)


    def insert_message_unit(self, message_unit: MessageUnit):
        conn = sqlite3.connect(self._work_db)
        c = conn.cursor()
        c.execute('''
            INSERT INTO history_memory (id, user_nickname, user_id, message, time, target, user_card)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (message_unit.get_hash(), 
              message_unit.user_nickname, 
              message_unit.user_id, 
              message_unit.message, 
              message_unit.time, 
              message_unit.target,
              message_unit.user_card))
        conn.commit()
        conn.close()