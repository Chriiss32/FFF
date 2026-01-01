import sqlite3
import uuid
from datetime import datetime
import os
from Category import Category
from ConsoleFormatter import ConsoleFormatter
from DatabaseManager import DatabaseManager
from Operation import Operation
from Subcategory import Subcategory
from Period import Period
from PlanSubcategory import PlanSubcategory


class FinanceApp:
    """Главный класс приложения"""

    def __init__(self):
        self.db = DatabaseManager()
        self.db.connect()
        self.category_manager = Category(self.db)
        self.subcategory_manager = Subcategory(self.db)
        self.operation_manager = Operation(self.db)
        self.period_manager = Period(self.db)
        self.plan_manager = PlanSubcategory(self.db)
        self.formatter = ConsoleFormatter()

    def clear_screen(self):
        """Очистка экрана консоли"""
        os.system('cls' if os.name == 'nt' else 'clear')

    def show_main_menu(self):
        """Отображение главного меню"""
        self.clear_screen()
        self.formatter.print_header("Управление личными финансами")

        self.formatter.print_menu([
            "⚙️  Настройки",
            "💰 Управление операциями",
            "📊 Просмотр отчетов",
            "📅 Планирование бюджета",
            "❌ Выход"
        ])

        choice = self.formatter.get_input("Выберите действие", input_type=int,
                                          validation_func=lambda x: 1 <= x <= 5)
        return choice

    def handle_settings_menu(self):
        """Обработка меню настроек"""
        while True:
            self.clear_screen()
            self.formatter.print_header("Настройки")

            self.formatter.print_menu([
                "📁 Управление категориями",
                "📂 Управление подкатегориями",
                "📊 Периоды планирования",
                "🔙 Назад в главное меню"
            ])

            choice = self.formatter.get_input("Выберите действие", input_type=int,
                                              validation_func=lambda x: 1 <= x <= 4)

            if choice == 1:
                self.handle_category_menu()
            elif choice == 2:
                self.handle_subcategory_menu()
            elif choice == 3:
                self.handle_view_periods()
            elif choice == 4:
                break
            else:
                self.formatter.print_error("Неверный выбор!")

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
                "🔙 Назад в настройки"
            ])

            choice = self.formatter.get_input("Выберите действие", input_type=int,
                                              validation_func=lambda x: 1 <= x <= 5)

            if choice == 1:
                self.handle_category_creation()
            elif choice == 2:
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

        self.formatter.print_menu(["📈 Доход", "📉 Расход", "0 - Отмена"], "Тип категории")
        type_choice = self.formatter.get_input("Выберите тип (0 для отмены)", input_type=int,
                                               validation_func=lambda x: 0 <= x <= 2)
        if type_choice is None:
            return
        elif type_choice == 0:
            self.formatter.print_info("Создание категории отменено.")
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
            "Только расходы",
            "0 - Назад"
        ], "Фильтр")

        filter_choice = self.formatter.get_input("Выберите фильтр (0 для отмены)", input_type=int,
                                                 validation_func=lambda x: 0 <= x <= 3)
        if filter_choice is None:
            return
        elif filter_choice == 0:
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
        print("2. 0 - для отмены")

        identifier = self.formatter.get_input("Введите ID для обновления (0 для отмены)", required=True)
        if identifier == '0':
            self.formatter.print_info("Обновление категории отменено.")

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
        print("2. 0 - для отмены")

        identifier = self.formatter.get_input("Введите ID для удаления (0 для отмены)", required=True)
        if identifier == '0':
            self.formatter.print_info("Удаление категории отменено.")
            input("\nНажмиte Enter для продолжения...")
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
                "🔙 Назад в настройки"
            ])

            choice = self.formatter.get_input("Выберите действие", input_type=int,
                                              validation_func=lambda x: 1 <= x <= 5)

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
        print("2. 0 - для отмены")

        category_identifier = self.formatter.get_input("Введите ID категории (0 для отмены)", required=True)
        if category_identifier == '0':
            self.formatter.print_info("Создание подкатегории отменено.")
            return

        name = self.formatter.get_input("Название подкатегории (0 для отмены)", required=True)
        if name == '0':
            self.formatter.print_info("Создание подкатегории отменено.")
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

            filter_choice = input("\nВведите ID категории для фильтрации (0 для отмены или Enter для всех): ").strip()
            if filter_choice == '0':
                return
            elif filter_choice:
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
        print("3. 0 - для отмены")

        identifier = self.formatter.get_input("Введите ID или имя подкатегории для обновления (0 для отмены)",
                                              required=True)
        if identifier == '0':
            self.formatter.print_info("Обновление подкатегории отменено.")
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
        print("3. 0 - для отмены")

        identifier = self.formatter.get_input("Введите ID или имя подкатегории для удаления (0 для отмены)",
                                              required=True)
        if identifier == '0':
            self.formatter.print_info("Удаление подкатегории отменено.")

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
        self.formatter.print_menu(["📈 Доход", "📉 Расход", "0 - Отмена"], "Тип операции")
        type_choice = self.formatter.get_input("Выберите тип (0 для отмены)", input_type=int,
                                               validation_func=lambda x: 0 <= x <= 2)
        if type_choice is None:
            return
        elif type_choice == 0:
            self.formatter.print_info("Создание операции отменено.")
            return

        type_ = 'income' if type_choice == 1 else 'expense'

        # Выбор категории
        categories = self.category_manager.get_all_categories(type_)
        if not categories:
            self.formatter.print_error(f"Сначала создайте категории типа '{type_}'!")
            input("\nНажмиte Enter для продолжения...")
            return

        self.category_manager.show_categories_table(type_, show_full_ids=True)
        category_identifier = self.formatter.get_input("Введите ID категории (0 для отмены)", required=True)
        if category_identifier == '0':
            self.formatter.print_info("Создание операции отменено.")
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

        subcategory_input = input("Введите ID или имя подкатегории (0 для отмены или Enter чтобы пропустить): ").strip()
        if subcategory_input == '0':
            self.formatter.print_info("Создание операции отменено.")
            return
        elif subcategory_input:
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
        amount = self.formatter.get_input("Сумма (0 для отмены)", input_type=float,
                                          validation_func=lambda x: x >= 0)
        if amount is None:
            return
        elif amount == 0:
            self.formatter.print_info("Создание операции отменено.")
            return

        # Ввод даты
        today = datetime.now().strftime("%Y-%m-%d")
        date = self.formatter.get_input(f"Дата (ГГГГ-ММ-ДД) [{today}] (0 для отмены)", default=today,
                                        validation_func=lambda x: x == '0' or self.operation_manager.validate_date(x))
        if date is None:
            return
        elif date == '0':
            self.formatter.print_info("Создание операции отменено.")
            input("\nНажмиte Enter для продолжения...")
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
            "По датам",
            "0 - Назад"
        ], "Фильтр")

        filter_choice = self.formatter.get_input("Выберите фильтр (0 для отмены)", input_type=int,
                                                 validation_func=lambda x: 0 <= x <= 4)
        if filter_choice is None:
            return
        elif filter_choice == 0:
            return

        type_ = None
        start_date = None
        end_date = None

        if filter_choice == 2:
            type_ = 'income'
        elif filter_choice == 3:
            type_ = 'expense'
        elif filter_choice == 4:
            start_date = self.formatter.get_input("Дата начала (ГГГГ-ММ-ДД) (0 для отмены)",
                                                  validation_func=lambda
                                                      x: x == '0' or self.operation_manager.validate_date(x))
            if start_date == '0':
                return
            if start_date is None:
                return

            end_date = self.formatter.get_input("Дата окончания (ГГГГ-ММ-ДД) (0 для отмены)",
                                                validation_func=lambda
                                                    x: x == '0' or self.operation_manager.validate_date(x))
            if end_date == '0':
                return
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

        input("\nНажмиte Enter для продолжения...")

    def handle_operation_search(self):
        """Обработка поиска операции по ID"""
        self.clear_screen()
        self.formatter.print_header("Поиск операции")

        operation_id = self.formatter.get_input("Введите ID операции (0 для отмены)", required=True)
        if operation_id == '0':
            self.formatter.print_info("Поиск операции отменен.")
            input("\nНажмиte Enter для продолжения...")
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

        input("\nНажмиte Enter для продолжения...")

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

        operation_id = self.formatter.get_input("Введите ID операции для обновления (0 для отмены)", required=True)
        if operation_id == '0':
            self.formatter.print_info("Обновление операции отменено.")
            input("\nНажмиte Enter для продолжения...")
            return

        self.operation_manager.update_operation(operation_id)

        input("\nНажмиte Enter для продолжения...")

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

        operation_id = self.formatter.get_input("Введите ID операции для удаления (0 для отмены)", required=True)
        if operation_id == '0':
            self.formatter.print_info("Удаление операции отменено.")
            input("\nНажмиte Enter для продолжения...")
            return

        self.operation_manager.delete_operation(operation_id)

        input("\nНажмиte Enter для продолжения...")

    # def show_reports(self):
    #     """Отображение отчетов"""
    #     self.clear_screen()
    #     self.formatter.print_header("Финансовые отчеты")
    #
    #     # Получаем все операции
    #     operations = self.operation_manager.get_all_operations()
    #
    #     if not operations:
    #         self.formatter.print_info("Нет данных для отчетов!")
    #         return
    #
    #     # Общая статистика
    #     total_income = sum(op['amount'] for op in operations if op['type'] == 'income')
    #     total_expense = sum(op['amount'] for op in operations if op['type'] == 'expense')
    #     balance = total_income - total_expense
    #
    #     self.formatter.print_header("Общая статистика")
    #
    #     headers = ["Показатель", "Значение"]
    #     rows = [
    #         ["Всего операций", len(operations)],
    #         ["Операций доходов", sum(1 for op in operations if op['type'] == 'income')],
    #         ["Операций расходов", sum(1 for op in operations if op['type'] == 'expense')],
    #         ["Общий доход", f"{total_income:.2f}"],
    #         ["Общий расход", f"{total_expense:.2f}"],
    #         ["Баланс", f"{balance:.2f}"]
    #     ]
    #
    #     self.formatter.print_table(headers, rows)
    #
    #     # Расходы по категориям
    #     expense_by_category = {}
    #     for op in operations:
    #         if op['type'] == 'expense':
    #             cat_name = op['category_name']
    #             expense_by_category[cat_name] = expense_by_category.get(cat_name, 0) + op['amount']
    #
    #     if expense_by_category:
    #         self.formatter.print_header("Расходы по категориям")
    #
    #         headers = ["Категория", "Сумма", "Доля"]
    #         rows = []
    #         for category, amount in sorted(expense_by_category.items(), key=lambda x: x[1], reverse=True):
    #             percentage = (amount / total_expense * 100) if total_expense > 0 else 0
    #             rows.append([category, f"{amount:.2f}", f"{percentage:.1f}%"])
    #
    #         self.formatter.print_table(headers, rows)
    #
    #     # Доходы по категориям
    #     income_by_category = {}
    #     for op in operations:
    #         if op['type'] == 'income':
    #             cat_name = op['category_name']
    #             income_by_category[cat_name] = income_by_category.get(cat_name, 0) + op['amount']
    #
    #     if income_by_category:
    #         self.formatter.print_header("Доходы по категориям")
    #
    #         headers = ["Категория", "Сумма", "Доля"]
    #         rows = []
    #         for category, amount in sorted(income_by_category.items(), key=lambda x: x[1], reverse=True):
    #             percentage = (amount / total_income * 100) if total_income > 0 else 0
    #             rows.append([category, f"{amount:.2f}", f"{percentage:.1f}%"])
    #
    #         self.formatter.print_table(headers, rows)
    #
    #     # Ежемесячная статистика
    #     monthly_stats = {}
    #     for op in operations:
    #         month = op['date'][:7]  # ГГГГ-ММ
    #         if month not in monthly_stats:
    #             monthly_stats[month] = {'income': 0, 'expense': 0}
    #
    #         if op['type'] == 'income':
    #             monthly_stats[month]['income'] += op['amount']
    #         else:
    #             monthly_stats[month]['expense'] += op['amount']
    #
    #     if monthly_stats:
    #         self.formatter.print_header("Ежемесячная статистика")
    #
    #         headers = ["Месяц", "Доход", "Расход", "Баланс"]
    #         rows = []
    #         for month in sorted(monthly_stats.keys(), reverse=True):
    #             stats = monthly_stats[month]
    #             balance = stats['income'] - stats['expense']
    #             rows.append([
    #                 month,
    #                 f"{stats['income']:.2f}",
    #                 f"{stats['expense']:.2f}",
    #                 f"{balance:.2f}"
    #             ])
    #
    #         self.formatter.print_table(headers, rows)

    def handle_budget_planning_menu(self):
        """Обработка меню планирования бюджета"""
        while True:
            self.clear_screen()
            self.formatter.print_header("Планирование бюджета")

            self.formatter.print_menu([
                "📊 Просмотреть и изменить бюджеты",
                "🔙 Назад в главное меню"
            ])

            choice = self.formatter.get_input("Выберите действие", input_type=int,
                                              validation_func=lambda x: 1 <= x <= 2)

            if choice == 1:
                self.handle_view_and_edit_budgets()
            elif choice == 2:
                break
            else:
                self.formatter.print_error("Неверный выбор!")

    def handle_view_and_edit_budgets(self):
        """Просмотр и редактирование бюджетов"""
        while True:
            self.clear_screen()
            self.formatter.print_header("Просмотр и редактирование бюджетов")

            # Показываем все бюджеты в виде полной таблицы
            plans = self.plan_manager.get_all_plans()

            if not plans:
                self.formatter.print_info(
                    "Бюджеты не найдены. Они будут созданы автоматически при добавлении подкатегорий.")
                input("\nНажмите Enter для продолжения...")
                return

            # Отображаем полную таблицу бюджетов
            self.formatter.print_header("Все бюджеты (доходы и расходы)")

            # Создаем таблицу с нужными колонками
            headers = ["№", "Тип", "Категория", "Подкатегория", "Период", "Сумма/период", "Прогноз на год",
                       "Эквив. месяц"]
            rows = []

            # Группируем бюджеты по типу
            income_plans = []
            expense_plans = []

            for plan in plans:
                # Определяем тип бюджета
                budget_type = "📈 Доход" if plan.get('category_type') == 'income' else "📉 Расход"
                plan['budget_type'] = budget_type

                # Рассчитываем эквивалентную месячную сумму
                period_count = plan.get('period_count', 1)
                if period_count > 0:
                    monthly_equivalent = plan['planned_amount'] * (12 / period_count)  # Приводим к месяцу
                else:
                    monthly_equivalent = 0
                plan['monthly_equivalent'] = monthly_equivalent

                if plan.get('category_type') == 'income':
                    income_plans.append(plan)
                else:
                    expense_plans.append(plan)

            # Показываем сначала доходы, потом расходы
            all_plans = income_plans + expense_plans

            for i, plan in enumerate(all_plans, 1):
                rows.append([
                    str(i),
                    plan['budget_type'],
                    plan['category_name'],
                    plan['subcategory_name'],
                    plan['period_name'],
                    f"{plan['planned_amount']:.2f}",
                    f"{plan['year_forecast']:.2f}",
                    f"{plan['monthly_equivalent']:.2f}"
                ])

            self.formatter.print_table(headers, rows)

            # Показываем статистику - ПЕРЕСЧИТЫВАЕМ В МЕСЯЦ
            total_income_monthly = sum(plan['monthly_equivalent'] for plan in income_plans)
            total_income_forecast = sum(plan['year_forecast'] for plan in income_plans)
            total_expense_monthly = sum(plan['monthly_equivalent'] for plan in expense_plans)
            total_expense_forecast = sum(plan['year_forecast'] for plan in expense_plans)

            print(f"\n📊 Статистика (все суммы приведены к месячному эквиваленту):")
            print(f"   • Всего бюджетов: {len(all_plans)}")
            print(f"     - 📈 Доходы: {len(income_plans)} бюджетов")
            print(f"     - 📉 Расходы: {len(expense_plans)} бюджетов")
            print(f"   • Общая сумма в месяц:")
            print(f"     - 📈 Доходы: {total_income_monthly:.2f}")
            print(f"     - 📉 Расходы: {total_expense_monthly:.2f}")
            print(f"   • Общий прогноз на год:")
            print(f"     - 📈 Доходы: {total_income_forecast:.2f}")
            print(f"     - 📉 Расходы: {total_expense_forecast:.2f}")

            # Рассчитываем прогнозируемые показатели
            monthly_balance = total_income_monthly - total_expense_monthly
            annual_balance = total_income_forecast - total_expense_forecast

            print(f"   • Прогнозируемый баланс:")
            print(f"     - В месяц: {monthly_balance:.2f}")
            print(f"     - В год: {annual_balance:.2f}")

            # Показываем соотношение доходов и расходов
            if total_income_monthly > 0:
                expense_ratio = (total_expense_monthly / total_income_monthly) * 100
                print(f"   • Расходы составляют {expense_ratio:.1f}% от доходов")

                if expense_ratio > 100:
                    print(f"   ⚠️  ВНИМАНИЕ: Расходы превышают доходы на {expense_ratio - 100:.1f}%!")
                elif expense_ratio > 80:
                    print(f"   ⚠️  Внимание: Высокий уровень расходов ({expense_ratio:.1f}% от доходов)")
                else:
                    print(f"   ✅ Хороший уровень: расходы {expense_ratio:.1f}% от доходов")

            print("\n" + "=" * 80)
            print("Выберите действие:")
            print("1. Редактировать бюджет по номеру")
            print("2. Показать бюджеты с полными ID")
            print("3. Показать только доходы")
            print("4. Показать только расходы")
            print("5. Экспорт статистики")
            print("0. Назад в меню планирования")

            try:
                choice = int(input("\nВаш выбор: ").strip())

                if choice == 0:
                    return
                elif choice == 1:
                    self.handle_edit_budget_by_number(all_plans)
                elif choice == 2:
                    self.show_budgets_with_full_ids()
                elif choice == 3:
                    self.show_only_income_budgets()
                elif choice == 4:
                    self.show_only_expense_budgets()
                elif choice == 5:
                    self.export_budget_statistics(all_plans, income_plans, expense_plans)
                else:
                    self.formatter.print_error("Неверный выбор!")
                    input("\nНажмите Enter для продолжения...")

            except ValueError:
                self.formatter.print_error("Неверный формат ввода!")
                input("\nНажмите Enter для продолжения...")

    def handle_edit_budget_by_number(self, plans):
        """Редактирование бюджета по номеру из таблицы"""
        try:
            plan_number = int(input("\nВведите номер бюджета для редактирования (0 для отмены): ").strip())

            if plan_number == 0:
                return

            if plan_number < 1 or plan_number > len(plans):
                self.formatter.print_error("Неверный номер!")
                input("\nНажмите Enter для продолжения...")
                return

            selected_plan = plans[plan_number - 1]
            self.edit_single_budget(selected_plan)

        except ValueError:
            self.formatter.print_error("Неверный формат номера!")
            input("\nНажмите Enter для продолжения...")

    def edit_single_budget(self, plan):
        """Редактирование одного бюджета"""
        self.clear_screen()
        self.formatter.print_header(f"Редактирование бюджета: {plan['subcategory_name']}")

        # Показываем текущие настройки
        print(f"📁 Категория: {plan['category_name']}")
        print(f"📂 Подкатегория: {plan['subcategory_name']}")
        print(f"\n📊 Текущие настройки бюджета:")
        print(f"   • Период: {plan['period_name']} (ID: {plan['period_id']})")
        print(f"   • Сумма за период: {plan['planned_amount']:.2f}")
        print(f"   • Прогноз на год: {plan['year_forecast']:.2f}")
        print(f"   • Коэффициент периода: {plan['period_count']}")

        print("\n" + "=" * 60)

        # Показываем доступные периоды
        periods = self.period_manager.get_all_periods()
        if periods:
            print("\n📅 Доступные периоды:")
            for period in periods:
                print(f"   • ID: {period['id']}| {period['name']:10} | Коэффициент: {period['period_count']}")

        # Запрашиваем изменение периода
        print(f"\nВведите ID нового периода (текущий: {plan['period_id'][:8]}...)")
        print("Или нажмите Enter, чтобы оставить текущий период")

        new_period_id = input("\nID нового периода: ").strip()

        if new_period_id:
            # Проверяем, существует ли период
            period_obj = self.period_manager.get_period_by_id(new_period_id)
            if not period_obj:
                self.formatter.print_error("Период не найден!")
                input("\nНажмите Enter для продолжения...")
                return
            period_count = period_obj['period_count']
        else:
            new_period_id = plan['period_id']
            period_count = plan['period_count']

        # Запрашиваем новую сумму
        print(f"\nВведите новую сумму для периода (текущая: {plan['planned_amount']:.2f})")
        print("Или нажмите Enter, чтобы оставить текущую сумму")

        new_amount_input = input("\nНовая сумма: ").strip()

        if new_amount_input:
            try:
                new_amount = float(new_amount_input)
                if new_amount < 0:
                    self.formatter.print_error("Сумма не может быть отрицательной!")
                    input("\nНажмите Enter для продолжения...")
                    return
            except ValueError:
                self.formatter.print_error("Неверный формат суммы!")
                input("\nНажмите Enter для продолжения...")
                return
        else:
            new_amount = plan['planned_amount']

        # Рассчитываем годовой прогноз
        new_year_forecast = new_amount * period_count

        # Обновляем бюджет, если что-то изменилось
        if new_period_id != plan['period_id'] or new_amount != plan['planned_amount']:
            # Обновляем бюджет
            success = self.plan_manager.update_plan(
                plan['id'],
                new_amount,
                new_period_id,
                new_year_forecast
            )

            if success:
                self.formatter.print_success("Бюджет успешно обновлен!")

                # Показываем обновленные данные
                updated_plan = self.plan_manager.get_budget_by_subcategory(plan['subcategory_id'])
                if updated_plan:
                    print(f"\n✅ Обновленные настройки:")
                    print(f"   • Период: {updated_plan['period_name']}")
                    print(f"   • Сумма за период: {updated_plan['planned_amount']:.2f}")
                    print(f"   • Прогноз на год: {updated_plan['year_forecast']:.2f}")
                    print(f"   • Коэффициент периода: {updated_plan['period_count']}")
            else:
                self.formatter.print_error("Ошибка при обновлении бюджета!")
        else:
            self.formatter.print_info("Изменений не внесено.")

        input("\nНажмите Enter для продолжения...")

    def show_budgets_with_full_ids(self):
        """Показать бюджеты с полными ID"""
        self.clear_screen()
        self.formatter.print_header("Бюджеты (полные ID)")

        plans = self.plan_manager.get_all_plans()

        if not plans:
            self.formatter.print_info("Бюджеты не найдены.")
            input("\nНажмите Enter для продолжения...")
            return

        headers = ["№", "ID", "Категория", "Подкатегория", "Период", "Сумма", "Прогноз на год"]
        rows = []

        for i, plan in enumerate(plans, 1):
            rows.append([
                str(i),
                plan['id'],  # Полный ID
                plan['category_name'],
                plan['subcategory_name'],
                plan['period_name'],
                f"{plan['planned_amount']:.2f}",
                f"{plan['year_forecast']:.2f}"
            ])

        self.formatter.print_table(headers, rows)
        self.formatter.print_info("Полные ID показаны. Вы можете скопировать их для использования в других функциях.")

        input("\nНажмите Enter для продолжения...")

    def handle_view_periods(self):
        """Просмотр периодов планирования"""
        self.clear_screen()
        self.formatter.print_header("Периоды планирования")

        periods = self.period_manager.get_all_periods()
        if periods:
            self.period_manager.show_periods_table()
        else:
            self.formatter.print_info("Периоды не найдены. Будут созданы стандартные периоды.")

            # Создаем стандартные периоды
            standard_periods = [
                ("День", 365),
                ("Неделя", 52),
                ("Месяц", 12),
                ("Квартал", 4),
                ("Полугодие", 2),
                ("Год", 1)
            ]

            for name, count in standard_periods:
                self.period_manager.create_period(name, count)

            # Показываем созданные периоды
            periods = self.period_manager.get_all_periods()
            self.period_manager.show_periods_table()

    def run(self):
        """Запуск приложения"""
        try:
            while True:
                choice = self.show_main_menu()

                if choice == 1:
                    self.handle_settings_menu()
                elif choice == 2:
                    self.handle_operation_menu()
                elif choice == 3:
                    self.show_reports()
                elif choice == 4:
                    self.handle_budget_planning_menu()
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

        # Таблица периодов планирования
        db_manager.execute_query("""
                                 CREATE TABLE IF NOT EXISTS periods
                                 (
                                     id
                                     TEXT
                                     PRIMARY
                                     KEY,
                                     name
                                     TEXT
                                     NOT
                                     NULL
                                     UNIQUE,
                                     period_count
                                     INTEGER
                                     NOT
                                     NULL
                                 )
                                 """)

        # Таблица планов подкатегорий (ИЗМЕНЕНО: limit -> planned_amount)
        db_manager.execute_query("""
                                 CREATE TABLE IF NOT EXISTS plan_subcategories
                                 (
                                     id
                                     TEXT
                                     PRIMARY
                                     KEY,
                                     category_id
                                     TEXT
                                     NOT
                                     NULL,
                                     subcategory_id
                                     TEXT
                                     NOT
                                     NULL,
                                     period_id
                                     TEXT
                                     NOT
                                     NULL,
                                     planned_amount
                                     REAL
                                     NOT
                                     NULL,
                                     year_forecast
                                     REAL
                                     NOT
                                     NULL,
                                     FOREIGN
                                     KEY
                                 (
                                     category_id
                                 ) REFERENCES categories
                                 (
                                     id
                                 ) ON DELETE CASCADE,
                                     FOREIGN KEY
                                 (
                                     subcategory_id
                                 ) REFERENCES subcategories
                                 (
                                     id
                                 )
                                   ON DELETE CASCADE,
                                     FOREIGN KEY
                                 (
                                     period_id
                                 ) REFERENCES periods
                                 (
                                     id
                                 )
                                   ON DELETE CASCADE,
                                     UNIQUE
                                 (
                                     subcategory_id,
                                     period_id
                                 )
                                     )
                                 """)

        # Таблица истории изменений сумм планов (ИЗМЕНЕНО: old_limit/new_limit -> old_amount/new_amount)
        db_manager.execute_query("""
                                 CREATE TABLE IF NOT EXISTS plan_subcategory_history
                                 (
                                     id
                                     TEXT
                                     PRIMARY
                                     KEY,
                                     plan_subcategory_id
                                     TEXT
                                     NOT
                                     NULL,
                                     changed_at
                                     DATETIME
                                     NOT
                                     NULL,
                                     old_amount
                                     REAL
                                     NOT
                                     NULL,
                                     new_amount
                                     REAL
                                     NOT
                                     NULL,
                                     FOREIGN
                                     KEY
                                 (
                                     plan_subcategory_id
                                 ) REFERENCES plan_subcategories
                                 (
                                     id
                                 ) ON DELETE CASCADE
                                     )
                                 """)

        # Добавляем индексы для ускорения поиска
        db_manager.execute_query("CREATE INDEX IF NOT EXISTS idx_operations_date ON operations(date)")
        db_manager.execute_query("CREATE INDEX IF NOT EXISTS idx_operations_type ON operations(type)")
        db_manager.execute_query("CREATE INDEX IF NOT EXISTS idx_subcategories_category ON subcategories(category_id)")
        db_manager.execute_query(
            "CREATE INDEX IF NOT EXISTS idx_plan_subcategory_subcategory ON plan_subcategories(subcategory_id)")
        db_manager.execute_query(
            "CREATE INDEX IF NOT EXISTS idx_plan_subcategory_period ON plan_subcategories(period_id)")
        db_manager.execute_query(
            "CREATE INDEX IF NOT EXISTS idx_plan_history_plan ON plan_subcategory_history(plan_subcategory_id)")

        print("✅ Таблицы успешно созданы!")

    except sqlite3.Error as e:
        print(f"❌ Ошибка при создании таблиц: {e}")
    finally:
        db_manager.disconnect()


def create_default(db_manager: DatabaseManager):
    """Создание стандартных категорий и подкатегорий с автоматическим созданием бюджетов"""
    try:
        db_manager.connect()

        # 1. Сначала создаем периоды, если их нет
        result = db_manager.fetch_one("SELECT COUNT(*) FROM periods")
        if result and result[0] == 0:
            print("➕ Создаем стандартные периоды планирования...")

            standard_periods = [
                ("День", 365),
                ("Неделя", 52),
                ("Месяц", 12),
                ("Квартал", 4),
                ("Полугодие", 2),
                ("Год", 1)
            ]

            for name, count in standard_periods:
                period_id = str(uuid.uuid4())
                query = "INSERT INTO periods (id, name, period_count) VALUES (?, ?, ?)"
                db_manager.execute_query(query, (period_id, name, count))

            print(f"✅ Создано {len(standard_periods)} стандартных периодов")

        # 2. Проверяем, есть ли уже категории
        result = db_manager.fetch_one("SELECT COUNT(*) FROM categories")

        if result and result[0] > 0:
            print("ℹ️  Категории уже существуют, стандартные не добавляются")

            # Проверяем и создаем бюджеты для существующих подкатегорий (ВСЕХ, не только расходов)
            print("💰 Проверяем бюджеты для существующих подкатегорий...")
            create_missing_budgets(db_manager)

        else:
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
                "Коммунальные услуги": ["Электричество", "Водоснабжение и водоотведение", "Газоснабжение", "Отопление",
                                        "Вывоз мусора", "Капитальный ремонт", "Домофон и консьерж",
                                        "Прочие коммунальные платежи"],
                "Связь и интернет": ["Мобильная связь", "Домашний интернет", "ТВ"],
                "Транспорт": ["Общественный транспорт", "Такси и каршеринг", "Бензин/зарядка для ЭВ",
                              "Техническое обслуживание и ремонт авто", "Страхование (ОСАГО, КАСКО)",
                              "Штрафы и парковка", "Налог на транспорт", "Мойка"],
                "Продукты питания": ["Бакалея", "Молочные продукты", "Яйца", "Мясо, птица, рыба", "Овощи и фрукты",
                                     "Хлеб и выпечка", "Напитки", "Сладости и снеки", "Готовые блюда"],
                "Налоги и сборы": ["Налог на имущество", "Земельный налог", "Прочие налоги и госпошлины"],
                "Кредиты и долги": ["Потребительские кредиты", "Кредитные карты", "Автокредит", "Займы"],
                "Одежда и обувь": ["Верхняя одежда", "Повседневная одежда", "Обувь", "Нижнее бельё и носки",
                                   "Аксессуары", "Ремонт и химчистка"],
                "Личные расходы": ["Парикмахерская", "Барбершоп", "Маникюр", "Косметика", "Парфюмерия",
                                   "Средства гигиены", "Канцелярия"],
                "Здоровье": ["Поликлиника, анализы, лечение", "Стоматология", "Лекарства и витамины", "Оптика",
                             "Медосмотры и справки", "ДМС"],
                "Образование": ["Курсы, тренинги, репетиторы", "Книги и учебные материалы", "Конференции и семинары"],
                "Дом и быт": ["Бытовая химия и чистящие средства", "Кухонная утварь и посуда", "Текстиль",
                              "Предметы интерьера и декор", "Хозтовары"],
                "Питомцы": ["Корм и лакомства", "Ветеринарные услуги и лекарства", "Аксессуары, игрушки, наполнитель",
                            "Груминг и передержка"],
                "Развлечения": ["Кино", "Театры / Концерты", "Клубы / Бары", "Выставки / Музеи",
                                "Развлекательные парки", "Доставка еды", "Рестораны"],
                "Хобби": ["Рукоделие / Творчество", "Коллекционирование", "Садоводство / Огород", "Фотография",
                          "Музыка (инструменты, ноты)"],
                "Спорт и фитнес": ["Абонемент в зал / Бассейн", "Тренер / Занятия", "Спортивная экипировка",
                                   "Участие в соревнованиях", "Спортивное питание"],
                "Подписки и сервисы": ["Видеостриминги (Netflix)", "Музыка (Spotify, Яндекс)",
                                       "Игровые подписки (PS Plus)", "Программное обеспечение", "Облачные хранилища"],
                "Путешествия и отдых": ["Авиа / ЖД билеты", "Отели / Аренда жилья", "Питание в поездках",
                                        "Экскурсии / Гиды", "Аренда авто / Такси", "Сувениры"],
                "Инвестиции": ["Акции / ETF", "Облигации", "ИИС / Брокерский счёт", "Криптовалюты", "Вклады / Депозиты",
                               "Недвижимость (взнос)"],
                "Сбережения": ["Подушка безопасности", "Накопления на авто", "Накопления на ремонт",
                               "Накопления на отпуск", "Пенсионные накопления"],
                "Страхование": ["Страхование жизни", "Страхование имущества", "Страхование от НС",
                                "Медицинское страхование"],
                "Благотворительность": ["Пожертвования фондам", "Помощь приютам", "Волонтёрство (расходы)",
                                        "Помощь близким", "Церковь / Храм"],
                "Подарки": ["Дни рождения", "Новый год", "8 марта", "Свадьбы", "Юбилеи", "Цветы", "Детские подарки"],
                "Прочие расходы": ["Непредвиденные траты", "Комиссии банков", "Утерянные деньги",
                                   "Проценты по кредитам", "Штрафы (не авто)"]
            }

            # Создаем подкатегории и бюджеты
            subcategories_created = 0
            all_subcategories = []  # Сохраняем информацию о ВСЕХ подкатегориях

            for category_name, subcat_names in default_subcategories.items():
                if category_name in category_ids:
                    category_id = category_ids[category_name]

                    # Получаем тип категории
                    type_query = "SELECT type FROM categories WHERE id = ?"
                    type_result = db_manager.fetch_one(type_query, (category_id,))
                    category_type = type_result[0] if type_result else None

                    for subcat_name in subcat_names:
                        subcategory_id = str(uuid.uuid4())
                        query = "INSERT INTO subcategories (id, category_id, name) VALUES (?, ?, ?)"
                        db_manager.execute_query(query, (subcategory_id, category_id, subcat_name))
                        subcategories_created += 1

                        # Сохраняем информацию о ВСЕХ подкатегориях (и доходах, и расходах)
                        all_subcategories.append({
                            'subcategory_id': subcategory_id,
                            'category_id': category_id,
                            'name': subcat_name,
                            'type': category_type  # 'income' или 'expense'
                        })

            print(f"✅ Создано {len(all_categories)} категорий и {subcategories_created} подкатегорий")

            # СОЗДАЕМ БЮДЖЕТЫ ДЛЯ ВСЕХ ПОДКАТЕГОРИЙ (и доходов, и расходов)
            if all_subcategories:
                print("💰 Создаем бюджеты по умолчанию для всех подкатегорий...")

                # Находим период "Месяц" по умолчанию
                period_query = "SELECT id, period_count FROM periods WHERE name = 'Месяц'"
                period_result = db_manager.fetch_one(period_query)

                if not period_result:
                    # Если нет периода "Месяц", берем первый доступный
                    period_query = "SELECT id, period_count FROM periods LIMIT 1"
                    period_result = db_manager.fetch_one(period_query)

                if period_result:
                    period_id = period_result[0]
                    period_count = period_result[1]
                    planned_amount = 0.0  # По умолчанию сумма 0
                    year_forecast = planned_amount * period_count

                    income_budgets = 0
                    expense_budgets = 0

                    for subcat_info in all_subcategories:
                        # Проверяем, нет ли уже бюджета для этой подкатегории
                        check_query = "SELECT id FROM plan_subcategories WHERE subcategory_id = ?"
                        existing = db_manager.fetch_one(check_query, (subcat_info['subcategory_id'],))

                        if not existing:
                            plan_id = str(uuid.uuid4())
                            query = """
                                    INSERT INTO plan_subcategories
                                    (id, category_id, subcategory_id, period_id, planned_amount, year_forecast)
                                    VALUES (?, ?, ?, ?, ?, ?) \
                                    """
                            db_manager.execute_query(query, (
                                plan_id,
                                subcat_info['category_id'],
                                subcat_info['subcategory_id'],
                                period_id,
                                planned_amount,
                                year_forecast
                            ))

                            if subcat_info['type'] == 'income':
                                income_budgets += 1
                            else:
                                expense_budgets += 1

                    print(f"✅ Создано {income_budgets} бюджетов для доходов и {expense_budgets} бюджетов для расходов")
                    print(f"✅ Всего создано {income_budgets + expense_budgets} бюджетов")
                else:
                    print("⚠️  Не удалось создать бюджеты: нет доступных периодов")

    except sqlite3.Error as e:
        print(f"⚠️  Ошибка при создании стандартных категорий: {e}")
    finally:
        db_manager.disconnect()


def create_missing_budgets(db_manager):
    """Создать недостающие бюджеты для ВСЕХ существующих подкатегорий"""
    try:
        # Находим ВСЕ подкатегории без бюджетов (и доходы, и расходы)
        query = """
                SELECT s.id as subcategory_id, s.category_id, s.name as subcategory_name, c.type as category_type
                FROM subcategories s
                         JOIN categories c ON s.category_id = c.id
                         LEFT JOIN plan_subcategories ps ON s.id = ps.subcategory_id
                WHERE ps.id IS NULL \
                """

        subcategories_without_budgets = db_manager.fetch_all(query)

        if not subcategories_without_budgets:
            print("✅ Все подкатегории уже имеют бюджеты")
            return

        print(f"💰 Найдено {len(subcategories_without_budgets)} подкатегорий без бюджетов")

        # Находим период "Месяц" по умолчанию
        period_query = "SELECT id, period_count FROM periods WHERE name = 'Месяц'"
        period_result = db_manager.fetch_one(period_query)

        if not period_result:
            # Если нет периода "Месяц", берем первый доступный
            period_query = "SELECT id, period_count FROM periods LIMIT 1"
            period_result = db_manager.fetch_one(period_query)

        if period_result:
            period_id = period_result[0]
            period_count = period_result[1]
            planned_amount = 0.0
            year_forecast = planned_amount * period_count

            income_budgets = 0
            expense_budgets = 0

            for subcat in subcategories_without_budgets:
                plan_id = str(uuid.uuid4())
                insert_query = """
                               INSERT INTO plan_subcategories
                               (id, category_id, subcategory_id, period_id, planned_amount, year_forecast)
                               VALUES (?, ?, ?, ?, ?, ?) \
                               """
                db_manager.execute_query(insert_query, (
                    plan_id,
                    subcat[1],  # category_id
                    subcat[0],  # subcategory_id
                    period_id,
                    planned_amount,
                    year_forecast
                ))

                if subcat[3] == 'income':  # category_type
                    income_budgets += 1
                else:
                    expense_budgets += 1

            print(f"✅ Создано {income_budgets} бюджетов для доходов и {expense_budgets} бюджетов для расходов")
            print(f"✅ Всего создано {income_budgets + expense_budgets} недостающих бюджетов")
        else:
            print("⚠️  Не удалось создать бюджеты: нет доступных периодов")

    except sqlite3.Error as e:
        print(f"⚠️  Ошибка при создании недостающих бюджетов: {e}")


def initialize_database():
    """Полная инициализация базы данных"""
    db = DatabaseManager()

    # Создаем таблицы
    create_tables(db)

    # Добавляем стандартные категории
    create_default(db)

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