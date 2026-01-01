# Period.py
import sqlite3
import uuid
from typing import Optional, List, Dict, Any
from DatabaseManager import DatabaseManager
from ConsoleFormatter import ConsoleFormatter


class Period:
    """Класс для работы с периодами планирования"""

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.formatter = ConsoleFormatter()

    def create_period(self, name: str, period_count: int):
        """Создание нового периода"""
        try:
            # Проверяем, существует ли уже период с таким названием
            existing = self.get_period_by_name(name)
            if existing:
                self.formatter.print_warning(f"Период '{name}' уже существует!")
                return existing['id']

            period_id = str(uuid.uuid4())
            query = "INSERT INTO periods (id, name, period_count) VALUES (?, ?, ?)"
            self.db.execute_query(query, (period_id, name, period_count))
            self.formatter.print_success(f"Период '{name}' создан успешно! ID: {period_id}")
            return period_id
        except sqlite3.Error as e:
            self.formatter.print_error(f"Ошибка при создании периода: {e}")
            return None

    def get_all_periods(self) -> List[Dict[str, Any]]:
        """Получение всех периодов"""
        try:
            query = "SELECT * FROM periods ORDER BY period_count"
            results = self.db.fetch_all(query)

            periods = []
            for row in results:
                periods.append({
                    'id': row['id'],
                    'name': row['name'],
                    'period_count': row['period_count']
                })
            return periods
        except sqlite3.Error as e:
            self.formatter.print_error(f"Ошибка при получении периодов: {e}")
            return []

    def get_period_by_id(self, period_id: str) -> Optional[Dict[str, Any]]:
        """Получение периода по ID"""
        try:
            query = "SELECT * FROM periods WHERE id = ?"
            result = self.db.fetch_one(query, (period_id,))

            if result:
                return {
                    'id': result['id'],
                    'name': result['name'],
                    'period_count': result['period_count']
                }
            return None
        except sqlite3.Error as e:
            self.formatter.print_error(f"Ошибка при получении периода: {e}")
            return None

    def get_period_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Получение периода по имени"""
        try:
            query = "SELECT * FROM periods WHERE name = ?"
            result = self.db.fetch_one(query, (name,))

            if result:
                return {
                    'id': result['id'],
                    'name': result['name'],
                    'period_count': result['period_count']
                }
            return None
        except sqlite3.Error as e:
            self.formatter.print_error(f"Ошибка при получении периода: {e}")
            return None

    def show_periods_table(self):
        """Отображение периодов в виде таблицы"""
        periods = self.get_all_periods()

        if not periods:
            self.formatter.print_info("Периоды не найдены!")
            return

        headers = ["ID", "Название", "Периодов в году"]
        rows = []

        for period in periods:
            rows.append([
                period['id'],
                period['name'],
                str(period['period_count'])
            ])

        self.formatter.print_table(headers, rows, "Периоды планирования")

    def get_period_by_id(self, period_id):
        """Получить период по ID"""
        try:
            query = "SELECT * FROM periods WHERE id = ?"
            result = self.db.fetch_one(query, (period_id,))

            if result:
                return {
                    'id': result[0],
                    'name': result[1],
                    'period_count': result[2]
                }
            return None

        except sqlite3.Error as e:
            print(f"Ошибка при получении периода: {e}")
            return None