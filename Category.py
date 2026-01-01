import sqlite3
import uuid
from typing import Optional, List, Dict, Any
from ConsoleFormatter import ConsoleFormatter
from DatabaseManager import DatabaseManager

class Category:
    """Класс для работы с категориями"""

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.formatter = ConsoleFormatter()

    def create_category(self, name: str, type_: str):
        """Создание новой категории"""
        try:
            category_id = str(uuid.uuid4())
            query = """
                    INSERT INTO categories (id, name, type)
                    VALUES (?, ?, ?) \
                    """
            self.db.execute_query(query, (category_id, name, type_))
            self.formatter.print_success(f"Категория '{name}' создана успешно! ID: {category_id}")
            return category_id
        except sqlite3.Error as e:
            self.formatter.print_error(f"Ошибка при создании категории: {e}")
            return None

    def get_all_categories(self, type_: Optional[str] = None) -> List[Dict[str, Any]]:
        """Получение всех категорий с опциональной фильтрацией по типу"""
        try:
            if type_:
                query = "SELECT * FROM categories WHERE type = ? ORDER BY name"
                results = self.db.fetch_all(query, (type_,))
            else:
                query = "SELECT * FROM categories ORDER BY name"
                results = self.db.fetch_all(query)

            categories = []
            for row in results:
                categories.append({
                    'id': row['id'],
                    'name': row['name'],
                    'type': row['type']
                })
            return categories
        except sqlite3.Error as e:
            self.formatter.print_error(f"Ошибка при получении категорий: {e}")
            return []

    def get_category_by_id(self, category_id: str) -> Optional[Dict[str, Any]]:
        """Получение категории по ID"""
        try:
            query = "SELECT * FROM categories WHERE id = ?"
            result = self.db.fetch_one(query, (category_id,))

            if result:
                return {
                    'id': result['id'],
                    'name': result['name'],
                    'type': result['type']
                }
            return None
        except sqlite3.Error as e:
            self.formatter.print_error(f"Ошибка при получении категории: {e}")
            return None

    # def get_category_by_name(self, name: str) -> Optional[Dict[str, Any]]:
    #     """Получение категории по имени"""
    #     try:
    #         query = "SELECT * FROM categories WHERE name = ?"
    #         result = self.db.fetch_one(query, (name,))
    #
    #         if result:
    #             return {
    #                 'id': result['id'],
    #                 'name': result['name'],
    #                 'type': result['type']
    #             }
    #         return None
    #     except sqlite3.Error as e:
    #         self.formatter.print_error(f"Ошибка при получении категории: {e}")
    #         return None

    def update_category(self, category_id: str, name: str = None):
        """Обновление категории"""
        try:
            category = self.get_category_by_id(category_id)
            if not category:
                # Попробуем найти по имени
                # if category_id and not '-' in category_id:  # Если введено не UUID
                #     category = self.get_category_by_name(category_id)

                if not category:
                    self.formatter.print_error(f"Категория '{category_id}' не найдена!")
                    return False
                else:
                    category_id = category['id']

            if name is None:
                name = self.formatter.get_input(
                    f"Введите новое название категории [{category['name']}]",
                    required=True,
                    default=category['name']
                )
                if name is None:
                    return False

            query = "UPDATE categories SET name = ? WHERE id = ?"
            self.db.execute_query(query, (name, category_id))
            self.formatter.print_success(f"Категория '{name}' обновлена успешно!")
            return True
        except sqlite3.Error as e:
            self.formatter.print_error(f"Ошибка при обновлении категории: {e}")
            return False

    def delete_category(self, category_id: str):
        """Удаление категории"""
        try:
            category = self.get_category_by_id(category_id)
            if not category:
                # # Попробуем найти по имени
                # if category_id and not '-' in category_id:  # Если введено не UUID
                #     category = self.get_category_by_name(category_id)

                if not category:
                    self.formatter.print_error(f"Категория '{category_id}' не найдена!")
                    return False
                else:
                    category_id = category['id']

            # Проверка наличия подкатегорий
            subcat_query = "SELECT COUNT(*) FROM subcategories WHERE category_id = ?"
            result = self.db.fetch_one(subcat_query, (category_id,))

            if result and result[0] > 0:
                self.formatter.print_warning("Нельзя удалить категорию, у которой есть подкатегории!")
                confirm = input("Удалить все подкатегории и категорию? (y/n): ").lower()
                if confirm != 'y':
                    return False

                # Удаляем подкатегории
                delete_subcats = "DELETE FROM subcategories WHERE category_id = ?"
                self.db.execute_query(delete_subcats, (category_id,))

            query = "DELETE FROM categories WHERE id = ?"
            self.db.execute_query(query, (category_id,))
            self.formatter.print_success(f"Категория '{category['name']}' удалена успешно!")
            return True
        except sqlite3.Error as e:
            self.formatter.print_error(f"Ошибка при удалении категории: {e}")
            return False

    def show_categories_table(self, type_: Optional[str] = None, show_full_ids: bool = False):
        """Отображение категорий в виде таблицы"""
        categories = self.get_all_categories(type_)

        if not categories:
            self.formatter.print_info(f"Категории типа '{type_}' не найдены!" if type_ else "Категории не найдены!")
            return

        headers = ["ID", "Название", "Тип"]
        rows = []

        for cat in categories:
            display_id = cat['id'] if show_full_ids else f"{cat['id'][:8]}..."
            rows.append([
                display_id,
                cat['name'],
                "📈 Доход" if cat['type'] == 'income' else "📉 Расход"
            ])

        title = f"Категории {'доходов' if type_ == 'income' else 'расходов' if type_ == 'expense' else ''}"
        self.formatter.print_table(headers, rows, title, show_full_ids)

        if not show_full_ids:
            self.formatter.print_info(
                "ID показаны сокращенно. Для копирования полного ID используйте команду 'Показать полные ID'")
