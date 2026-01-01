import sqlite3
import uuid
from typing import Optional, List, Dict, Any
from datetime import datetime
from ConsoleFormatter import ConsoleFormatter
from DatabaseManager import DatabaseManager


class Operation:
    """Класс для работы с финансовыми операциями"""

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.formatter = ConsoleFormatter()

    @staticmethod
    def validate_date(date_str: str) -> bool:
        """Проверка корректности даты в формате ГГГГ-ММ-ДД"""
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    def create_operation(self, type_: str, category_id: str, subcategory_id: Optional[str],
                         amount: float, date: str, description: Optional[str]):
        """Создание новой операции"""
        try:
            op_id = str(uuid.uuid4())
            query = """
                    INSERT INTO operations (id, type, category_id, subcategory_id, amount, date, description)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """
            self.db.execute_query(query, (op_id, type_, category_id, subcategory_id, amount, date, description))
            self.formatter.print_success(f"Операция создана успешно! ID: {op_id}")
            return op_id
        except sqlite3.Error as e:
            self.formatter.print_error(f"Ошибка при создании операции: {e}")
            return None

    def get_all_operations(self, start_date: Optional[str] = None,
                           end_date: Optional[str] = None,
                           type_: Optional[str] = None) -> List[Dict[str, Any]]:
        """Получение всех операций с фильтрацией по дате и типу"""
        try:
            query = """
                    SELECT o.*, c.name as category_name, s.name as subcategory_name
                    FROM operations o
                    JOIN categories c ON o.category_id = c.id
                    LEFT JOIN subcategories s ON o.subcategory_id = s.id
                    """
            params = []
            filters = []

            if type_:
                filters.append("o.type = ?")
                params.append(type_)

            if start_date:
                filters.append("o.date >= ?")
                params.append(start_date)
            if end_date:
                filters.append("o.date <= ?")
                params.append(end_date)

            if filters:
                query += " WHERE " + " AND ".join(filters)

            query += " ORDER BY o.date DESC"

            rows = self.db.fetch_all(query, tuple(params))

            operations = []
            for row in rows:
                operations.append({
                    'id': row['id'],
                    'type': row['type'],
                    'category_id': row['category_id'],
                    'category_name': row['category_name'],
                    'subcategory_id': row['subcategory_id'],
                    'subcategory_name': row['subcategory_name'],
                    'amount': row['amount'],
                    'date': row['date'],
                    'description': row['description']
                })

            return operations
        except sqlite3.Error as e:
            self.formatter.print_error(f"Ошибка при получении операций: {e}")
            return []

    def get_operation_by_id(self, op_id: str) -> Optional[Dict[str, Any]]:
        """Получение операции по ID"""
        try:
            query = """
                    SELECT o.*, c.name as category_name, s.name as subcategory_name
                    FROM operations o
                    JOIN categories c ON o.category_id = c.id
                    LEFT JOIN subcategories s ON o.subcategory_id = s.id
                    WHERE o.id = ?
                    """
            row = self.db.fetch_one(query, (op_id,))
            if row:
                return {
                    'id': row['id'],
                    'type': row['type'],
                    'category_id': row['category_id'],
                    'category_name': row['category_name'],
                    'subcategory_id': row['subcategory_id'],
                    'subcategory_name': row['subcategory_name'],
                    'amount': row['amount'],
                    'date': row['date'],
                    'description': row['description']
                }
            return None
        except sqlite3.Error as e:
            self.formatter.print_error(f"Ошибка при получении операции: {e}")
            return None

    def update_operation(self, op_id: str):
        """Обновление операции по ID"""
        operation = self.get_operation_by_id(op_id)
        if not operation:
            self.formatter.print_error(f"Операция с ID {op_id} не найдена!")
            return False

        self.formatter.print_info(f"Обновление операции ID: {op_id}")

        # Сумма
        amount = self.formatter.get_input(f"Сумма [{operation['amount']}]", input_type=float,
                                          default=operation['amount'],
                                          validation_func=lambda x: x > 0)
        if amount is None:
            return False

        # Дата
        date = self.formatter.get_input(f"Дата (ГГГГ-ММ-ДД) [{operation['date']}]",
                                        default=operation['date'],
                                        validation_func=Operation.validate_date)
        if date is None:
            return False

        # Описание
        description = input(f"Описание [{operation['description'] if operation['description'] else '-'}]: ").strip()
        if not description:
            description = operation['description']

        # Категория
        category_id = self.formatter.get_input(f"ID категории [{operation['category_id']}]", required=True, default=operation['category_id'])
        if category_id is None:
            return False

        # Подкатегория (опционально)
        subcategory_id = self.formatter.get_input(f"ID подкатегории [{operation['subcategory_id'] if operation['subcategory_id'] else '-'}] (Enter чтобы оставить пустым)", default=operation['subcategory_id'])
        if subcategory_id == '':
            subcategory_id = None

        # Обновляем запись
        try:
            query = """
                    UPDATE operations
                    SET amount = ?, date = ?, description = ?, category_id = ?, subcategory_id = ?
                    WHERE id = ?
                    """
            self.db.execute_query(query, (amount, date, description, category_id, subcategory_id, op_id))
            self.formatter.print_success("Операция успешно обновлена!")
            return True
        except sqlite3.Error as e:
            self.formatter.print_error(f"Ошибка при обновлении операции: {e}")
            return False

    def delete_operation(self, op_id: str):
        """Удаление операции по ID"""
        operation = self.get_operation_by_id(op_id)
        if not operation:
            self.formatter.print_error(f"Операция с ID {op_id} не найдена!")
            return False

        confirm = input(f"Удалить операцию '{op_id}'? (y/n): ").lower()
        if confirm != 'y':
            return False

        try:
            self.db.execute_query("DELETE FROM operations WHERE id = ?", (op_id,))
            self.formatter.print_success("Операция успешно удалена!")
            return True
        except sqlite3.Error as e:
            self.formatter.print_error(f"Ошибка при удалении операции: {e}")
            return False

    def show_operations_table(self, operations: List[Dict[str, Any]], title: str, show_full_ids: bool = False):
        """Отображение операций в виде таблицы"""
        if not operations:
            self.formatter.print_info("Операции не найдены!")
            return

        headers = ["ID", "Дата", "Тип", "Сумма", "Категория", "Подкатегория", "Описание"]
        rows = []

        for op in operations:
            display_id = op['id'] if show_full_ids else f"{op['id'][:8]}..."
            rows.append([
                display_id,
                op['date'],
                "📈 Доход" if op['type'] == 'income' else "📉 Расход",
                f"{op['amount']:.2f}",
                op['category_name'],
                op['subcategory_name'] if op['subcategory_name'] else "-",
                op['description'] if op['description'] else "-"
            ])

        self.formatter.print_table(headers, rows, title, show_full_ids)
