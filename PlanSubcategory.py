import sqlite3
import uuid
from datetime import datetime


class PlanSubcategory:
    """Управление планами подкатегорий"""

    def __init__(self, db_manager):
        self.db = db_manager

    def create_default_budget(self, subcategory_id):
        """Создать бюджет по умолчанию для подкатегории"""
        try:
            # Получаем информацию о подкатегории
            query = """
                    SELECT category_id \
                    FROM subcategories
                    WHERE id = ? \
                    """
            subcategory = self.db.fetch_one(query, (subcategory_id,))

            if not subcategory:
                return None

            category_id = subcategory[0]

            # Находим период "Месяц" по умолчанию
            period_query = "SELECT id FROM periods WHERE name = 'Месяц'"
            period_result = self.db.fetch_one(period_query)

            if not period_result:
                # Если нет периода "Месяц", берем первый доступный
                period_query = "SELECT id FROM periods LIMIT 1"
                period_result = self.db.fetch_one(period_query)

            if not period_result:
                return None

            period_id = period_result[0]
            planned_amount = 0.0  # По умолчанию сумма 0
            year_forecast = planned_amount * 12  # Для месяца годовой прогноз = сумма * 12

            # Создаем бюджет
            plan_id = str(uuid.uuid4())
            query = """
                    INSERT INTO plan_subcategories
                    (id, category_id, subcategory_id, period_id, planned_amount, year_forecast)
                    VALUES (?, ?, ?, ?, ?, ?) \
                    """

            self.db.execute_query(query,
                                  (plan_id, category_id, subcategory_id, period_id, planned_amount, year_forecast))

            return {
                'id': plan_id,
                'category_id': category_id,
                'subcategory_id': subcategory_id,
                'period_id': period_id,
                'planned_amount': planned_amount,
                'year_forecast': year_forecast
            }

        except sqlite3.Error as e:
            print(f"Ошибка при создании бюджета по умолчанию: {e}")
            return None

    def get_budget_by_subcategory(self, subcategory_id):
        """Получить бюджет по ID подкатегории"""
        try:
            query = """
                    SELECT ps.*, \
                           p.name as period_name, \
                           p.period_count,
                           c.name as category_name, \
                           s.name as subcategory_name
                    FROM plan_subcategories ps
                             JOIN periods p ON ps.period_id = p.id
                             JOIN categories c ON ps.category_id = c.id
                             JOIN subcategories s ON ps.subcategory_id = s.id
                    WHERE ps.subcategory_id = ? \
                    """

            result = self.db.fetch_one(query, (subcategory_id,))

            if result:
                return {
                    'id': result[0],
                    'category_id': result[1],
                    'subcategory_id': result[2],
                    'period_id': result[3],
                    'planned_amount': result[4],
                    'year_forecast': result[5],
                    'period_name': result[6],
                    'period_count': result[7],
                    'category_name': result[8],
                    'subcategory_name': result[9]
                }
            return None

        except sqlite3.Error as e:
            print(f"Ошибка при получении бюджета: {e}")
            return None

    def update_plan(self, plan_id, new_amount=None, new_period_id=None, new_year_forecast=None):
        """Обновление плана с записью в историю изменений"""
        try:
            # Получаем текущий план
            query = "SELECT * FROM plan_subcategories WHERE id = ?"
            plan = self.db.fetch_one(query, (plan_id,))

            if not plan:
                print("План не найден!")
                return False

            old_amount = plan[4]
            old_period_id = plan[3]

            # Определяем новые значения
            updated_amount = new_amount if new_amount is not None else old_amount
            updated_period_id = new_period_id if new_period_id is not None else old_period_id

            # Если изменился период, нужно пересчитать годовой прогноз
            if new_period_id is not None:
                # Получаем информацию о новом периоде
                period_query = "SELECT period_count FROM periods WHERE id = ?"
                period_result = self.db.fetch_one(period_query, (new_period_id,))
                if period_result:
                    period_count = period_result[0]
                    updated_year_forecast = updated_amount * period_count
                else:
                    return False
            elif new_year_forecast is not None:
                updated_year_forecast = new_year_forecast
            else:
                # Если не изменился период, но изменилась сумма, пересчитываем прогноз
                if new_amount is not None:
                    period_query = "SELECT period_count FROM periods WHERE id = ?"
                    period_result = self.db.fetch_one(period_query, (old_period_id,))
                    if period_result:
                        period_count = period_result[0]
                        updated_year_forecast = updated_amount * period_count
                    else:
                        return False
                else:
                    updated_year_forecast = plan[5]

            # Обновляем план
            update_query = """
                           UPDATE plan_subcategories
                           SET planned_amount = ?, \
                               period_id      = ?, \
                               year_forecast  = ?
                           WHERE id = ? \
                           """
            self.db.execute_query(update_query, (updated_amount, updated_period_id, updated_year_forecast, plan_id))

            # Записываем в историю, если изменилась сумма
            if new_amount is not None and new_amount != old_amount:
                history_id = str(uuid.uuid4())
                history_query = """
                                INSERT INTO plan_subcategory_history
                                    (id, plan_subcategory_id, changed_at, old_amount, new_amount)
                                VALUES (?, ?, ?, ?, ?) \
                                """
                self.db.execute_query(history_query,
                                      (history_id, plan_id, datetime.now().isoformat(), old_amount, new_amount))

            print("✅ План успешно обновлен!")
            return True

        except sqlite3.Error as e:
            print(f"❌ Ошибка при обновлении плана: {e}")
            return False

    def get_all_plans(self, category_id=None, period_id=None):
        """Получить все планы с фильтрацией"""
        try:
            query = """
                    SELECT ps.*, \
                           p.name as period_name, \
                           p.period_count,
                           c.name as category_name, \
                           s.name as subcategory_name, \
                           c.type as category_type
                    FROM plan_subcategories ps
                             JOIN periods p ON ps.period_id = p.id
                             JOIN categories c ON ps.category_id = c.id
                             JOIN subcategories s ON ps.subcategory_id = s.id \
                    """
            params = []

            if category_id or period_id:
                query += " WHERE "
                conditions = []

                if category_id:
                    conditions.append("ps.category_id = ?")
                    params.append(category_id)

                if period_id:
                    conditions.append("ps.period_id = ?")
                    params.append(period_id)

                query += " AND ".join(conditions)

            query += " ORDER BY c.type DESC, c.name, s.name"  # Сначала доходы, потом расходы

            results = self.db.fetch_all(query, params)

            plans = []
            for row in results:
                plans.append({
                    'id': row[0],
                    'category_id': row[1],
                    'subcategory_id': row[2],
                    'period_id': row[3],
                    'planned_amount': row[4],
                    'year_forecast': row[5],
                    'period_name': row[6],
                    'period_count': row[7],
                    'category_name': row[8],
                    'subcategory_name': row[9],
                    'category_type': row[10]  # 'income' или 'expense'
                })

            return plans

        except sqlite3.Error as e:
            print(f"Ошибка при получении планов: {e}")
            return []

    def create_plan(self, category_id, subcategory_id, period_id, amount):
        """Создание плана бюджета"""
        try:
            # Проверяем, существует ли уже план для этой подкатегории
            check_query = "SELECT id FROM plan_subcategories WHERE subcategory_id = ?"
            existing = self.db.fetch_one(check_query, (subcategory_id,))

            if existing:
                print("⚠️  План для этой подкатегории уже существует!")
                return existing[0]

            # Получаем информацию о периоде
            period_query = "SELECT period_count FROM periods WHERE id = ?"
            period_result = self.db.fetch_one(period_query, (period_id,))

            if not period_result:
                print("❌ Период не найден!")
                return None

            period_count = period_result[0]
            year_forecast = amount * period_count

            # Создаем план
            plan_id = str(uuid.uuid4())
            query = """
                    INSERT INTO plan_subcategories
                    (id, category_id, subcategory_id, period_id, planned_amount, year_forecast)
                    VALUES (?, ?, ?, ?, ?, ?) \
                    """

            self.db.execute_query(query, (plan_id, category_id, subcategory_id, period_id, amount, year_forecast))

            print("✅ План бюджета успешно создан!")
            return plan_id

        except sqlite3.Error as e:
            print(f"❌ Ошибка при создании плана: {e}")
            return None

    def show_plans_table(self, plans=None):
        """Отображение таблицы планов"""
        if plans is None:
            plans = self.get_all_plans()

        if not plans:
            print("📭 Бюджеты не найдены")
            return

        headers = ["№", "ID", "Категория", "Подкатегория", "Период", "Сумма", "Прогноз на год"]
        rows = []

        for i, plan in enumerate(plans, 1):
            rows.append([
                str(i),
                plan['id'][:8] + "...",
                plan['category_name'],
                plan['subcategory_name'],
                plan['period_name'],
                f"{plan['planned_amount']:.2f}",
                f"{plan['year_forecast']:.2f}"
            ])

        from ConsoleFormatter import ConsoleFormatter
        formatter = ConsoleFormatter()
        formatter.print_table(headers, rows)

        # Показываем статистику
        total_amount = sum(plan['planned_amount'] for plan in plans)
        total_forecast = sum(plan['year_forecast'] for plan in plans)
        print(f"\n📊 Статистика:")
        print(f"   • Всего бюджетов: {len(plans)}")
        print(f"   • Общая сумма на периоды: {total_amount:.2f}")
        print(f"   • Общий прогноз на год: {total_forecast:.2f}")