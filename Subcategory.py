import sqlite3
import uuid
from datetime import datetime


class Subcategory:
    """Управление подкатегориями"""

    def __init__(self, db_manager):
        self.db = db_manager

    def create_subcategory(self, category_identifier, name):
        """Создание подкатегории с автоматическим созданием бюджета"""
        try:
            # Ищем категорию по ID или имени
            category = None
            if len(category_identifier) == 36:  # UUID
                query = "SELECT * FROM categories WHERE id = ?"
                category = self.db.fetch_one(query, (category_identifier,))
            else:
                query = "SELECT * FROM categories WHERE name = ?"
                category = self.db.fetch_one(query, (category_identifier,))

            if not category:
                print("❌ Категория не найдена!")
                return None

            category_id = category[0]
            category_type = category[2]  # 'income' или 'expense'

            # Проверяем, существует ли уже подкатегория с таким именем в этой категории
            check_query = "SELECT * FROM subcategories WHERE category_id = ? AND name = ?"
            existing = self.db.fetch_one(check_query, (category_id, name))

            if existing:
                print("❌ Подкатегория с таким именем уже существует в этой категории!")
                return None

            # Создаем подкатегорию
            subcategory_id = str(uuid.uuid4())
            query = "INSERT INTO subcategories (id, category_id, name) VALUES (?, ?, ?)"
            self.db.execute_query(query, (subcategory_id, category_id, name))

            print("✅ Подкатегория создана успешно!")

            # Автоматически создаем бюджет по умолчанию для ВСЕХ подкатегорий
            print("💰 Создаем бюджет по умолчанию...")

            # Находим период "Месяц" по умолчанию
            period_query = "SELECT id FROM periods WHERE name = 'Месяц'"
            period_result = self.db.fetch_one(period_query)

            if not period_result:
                # Если нет периода "Месяц", берем первый доступный
                period_query = "SELECT id FROM periods LIMIT 1"
                period_result = self.db.fetch_one(period_query)

            if period_result:
                period_id = period_result[0]
                planned_amount = 0.0

                # Получаем коэффициент периода
                period_count_query = "SELECT period_count FROM periods WHERE id = ?"
                period_count_result = self.db.fetch_one(period_count_query, (period_id,))
                period_count = period_count_result[0] if period_count_result else 12
                year_forecast = planned_amount * period_count

                # Создаем бюджет
                plan_id = str(uuid.uuid4())
                budget_query = """
                               INSERT INTO plan_subcategories
                               (id, category_id, subcategory_id, period_id, planned_amount, year_forecast)
                               VALUES (?, ?, ?, ?, ?, ?) \
                               """
                self.db.execute_query(budget_query,
                                      (plan_id, category_id, subcategory_id, period_id, planned_amount, year_forecast))
                print("✅ Бюджет по умолчанию создан!")
            else:
                print("⚠️  Нет доступных периодов для создания бюджета")

            return subcategory_id

        except sqlite3.Error as e:
            print(f"❌ Ошибка при создании подкатегории: {e}")
            return None

    # Остальные методы остаются без изменений...
    def get_all_subcategories(self, category_id=None):
        """Получение всех подкатегорий"""
        try:
            if category_id:
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
                    'id': row[0],
                    'category_id': row[1],
                    'name': row[2],
                    'category_name': row[3]
                })

            return subcategories

        except sqlite3.Error as e:
            print(f"Ошибка при получении подкатегорий: {e}")
            return []

    def get_subcategory_by_id(self, subcategory_id):
        """Получить подкатегорию по ID"""
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
                    'id': result[0],
                    'category_id': result[1],
                    'name': result[2],
                    'category_name': result[3]
                }
            return None

        except sqlite3.Error as e:
            print(f"Ошибка при получении подкатегории: {e}")
            return None

    def update_subcategory(self, identifier):
        """Обновление подкатегории"""
        try:
            # Сначала ищем подкатегорию по ID или имени
            subcategory = None
            if len(identifier) == 36:  # UUID
                query = "SELECT * FROM subcategories WHERE id = ?"
                subcategory = self.db.fetch_one(query, (identifier,))
            else:
                # Ищем по имени
                query = """
                        SELECT s.*, c.name as category_name
                        FROM subcategories s
                                 JOIN categories c ON s.category_id = c.id
                        WHERE s.name = ? \
                        """
                result = self.db.fetch_one(query, (identifier,))
                if result:
                    subcategory = result

            if not subcategory:
                print("❌ Подкатегория не найдена!")
                return

            print(f"\n📝 Обновление подкатегории: {subcategory[2]}")
            print(f"📂 Категория: {subcategory[1] if len(subcategory) == 3 else subcategory[3]}")
            print("\nЧто вы хотите обновить?")
            print("1. Название подкатегории")
            print("2. Категорию")
            print("0. Отмена")

            choice = input("\nВыберите действие (0-2): ").strip()

            if choice == '0':
                print("Отмена обновления.")
                return
            elif choice == '1':
                new_name = input("Введите новое название подкатегории: ").strip()
                if new_name:
                    update_query = "UPDATE subcategories SET name = ? WHERE id = ?"
                    self.db.execute_query(update_query, (new_name, subcategory[0]))
                    print("✅ Название подкатегории обновлено!")
            elif choice == '2':
                # Показываем доступные категории
                from Category import Category
                cat_manager = Category(self.db)
                cat_manager.show_categories_table()

                new_category_id = input("Введите ID новой категории: ").strip()
                if new_category_id:
                    update_query = "UPDATE subcategories SET category_id = ? WHERE id = ?"
                    self.db.execute_query(update_query, (new_category_id, subcategory[0]))
                    print("✅ Категория подкатегории обновлена!")
            else:
                print("❌ Неверный выбор!")

        except sqlite3.Error as e:
            print(f"❌ Ошибка при обновлении подкатегории: {e}")

    def delete_subcategory(self, identifier):
        """Удаление подкатегории"""
        try:
            # Сначала ищем подкатегорию по ID или имени
            subcategory = None
            if len(identifier) == 36:  # UUID
                query = "SELECT * FROM subcategories WHERE id = ?"
                subcategory = self.db.fetch_one(query, (identifier,))
            else:
                # Ищем по имени, может быть несколько с одинаковыми именами
                print("⚠️  Найдено несколько подкатегорий с таким именем:")
                query = """
                        SELECT s.*, c.name as category_name
                        FROM subcategories s
                                 JOIN categories c ON s.category_id = c.id
                        WHERE s.name = ? \
                        """
                results = self.db.fetch_all(query, (identifier,))

                if results:
                    print("\nПодкатегории с именем '{}':".format(identifier))
                    for i, row in enumerate(results, 1):
                        print(f"{i}. ID: {row[0][:8]}... | Категория: {row[3]}")

                    choice = input("\nВыберите номер подкатегории для удаления (0 для отмены): ").strip()
                    try:
                        choice_idx = int(choice)
                        if 1 <= choice_idx <= len(results):
                            subcategory = results[choice_idx - 1]
                    except ValueError:
                        print("❌ Неверный выбор!")
                        return

            if not subcategory:
                print("❌ Подкатегория не найдена!")
                return

            confirm = input(f"\nВы уверены, что хотите удалить подкатегорию '{subcategory[2]}'? (y/n): ").lower()
            if confirm == 'y':
                delete_query = "DELETE FROM subcategories WHERE id = ?"
                self.db.execute_query(delete_query, (subcategory[0],))
                print("✅ Подкатегория удалена!")
            else:
                print("❌ Удаление отменено.")

        except sqlite3.Error as e:
            print(f"❌ Ошибка при удалении подкатегории: {e}")

    def show_subcategories_table(self, category_id=None, show_full_ids=False):
        """Отображение таблицы подкатегорий"""
        subcategories = self.get_all_subcategories(category_id)

        if not subcategories:
            print("📭 Подкатегории не найдены")
            return

        headers = ["ID", "Категория", "Название подкатегории"]
        rows = []

        for subcat in subcategories:
            subcat_id = subcat['id'] if show_full_ids else subcat['id'][:8] + "..."
            rows.append([subcat_id, subcat['category_name'], subcat['name']])

        from ConsoleFormatter import ConsoleFormatter
        formatter = ConsoleFormatter()
        formatter.print_table(headers, rows)