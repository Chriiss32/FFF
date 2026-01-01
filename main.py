import sqlite3
import uuid
from datetime import datetime
import os
from Category import Category
from ConsoleFormatter import ConsoleFormatter
from DatabaseManager import DatabaseManager
from Operation import Operation
from Subcategory import Subcategory


class FinanceApp:
    """Главный класс приложения"""

    def __init__(self):
        self.db = DatabaseManager()
        self.db.connect()
        self.category_manager = Category(self.db)
        self.subcategory_manager = Subcategory(self.db)
        self.operation_manager = Operation(self.db)
        self.formatter = ConsoleFormatter()

    def clear_screen(self):
        """Очистка экрана консоли"""
        os.system('cls' if os.name == 'nt' else 'clear')

    def show_main_menu(self):
        """Отображение главного меню"""
        self.clear_screen()
        self.formatter.print_header("Управление личными финансами")

        self.formatter.print_menu([
            "📁 Управление категориями",
            "📂 Управление подкатегориями",
            "💰 Управление операциями",
            "📊 Просмотр отчетов",
            "❌ Выход"
        ])

        choice = self.formatter.get_input("Выберите действие", input_type=int,
                                          validation_func=lambda x: 1 <= x <= 5)
        return choice

    def handle_category_menu(self):
        """Обработка меню категорий"""
        while True:
            self.clear_screen()
            self.formatter.print_header("Управление категориями")

            self.formatter.print_menu([
                "➕ Создать категорию",
                "👁️ Просмотреть все категории (полные ID)",
                "📝 Обновить категорию",
                "🗑️ Удалить категорию",
                "🔙 Назад в главное меню"
            ])

            choice = self.formatter.get_input("Выберите действие", input_type=int,
                                              validation_func=lambda x: 1 <= x <= 6)

            if choice == 1:
                self.handle_category_creation()
            elif choice ==  2:
                self.handle_category_list(show_full_ids=True)
            elif choice == 3:
                self.handle_category_update()
            elif choice == 4:
                self.handle_category_delete()
            elif choice == 5:
                break
            else:
                self.formatter.print_error("Неверный выбор!")

    def handle_category_creation(self):
        """Обработка создания категории"""
        self.clear_screen()
        self.formatter.print_header("Создание категории")

        name = self.formatter.get_input("Название категории", required=True)
        if name is None:
            return

        self.formatter.print_menu(["📈 Доход", "📉 Расход"], "Тип категории")
        type_choice = self.formatter.get_input("Выберите тип", input_type=int,
                                               validation_func=lambda x: 1 <= x <= 2)
        if type_choice is None:
            return

        type_ = 'income' if type_choice == 1 else 'expense'

        self.category_manager.create_category(name, type_)

    def handle_category_list(self, show_full_ids: bool = False):
        """Обработка просмотра категорий"""
        self.clear_screen()
        if show_full_ids:
            self.formatter.print_header("Просмотр категорий (полные ID)")
        else:
            self.formatter.print_header("Просмотр категорий (сокращенные ID)")

        self.formatter.print_menu([
            "Все категории",
            "Только доходы",
            "Только расходы"
        ], "Фильтр")

        filter_choice = self.formatter.get_input("Выберите фильтр", input_type=int,
                                                 validation_func=lambda x: 1 <= x <= 3)
        if filter_choice is None:
            return

        type_ = None
        if filter_choice == 2:
            type_ = 'income'
        elif filter_choice == 3:
            type_ = 'expense'

        self.category_manager.show_categories_table(type_, show_full_ids)

        if show_full_ids:
            self.formatter.print_info("Полные ID показаны. Вы можете скопировать их для обновления/удаления.")

    def handle_category_update(self):
        """Обработка обновления категории"""
        self.clear_screen()
        self.formatter.print_header("Обновление категории")

        # Показываем все категории с полными ID
        categories = self.category_manager.get_all_categories()
        if categories:
            self.category_manager.show_categories_table(show_full_ids=True)
        else:
            self.formatter.print_info("Категории не найдены!")
            return

        self.formatter.print_info("Вы можете ввести:")
        print("1. Полный ID категории (скопируйте из таблицы выше)")
        identifier = self.formatter.get_input("Введите ID для обновления", required=True)
        if identifier is None:
            return

        self.category_manager.update_category(identifier)

    def handle_category_delete(self):
        """Обработка удаления категории"""
        self.clear_screen()
        self.formatter.print_header("Удаление категории")

        # Показываем все категории с полными ID
        categories = self.category_manager.get_all_categories()
        if categories:
            self.category_manager.show_categories_table(show_full_ids=True)
        else:
            self.formatter.print_info("Категории не найдены!")
            return

        self.formatter.print_info("Вы можете ввести:")
        print("1. Полный ID категории (скопируйте из таблицы выше)")
        identifier = self.formatter.get_input("Введите ID для удаления", required=True)
        if identifier is None:
            return

        self.category_manager.delete_category(identifier)

    def handle_subcategory_menu(self):
        """Обработка меню подкатегорий"""
        while True:
            self.clear_screen()
            self.formatter.print_header("Управление подкатегориями")

            self.formatter.print_menu([
                "➕ Создать подкатегорию",
                "👁️ Просмотреть все подкатегории (полные ID)",
                "📝 Обновить подкатегорию",
                "🗑️ Удалить подкатегорию",
                "🔙 Назад в главное меню"
            ])

            choice = self.formatter.get_input("Выберите действие", input_type=int,
                                              validation_func=lambda x: 1 <= x <= 6)

            if choice == 1:
                self.handle_subcategory_creation()
            elif choice == 2:
                self.handle_subcategory_list(show_full_ids=True)
            elif choice == 3:
                self.handle_subcategory_update()
            elif choice == 4:
                self.handle_subcategory_delete()
            elif choice == 5:
                break
            else:
                self.formatter.print_error("Неверный выбор!")

    def handle_subcategory_creation(self):
        """Обработка создания подкатегории"""
        self.clear_screen()
        self.formatter.print_header("Создание подкатегории")

        # Показать доступные категории
        categories = self.category_manager.get_all_categories()
        if not categories:
            self.formatter.print_warning("Сначала создайте категории!")
            return

        self.category_manager.show_categories_table(show_full_ids=True)

        self.formatter.print_info("Вы можете ввести:")
        print("1. Полный ID категории (скопируйте из таблицы выше)")

        category_identifier = self.formatter.get_input("Введите ID", required=True)
        if category_identifier is None:
            return

        name = self.formatter.get_input("Название подкатегории", required=True)
        if name is None:
            return

        self.subcategory_manager.create_subcategory(category_identifier, name)

    def handle_subcategory_list(self, show_full_ids: bool = False):
        """Обработка просмотра подкатегорий"""
        self.clear_screen()
        if show_full_ids:
            self.formatter.print_header("Просмотр подкатегорий (полные ID)")
        else:
            self.formatter.print_header("Просмотр подкатегорий (сокращенные ID)")

        # Показать категории для фильтрации
        categories = self.category_manager.get_all_categories()
        if categories:
            self.category_manager.show_categories_table(show_full_ids=True)

            filter_choice = input("\nВведите ID для фильтрации (или Enter для всех): ").strip()
            if filter_choice:
                self.subcategory_manager.show_subcategories_table(filter_choice, show_full_ids)
            else:
                self.subcategory_manager.show_subcategories_table(None, show_full_ids)
        else:
            self.formatter.print_info("Категории не найдены!")

        if show_full_ids:
            self.formatter.print_info("Полные ID показаны. Вы можете скопировать их для обновления/удаления.")

    def handle_subcategory_update(self):
        """Обработка обновления подкатегории"""
        self.clear_screen()
        self.formatter.print_header("Обновление подкатегории")

        # Показываем все подкатегории с полными ID
        subcategories = self.subcategory_manager.get_all_subcategories()
        if subcategories:
            self.subcategory_manager.show_subcategories_table(show_full_ids=True)
        else:
            self.formatter.print_info("Подкатегории не найдены!")
            return

        self.formatter.print_info("Вы можете ввести:")
        print("1. Полный ID подкатегории (скопируйте из таблицы выше)")
        print("2. Имя подкатегории (тогда потребуется ввести имя категории)")

        identifier = self.formatter.get_input("Введите ID или имя подкатегории для обновления", required=True)
        if identifier is None:
            return

        self.subcategory_manager.update_subcategory(identifier)

    def handle_subcategory_delete(self):
        """Обработка удаления подкатегории"""
        self.clear_screen()
        self.formatter.print_header("Удаление подкатегории")

        # Показываем все подкатегории с полными ID
        subcategories = self.subcategory_manager.get_all_subcategories()
        if subcategories:
            self.subcategory_manager.show_subcategories_table(show_full_ids=True)
        else:
            self.formatter.print_info("Подкатегории не найдены!")
            return

        self.formatter.print_info("Вы можете ввести:")
        print("1. Полный ID подкатегории (скопируйте из таблицы выше)")
        print("2. Имя подкатегории (тогда потребуется ввести имя категории)")

        identifier = self.formatter.get_input("Введите ID или имя подкатегории для удаления", required=True)
        if identifier is None:
            return

        self.subcategory_manager.delete_subcategory(identifier)

    def handle_operation_menu(self):
        """Обработка меню операций"""
        while True:
            self.clear_screen()
            self.formatter.print_header("Управление операциями")

            self.formatter.print_menu([
                "➕ Создать операцию",
                "👁️ Просмотреть все операции (сокращенные ID)",
                "👁️ Просмотреть все операции (полные ID)",
                "🔍 Поиск операции по ID",
                "📝 Обновить операцию",
                "🗑️ Удалить операцию",
                "🔙 Назад в главное меню"
            ])

            choice = self.formatter.get_input("Выберите действие", input_type=int,
                                              validation_func=lambda x: 1 <= x <= 7)

            if choice == 1:
                self.handle_operation_creation()
            elif choice == 2:
                self.handle_operation_list(show_full_ids=False)
            elif choice == 3:
                self.handle_operation_list(show_full_ids=True)
            elif choice == 4:
                self.handle_operation_search()
            elif choice == 5:
                self.handle_operation_update()
            elif choice == 6:
                self.handle_operation_delete()
            elif choice == 7:
                break
            else:
                self.formatter.print_error("Неверный выбор!")

    def handle_operation_creation(self):
        """Обработка создания операции"""
        self.clear_screen()
        self.formatter.print_header("Создание операции")

        # Тип операции
        self.formatter.print_menu(["📈 Доход", "📉 Расход"], "Тип операции")
        type_choice = self.formatter.get_input("Выберите тип", input_type=int,
                                               validation_func=lambda x: 1 <= x <= 2)
        if type_choice is None:
            return

        type_ = 'income' if type_choice == 1 else 'expense'

        # Выбор категории
        categories = self.category_manager.get_all_categories(type_)
        if not categories:
            self.formatter.print_error(f"Сначала создайте категории типа '{type_}'!")
            return

        self.category_manager.show_categories_table(type_, show_full_ids=True)
        category_identifier = self.formatter.get_input("Введите ID категории", required=True)
        if category_identifier is None:
            return

        category = self.category_manager.get_category_by_id(category_identifier)
        if not category:
            self.formatter.print_error(f"Категория с ID '{category_identifier}' не найдена!")
            return
        category_id = category['id']

        # Выбор подкатегории
        subcategories = self.subcategory_manager.get_all_subcategories(category_id)
        subcategory_id = None

        if subcategories:
            self.subcategory_manager.show_subcategories_table(category_id, show_full_ids=True)

        subcategory_input = input("Введите ID или имя подкатегории (Enter чтобы пропустить): ").strip()
        if subcategory_input:
            # Сначала ищем по ID
            subcat = self.subcategory_manager.get_subcategory_by_id(subcategory_input)
            if subcat and subcat['category_id'] == category_id:
                subcategory_id = subcat['id']
            else:
                # Ищем по имени в текущей категории
                for s in subcategories:
                    if s['name'].lower() == subcategory_input.lower():
                        subcategory_id = s['id']
                        break
                # Если не нашли — создаём новую
                if not subcategory_id:
                    create_new = input(f"Подкатегория '{subcategory_input}' не найдена. Создать новую? (y/n): ").lower()
                    if create_new == 'y':
                        subcategory_id = self.subcategory_manager.create_subcategory(category_id, subcategory_input)

        # Ввод суммы
        amount = self.formatter.get_input("Сумма", input_type=float, validation_func=lambda x: x > 0)
        if amount is None:
            return

        # Ввод даты
        today = datetime.now().strftime("%Y-%m-%d")
        date = self.formatter.get_input(f"Дата (ГГГГ-ММ-ДД) [{today}]", default=today,
                                        validation_func=lambda x: self.operation_manager.validate_date(x))
        if date is None:
            return

        # Ввод описания
        description = input("Описание (опционально, Enter чтобы пропустить): ").strip()

        # Создание операции
        self.operation_manager.create_operation(type_, category_id, subcategory_id, amount, date, description)
        self.formatter.print_success("Операция создана успешно!")

    def handle_operation_list(self, show_full_ids: bool = False):
        """Обработка просмотра операций"""
        self.clear_screen()
        if show_full_ids:
            self.formatter.print_header("Просмотр операций (полные ID)")
        else:
            self.formatter.print_header("Просмотр операций (сокращенные ID)")

        self.formatter.print_menu([
            "Все операции",
            "Только доходы",
            "Только расходы",
            "По датам"
        ], "Фильтр")

        filter_choice = self.formatter.get_input("Выберите фильтр", input_type=int,
                                                 validation_func=lambda x: 1 <= x <= 4)
        if filter_choice is None:
            return

        type_ = None
        start_date = None
        end_date = None

        if filter_choice == 2:
            type_ = 'income'
        elif filter_choice == 3:
            type_ = 'expense'
        elif filter_choice == 4:
            start_date = self.formatter.get_input("Дата начала (ГГГГ-ММ-ДД)",
                                                  validation_func=lambda x: self.operation_manager._validate_date(x))
            if start_date is None:
                return

            end_date = self.formatter.get_input("Дата окончания (ГГГГ-ММ-ДД)",
                                                validation_func=lambda x: self.operation_manager._validate_date(x))
            if end_date is None:
                return

        operations = self.operation_manager.get_all_operations(start_date, end_date, type_)

        if operations:
            # Выводим статистику
            total_income = sum(op['amount'] for op in operations if op['type'] == 'income')
            total_expense = sum(op['amount'] for op in operations if op['type'] == 'expense')
            balance = total_income - total_expense

            self.formatter.print_header("Статистика")
            print(f"📈 Всего доходов: {total_income:.2f}")
            print(f"📉 Всего расходов: {total_expense:.2f}")
            print(f"💰 Баланс: {balance:.2f}")

            # Выводим операции
            title = f"Операции ({len(operations)})"
            self.operation_manager.show_operations_table(operations, title, show_full_ids)
        else:
            self.formatter.print_info("Операции не найдены!")

        if show_full_ids:
            self.formatter.print_info("Полные ID показаны. Вы можете скопировать их для обновления/удаления.")

    def handle_operation_search(self):
        """Обработка поиска операции по ID"""
        self.clear_screen()
        self.formatter.print_header("Поиск операции")

        operation_id = self.formatter.get_input("Введите ID операции", required=True)
        if operation_id is None:
            return

        operation = self.operation_manager.get_operation_by_id(operation_id)

        if operation:
            self.formatter.print_header("Детали операции")

            headers = ["Поле", "Значение"]
            rows = [
                ["ID", operation['id']],
                ["Тип", "📈 Доход" if operation['type'] == 'income' else "📉 Расход"],
                ["Дата", operation['date']],
                ["Сумма", f"{operation['amount']:.2f}"],
                ["Категория", operation['category_name']],
                ["Подкатегория", operation['subcategory_name'] if operation['subcategory_name'] else "-"],
                ["Описание", operation['description'] if operation['description'] else "-"]
            ]

            self.formatter.print_table(headers, rows)
        else:
            self.formatter.print_error("Операция не найдена!")

    def handle_operation_update(self):
        """Обработка обновления операции"""
        self.clear_screen()
        self.formatter.print_header("Обновление операции")

        # Показываем последние 10 операций с полными ID
        recent_ops = self.operation_manager.get_all_operations()
        if recent_ops:
            self.formatter.print_info("Последние операции (полные ID):")
            self.operation_manager.show_operations_table(recent_ops[:10], "Последние 10 операций", show_full_ids=True)
        else:
            self.formatter.print_info("Операции не найдены!")

        operation_id = self.formatter.get_input("Введите ID операции для обновления", required=True)
        if operation_id is None:
            return

        self.operation_manager.update_operation(operation_id)

    def handle_operation_delete(self):
        """Обработка удаления операции"""
        self.clear_screen()
        self.formatter.print_header("Удаление операции")

        # Показываем последние 10 операций с полными ID
        recent_ops = self.operation_manager.get_all_operations()
        if recent_ops:
            self.formatter.print_info("Последние операции (полные ID):")
            self.operation_manager.show_operations_table(recent_ops[:10], "Последние 10 операций", show_full_ids=True)
        else:
            self.formatter.print_info("Операции не найдены!")

        operation_id = self.formatter.get_input("Введите ID операции для удаления", required=True)
        if operation_id is None:
            return

        self.operation_manager.delete_operation(operation_id)

    def show_reports(self):
        """Отображение отчетов"""
        self.clear_screen()
        self.formatter.print_header("Финансовые отчеты")

        # Получаем все операции
        operations = self.operation_manager.get_all_operations()

        if not operations:
            self.formatter.print_info("Нет данных для отчетов!")
            return

        # Общая статистика
        total_income = sum(op['amount'] for op in operations if op['type'] == 'income')
        total_expense = sum(op['amount'] for op in operations if op['type'] == 'expense')
        balance = total_income - total_expense

        self.formatter.print_header("Общая статистика")

        headers = ["Показатель", "Значение"]
        rows = [
            ["Всего операций", len(operations)],
            ["Операций доходов", sum(1 for op in operations if op['type'] == 'income')],
            ["Операций расходов", sum(1 for op in operations if op['type'] == 'expense')],
            ["Общий доход", f"{total_income:.2f}"],
            ["Общий расход", f"{total_expense:.2f}"],
            ["Баланс", f"{balance:.2f}"]
        ]

        self.formatter.print_table(headers, rows)

        # Расходы по категориям
        expense_by_category = {}
        for op in operations:
            if op['type'] == 'expense':
                cat_name = op['category_name']
                expense_by_category[cat_name] = expense_by_category.get(cat_name, 0) + op['amount']

        if expense_by_category:
            self.formatter.print_header("Расходы по категориям")

            headers = ["Категория", "Сумма", "Доля"]
            rows = []
            for category, amount in sorted(expense_by_category.items(), key=lambda x: x[1], reverse=True):
                percentage = (amount / total_expense * 100) if total_expense > 0 else 0
                rows.append([category, f"{amount:.2f}", f"{percentage:.1f}%"])

            self.formatter.print_table(headers, rows)

        # Доходы по категориям
        income_by_category = {}
        for op in operations:
            if op['type'] == 'income':
                cat_name = op['category_name']
                income_by_category[cat_name] = income_by_category.get(cat_name, 0) + op['amount']

        if income_by_category:
            self.formatter.print_header("Доходы по категориям")

            headers = ["Категория", "Сумма", "Доля"]
            rows = []
            for category, amount in sorted(income_by_category.items(), key=lambda x: x[1], reverse=True):
                percentage = (amount / total_income * 100) if total_income > 0 else 0
                rows.append([category, f"{amount:.2f}", f"{percentage:.1f}%"])

            self.formatter.print_table(headers, rows)

        # Ежемесячная статистика
        monthly_stats = {}
        for op in operations:
            month = op['date'][:7]  # ГГГГ-ММ
            if month not in monthly_stats:
                monthly_stats[month] = {'income': 0, 'expense': 0}

            if op['type'] == 'income':
                monthly_stats[month]['income'] += op['amount']
            else:
                monthly_stats[month]['expense'] += op['amount']

        if monthly_stats:
            self.formatter.print_header("Ежемесячная статистика")

            headers = ["Месяц", "Доход", "Расход", "Баланс"]
            rows = []
            for month in sorted(monthly_stats.keys(), reverse=True):
                stats = monthly_stats[month]
                balance = stats['income'] - stats['expense']
                rows.append([
                    month,
                    f"{stats['income']:.2f}",
                    f"{stats['expense']:.2f}",
                    f"{balance:.2f}"
                ])

            self.formatter.print_table(headers, rows)

    def run(self):
        """Запуск приложения"""
        try:
            while True:
                choice = self.show_main_menu()

                if choice == 1:
                    self.handle_category_menu()
                elif choice == 2:
                    self.handle_subcategory_menu()
                elif choice == 3:
                    self.handle_operation_menu()
                elif choice == 4:
                    self.show_reports()
                elif choice == 5:
                    self.formatter.print_success("Выход из приложения...")
                    break
                else:
                    self.formatter.print_error("Неверный выбор!")
        except KeyboardInterrupt:
            self.formatter.print_warning("\nПриложение завершено пользователем")
        except Exception as e:
            self.formatter.print_error(f"Критическая ошибка: {e}")
        finally:
            self.db.disconnect()


def create_tables(db_manager: DatabaseManager):
    """Создание таблиц в базе данных"""
    db_manager.connect()

    try:
        # Таблица категорий
        db_manager.execute_query("""
                                 CREATE TABLE IF NOT EXISTS categories
                                 (
                                     id
                                     TEXT
                                     PRIMARY
                                     KEY,
                                     name
                                     TEXT
                                     NOT
                                     NULL,
                                     type
                                     TEXT
                                     NOT
                                     NULL
                                     CHECK (
                                     type
                                     IN
                                 (
                                     'income',
                                     'expense'
                                 ))
                                     )
                                 """)

        # Таблица подкатегорий
        db_manager.execute_query("""
                                 CREATE TABLE IF NOT EXISTS subcategories
                                 (
                                     id
                                     TEXT
                                     PRIMARY
                                     KEY,
                                     category_id
                                     TEXT
                                     NOT
                                     NULL,
                                     name
                                     TEXT
                                     NOT
                                     NULL,
                                     FOREIGN
                                     KEY
                                 (
                                     category_id
                                 ) REFERENCES categories
                                 (
                                     id
                                 ) ON DELETE CASCADE
                                     )
                                 """)

        # Таблица операций
        db_manager.execute_query("""
                                 CREATE TABLE IF NOT EXISTS operations
                                 (
                                     id
                                     TEXT
                                     PRIMARY
                                     KEY,
                                     type
                                     TEXT
                                     NOT
                                     NULL
                                     CHECK (
                                     type
                                     IN
                                 (
                                     'income',
                                     'expense'
                                 )),
                                     category_id TEXT NOT NULL,
                                     subcategory_id TEXT,
                                     amount REAL NOT NULL,
                                     date DATETIME NOT NULL,
                                     description TEXT,
                                     FOREIGN KEY
                                 (
                                     category_id
                                 ) REFERENCES categories
                                 (
                                     id
                                 ),
                                     FOREIGN KEY
                                 (
                                     subcategory_id
                                 ) REFERENCES subcategories
                                 (
                                     id
                                 ) ON DELETE SET NULL
                                     )
                                 """)

        # Добавляем индексы для ускорения поиска
        db_manager.execute_query("CREATE INDEX IF NOT EXISTS idx_operations_date ON operations(date)")
        db_manager.execute_query("CREATE INDEX IF NOT EXISTS idx_operations_type ON operations(type)")
        db_manager.execute_query("CREATE INDEX IF NOT EXISTS idx_subcategories_category ON subcategories(category_id)")

        print("✅ Таблицы успешно созданы!")

    except sqlite3.Error as e:
        print(f"❌ Ошибка при создании таблиц: {e}")
    finally:
        db_manager.disconnect()


def create_default_categories(db_manager: DatabaseManager):
    """Создание стандартных категорий и подкатегорий"""
    try:
        db_manager.connect()

        # Проверяем, есть ли уже категории
        result = db_manager.fetch_one("SELECT COUNT(*) FROM categories")
        if result and result[0] > 0:
            print("ℹ️  Категории уже существуют, стандартные не добавляются")
            return

        print("➕ Создаем стандартные категории и подкатегории...")

        # Стандартные категории доходов
        income_categories = [
            ("Зарплата", "income"),
            ("Инвестиции_Д", "income"),
            ("Случайные доход", "income"),
            ("Социальные выплаты", "income"),
            ("Прочие доходы", "income")
        ]

        # Стандартные категории расходов
        expense_categories = [
            ("Жильё", "expense"),
            ("Коммунальные услуги", "expense"),
            ("Связь и интернет", "expense"),
            ("Транспорт", "expense"),
            ("Продукты питания", "expense"),
            ("Налоги и сборы", "expense"),
            ("Кредиты и долги", "expense"),
            ("Одежда и обувь", "expense"),
            ("Личные расходы", "expense"),
            ("Здоровье", "expense"),
            ("Образование", "expense"),
            ("Дети", "expense"),
            ("Дом и быт", "expense"),
            ("Питомцы", "expense"),
            ("Развлечения", "expense"),
            ("Хобби", "expense"),
            ("Спорт и фитнес", "expense"),
            ("Подписки и сервисы", "expense"),
            ("Путешествия и отдых", "expense"),
            ("Инвестиции", "expense"),
            ("Сбережения", "expense"),
            ("Страхование", "expense"),
            ("Благотворительность", "expense"),
            ("Подарки", "expense"),
            ("Прочие расходы", "expense")
        ]

        # Словарь для хранения ID категорий (название -> id)
        category_ids = {}

        # Создаем все категории
        all_categories = income_categories + expense_categories
        for name, type_ in all_categories:
            category_id = str(uuid.uuid4())
            query = "INSERT INTO categories (id, name, type) VALUES (?, ?, ?)"
            db_manager.execute_query(query, (category_id, name, type_))
            category_ids[name] = category_id

        # Стандартные подкатегории для некоторых категорий
        default_subcategories = {
            "Зарплата": ["Зарплата", "Фриланс"],
            "Инвестиции_Д": ["Дивиденды по акциям", "Процентный доход"],
            "Случайные доход": ["Подарки", "Долг", "Продажа"],
            "Социальные выплаты": ["Пенсия", "Стипендия"],
            "Прочие доходы": ["Кэшбэк", "Возврат билетов", "Компенсация"],
            "Жильё": ["Арендная плата", "Ипотека", "Ремонт и обслуживание"],
            "Коммунальные услуги": ["Электричество", "Водоснабжение и водоотведение", "Газоснабжение", "Отопление", "Вывоз мусора", "Капитальный ремонт", "Домофон и консьерж", "Прочие коммунальные платежи"],
            "Связь и интернет": ["Мобильная связь", "Домашний интернет", "ТВ"],
            "Транспорт": ["Общественный транспорт", "Такси и каршеринг", "Бензин/зарядка для ЭВ", "Техническое обслуживание и ремонт авто", "Страхование (ОСАГО, КАСКО)", "Штрафы и парковка", "Налог на транспорт", "Мойка"],
            "Продукты питания": ["Бакалея", "Молочные продукты", "Яйца", "Мясо, птица, рыба", "Овощи и фрукты", "Хлеб и выпечка", "Напитки", "Сладости и снеки", "Готовые блюда"],
            "Налоги и сборы": ["Налог на имущество", "Земельный налог", "Прочие налоги и госпошлины"],
            "Кредиты и долги": ["Потребительские кредиты", "Кредитные карты", "Автокредит", "Займы"],
            "Одежда и обувь": ["Верхняя одежда", "Повседневная одежда", "Обувь", "Нижнее бельё и носки", "Аксессуары", "Ремонт и химчистка"],
            "Личные расходы": ["Парикмахерская", "Барбершоп", "Маникюр", "Косметика", "Парфюмерия", "Средства гигиены", "Канцелярия"],
            "Здоровье": ["Поликлиника, анализы, лечение", "Стоматология", "Лекарства и витамины", "Оптика", "Медосмотры и справки", "ДМС"],
            "Образование": ["Курсы, тренинги, репетиторы", "Книги и учебные материалы", "Конференции и семинары"],
            "Дом и быт": ["Бытовая химия и чистящие средства", "Кухонная утварь и посуда", "Текстиль", "Предметы интерьера и декор", "Хозтовары"],
            "Питомцы": ["Корм и лакомства", "Ветеринарные услуги и лекарства", "Аксессуары, игрушки, наполнитель", "Груминг и передержка"],
            "Развлечения": ["Кино", "Театры / Концерты", "Клубы / Бары", "Выставки / Музеи", "Развлекательные парки", "Доставка еды", "Рестораны"],
            "Хобби": ["Рукоделие / Творчество", "Коллекционирование", "Садоводство / Огород", "Фотография", "Музыка (инструменты, ноты)"],
            "Спорт и фитнес": ["Абонемент в зал / Бассейн", "Тренер / Занятия", "Спортивная экипировка", "Участие в соревнованиях", "Спортивное питание"],
            "Подписки и сервисы": ["Видеостриминги (Netflix)", "Музыка (Spotify, Яндекс)", "Игровые подписки (PS Plus)", "Программное обеспечение", "Облачные хранилища"],
            "Путешествия и отдых": ["Авиа / ЖД билеты", "Отели / Аренда жилья", "Питание в поездках", "Экскурсии / Гиды", "Аренда авто / Такси", "Сувениры"],
            "Инвестиции": ["Акции / ETF", "Облигации", "ИИС / Брокерский счёт", "Криптовалюты", "Вклады / Депозиты", "Недвижимость (взнос)"],
            "Сбережения": ["Подушка безопасности", "Накопления на авто", "Накопления на ремонт", "Накопления на отпуск", "Пенсионные накопления"],
            "Страхование": ["Страхование жизни", "Страхование имущества", "Страхование от НС", "Медицинское страхование"],
            "Благотворительность": ["Пожертвования фондам", "Помощь приютам", "Волонтёрство (расходы)", "Помощь близким", "Церковь / Храм"],
            "Подарки": ["Дни рождения", "Новый год", "8 марта", "Свадьбы", "Юбилеи", "Цветы", "Детские подарки"],
            "Прочие расходы": ["Непредвиденные траты", "Комиссии банков", "Утерянные деньги", "Проценты по кредитам", "Штрафы (не авто)"]
        }

        # Создаем подкатегории
        subcategories_created = 0
        for category_name, subcat_names in default_subcategories.items():
            if category_name in category_ids:
                for subcat_name in subcat_names:
                    subcategory_id = str(uuid.uuid4())
                    query = "INSERT INTO subcategories (id, category_id, name) VALUES (?, ?, ?)"
                    db_manager.execute_query(query, (subcategory_id, category_ids[category_name], subcat_name))
                    subcategories_created += 1

        print(f"✅ Создано {len(all_categories)} категорий и {subcategories_created} подкатегорий")

    except sqlite3.Error as e:
        print(f"⚠️  Ошибка при создании стандартных категорий: {e}")
    finally:
        db_manager.disconnect()

def initialize_database():
    """Полная инициализация базы данных"""
    db = DatabaseManager()

    # Создаем таблицы
    create_tables(db)

    # Добавляем стандартные категории
    create_default_categories(db)

    return db


def main():
    """Точка входа в приложение"""
    print("\n" + "═" * 70)
    print(f"{'💰 Приложение личных финансов 💰':^70}")
    print("═" * 70)

    # Создаем таблицы при первом запуске
    db = initialize_database()

    # Запускаем приложение
    app = FinanceApp()
    app.run()


if __name__ == "__main__":
    main()