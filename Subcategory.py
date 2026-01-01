import sqlite3
import uuid
from typing import Optional, List, Dict, Any

from Category import Category
from ConsoleFormatter import ConsoleFormatter


class DatabaseManager:
    pass


class Subcategory:
    """Класс для работы с подкатегориями"""

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.formatter = ConsoleFormatter()
        self.category_manager = Category(db_manager)

    def create_subcategory(self, category_id: str, name: str):
        """Создание новой подкатегории"""
        try:
            # Проверяем, существует ли уже такая подкатегория в этой категории
            existing = self.get_all_subcategories(category_id)
            for subcat in existing:
                if subcat['name'].lower() == name.lower():
                    self.formatter.print_warning(f"Подкатегория '{name}' уже существует в этой категории!")
                    return subcat['id']

            # Создаем новую подкатегорию
            subcategory_id = str(uuid.uuid4())
            query = """
                    INSERT INTO subcategories (id, category_id, name)
                    VALUES (?, ?, ?) \
                    """
            self.db.execute_query(query, (subcategory_id, category_id, name))
            self.formatter.print_success(f"Подкатегория '{name}' создана успешно! ID: {subcategory_id}")
            return subcategory_id
        except sqlite3.Error as e:
            self.formatter.print_error(f"Ошибка при создании подкатегории: {e}")
            return None

    def get_all_subcategories(self, category_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Получение всех подкатегорий с опциональной фильтрацией по категории"""
        try:
            if category_id:
                # Проверим, может быть введено имя категории вместо ID
                category = self.category_manager.get_category_by_id(category_id)
                if not category:
                    category = self.category_manager.get_category_by_name(category_id)
                    if category:
                        category_id = category['id']

                query = """
                        SELECT s.*, c.name as category_name
                        FROM subcategories s
                                 JOIN categories c ON s.category_id = c.id
                        WHERE s.category_id = ?
                        ORDER BY s.name \
                        """
                results = self.db.fetch_all(query, (category_id,))
            else:
                query = """
                        SELECT s.*, c.name as category_name
                        FROM subcategories s
                                 JOIN categories c ON s.category_id = c.id
                        ORDER BY c.name, s.name \
                        """
                results = self.db.fetch_all(query)

            subcategories = []
            for row in results:
                subcategories.append({
                    'id': row['id'],
                    'category_id': row['category_id'],
                    'name': row['name'],
                    'category_name': row['category_name']
                })
            return subcategories
        except sqlite3.Error as e:
            self.formatter.print_error(f"Ошибка при получении подкатегорий: {e}")
            return []

    def get_subcategory_by_id(self, subcategory_id: str) -> Optional[Dict[str, Any]]:
        """Получение подкатегории по ID"""
        try:
            query = """
                    SELECT s.*, c.name as category_name
                    FROM subcategories s
                             JOIN categories c ON s.category_id = c.id
                    WHERE s.id = ? \
                    """
            result = self.db.fetch_one(query, (subcategory_id,))

            if result:
                return {
                    'id': result['id'],
                    'category_id': result['category_id'],
                    'name': result['name'],
                    'category_name': result['category_name']
                }
            return None
        except sqlite3.Error as e:
            self.formatter.print_error(f"Ошибка при получении подкатегории: {e}")
            return None

    def get_subcategory_by_name(self, name: str, category_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Получение подкатегории по имени"""
        try:
            if category_name:
                query = """
                        SELECT s.*, c.name as category_name
                        FROM subcategories s
                                 JOIN categories c ON s.category_id = c.id
                        WHERE s.name = ? \
                          AND c.name = ? \
                        """
                result = self.db.fetch_one(query, (name, category_name))
            else:
                query = """
                        SELECT s.*, c.name as category_name
                        FROM subcategories s
                                 JOIN categories c ON s.category_id = c.id
                        WHERE s.name = ? \
                        """
                result = self.db.fetch_one(query, (name,))

            if result:
                return {
                    'id': result['id'],
                    'category_id': result['category_id'],
                    'name': result['name'],
                    'category_name': result['category_name']
                }
            return None
        except sqlite3.Error as e:
            self.formatter.print_error(f"Ошибка при получении подкатегории: {e}")
            return None

    def update_subcategory(self, subcategory_id: str, name: str = None,
                           category_id: str = None):
        """Обновление подкатегории"""
        try:
            subcategory = self.get_subcategory_by_id(subcategory_id)
            if not subcategory:
                # Попробуем найти по имени
                if subcategory_id and not '-' in subcategory_id:  # Если введено не UUID
                    # Спросим имя категории
                    category_name = input("Введите имя категории подкатегории: ").strip()
                    if category_name:
                        subcategory = self.get_subcategory_by_name(subcategory_id, category_name)

                if not subcategory:
                    self.formatter.print_error(f"Подкатегория '{subcategory_id}' не найдена!")
                    return False
                else:
                    subcategory_id = subcategory['id']

            if name is None:
                name = self.formatter.get_input(
                    f"Введите новое название подкатегории [{subcategory['name']}]",
                    required=True,
                    default=subcategory['name']
                )
                if name is None:
                    return False

            if category_id is None:
                # Показать текущую категорию и спросить о смене
                self.formatter.print_info(f"Текущая категория: {subcategory['category_name']}")
                change_cat = input("Изменить категорию? (y/n): ").lower()
                if change_cat == 'y':
                    # Показать все категории для выбора
                    categories = self.category_manager.get_all_categories()
                    if not categories:
                        self.formatter.print_warning("Нет доступных категорий!")
                        return False

                    self.category_manager.show_categories_table(show_full_ids=True)

                    cat_choice = self.formatter.get_input(
                        "Введите ID новой категории",
                        required=True
                    )
                    if cat_choice is None:
                        return False
                    category_id = cat_choice
                else:
                    category_id = subcategory['category_id']

            query = "UPDATE subcategories SET name = ?, category_id = ? WHERE id = ?"
            self.db.execute_query(query, (name, category_id, subcategory_id))
            self.formatter.print_success(f"Подкатегория '{name}' обновлена успешно!")
            return True
        except sqlite3.Error as e:
            self.formatter.print_error(f"Ошибка при обновлении подкатегории: {e}")
            return False

    def delete_subcategory(self, subcategory_id: str):
        """Удаление подкатегории"""
        try:
            subcategory = self.get_subcategory_by_id(subcategory_id)
            if not subcategory:
                # Попробуем найти по имени
                if subcategory_id and not '-' in subcategory_id:  # Если введено не UUID
                    # Спросим имя категории
                    category_name = input("Введите имя категории подкатегории: ").strip()
                    if category_name:
                        subcategory = self.get_subcategory_by_name(subcategory_id, category_name)

                if not subcategory:
                    self.formatter.print_error(f"Подкатегория '{subcategory_id}' не найдена!")
                    return False
                else:
                    subcategory_id = subcategory['id']

            confirm = input(f"Удалить подкатегорию '{subcategory['name']}'? (y/n): ").lower()
            if confirm != 'y':
                return False

            query = "DELETE FROM subcategories WHERE id = ?"
            self.db.execute_query(query, (subcategory_id,))
            self.formatter.print_success(f"Подкатегория '{subcategory['name']}' удалена успешно!")
            return True
        except sqlite3.Error as e:
            self.formatter.print_error(f"Ошибка при удалении подкатегории: {e}")
            return False

    def show_subcategories_table(self, category_id: Optional[str] = None, show_full_ids: bool = False):
        """Отображение подкатегорий в виде таблицы"""
        subcategories = self.get_all_subcategories(category_id)

        if not subcategories:
            if category_id:
                self.formatter.print_info(f"Подкатегории для выбранной категории не найдены!")
            else:
                self.formatter.print_info("Подкатегории не найдены!")
            return

        headers = ["ID", "Название", "Категория"]
        rows = []

        for subcat in subcategories:
            display_id = subcat['id'] if show_full_ids else f"{subcat['id'][:8]}..."
            rows.append([
                display_id,
                subcat['name'],
                subcat['category_name']
            ])

        title = "Подкатегории"
        self.formatter.print_table(headers, rows, title, show_full_ids)

        if not show_full_ids:
            self.formatter.print_info(
                "ID показаны сокращенно. Для копирования полного ID используйте команду 'Показать полные ID'")