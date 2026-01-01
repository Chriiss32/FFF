import sqlite3


class DatabaseManager:
    """Класс для управления базой данных"""

    def __init__(self, db_name: str = "finance.db"):
        self.db_name = db_name
        self.conn = None
        self.cursor = None

    def connect(self):
        """Установка соединения с базой данных"""
        self.conn = sqlite3.connect(self.db_name)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

    def disconnect(self):
        """Закрытие соединения с базой данных"""
        if self.conn:
            self.conn.close()

    def execute_query(self, query: str, params: tuple = ()):
        """Выполнение SQL запроса"""
        self.cursor.execute(query, params)
        self.conn.commit()

    def fetch_all(self, query: str, params: tuple = ()):
        """Получение всех результатов запроса"""
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def fetch_one(self, query: str, params: tuple = ()):
        """Получение одного результата запроса"""
        self.cursor.execute(query, params)
        return self.cursor.fetchone()