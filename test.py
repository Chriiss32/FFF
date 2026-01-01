import sqlite3
import pandas as pd
import sys
import os

# Добавляем путь к текущей директории
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def get_operations_as_dataframe(db_path='finance.db'):
    """Получение операций в виде DataFrame pandas"""
    try:
        # Подключаемся к базе данных
        conn = sqlite3.connect(db_path)

        # SQL запрос для получения операций с названиями категорий и подкатегорий
        query = """
                SELECT o.id, \
                       o.type, \
                       o.amount, \
                       o.date, \
                       o.description, \
                       c.name as category_name, \
                       c.type as category_type, \
                       s.name as subcategory_name
                FROM operations o
                         LEFT JOIN categories c ON o.category_id = c.id
                         LEFT JOIN subcategories s ON o.subcategory_id = s.id
                ORDER BY o.date DESC \
                """

        # Читаем данные в DataFrame
        df = pd.read_sql_query(query, conn)
        conn.close()

        if df.empty:
            print("❌ Операции не найдены в базе данных")
            return None

        return df

    except sqlite3.Error as e:
        print(f"❌ Ошибка базы данных: {e}")
        return None
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None


def display_operations_with_pandas():
    """Отображение операций с использованием pandas"""
    print("📊 ВЫБОРКА ОПЕРАЦИЙ С ИСПОЛЬЗОВАНИЕМ PANDAS")
    print("=" * 80)

    # Получаем данные
    df = get_operations_as_dataframe()

    if df is None or df.empty:
        return

    print(f"✅ Найдено {len(df)} операций")
    print("\n" + "-" * 80)

    # 1. Отображаем полную таблицу
    print("1. ПОЛНАЯ ТАБЛИЦА ОПЕРАЦИЙ:")
    print("-" * 80)

    # Форматируем вывод
    display_df = df.copy()
    display_df['type'] = display_df['type'].map({'income': '📈 Доход', 'expense': '📉 Расход'})
    display_df['category_type'] = display_df['category_type'].map({'income': 'Доход', 'expense': 'Расход'})

    # Выбираем нужные колонки и переименовываем их
    display_columns = {
        'date': 'Дата',
        'type': 'Тип операции',
        'amount': 'Сумма',
        'category_name': 'Категория',
        'category_type': 'Тип категории',
        'subcategory_name': 'Подкатегория',
        'description': 'Описание'
    }

    display_df = display_df.rename(columns=display_columns)

    # Настраиваем отображение pandas
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', 30)

    print(display_df[list(display_columns.values())].head(20))

    # 2. Основная статистика
    print("\n2. ОСНОВНАЯ СТАТИСТИКА:")
    print("-" * 80)

    stats = pd.DataFrame({
        'Показатель': [
            'Всего операций',
            'Операций доходов',
            'Операций расходов',
            'Сумма доходов',
            'Сумма расходов',
            'Общий баланс'
        ],
        'Значение': [
            len(df),
            len(df[df['type'] == 'income']),
            len(df[df['type'] == 'expense']),
            df[df['type'] == 'income']['amount'].sum(),
            df[df['type'] == 'expense']['amount'].sum(),
            df[df['type'] == 'income']['amount'].sum() - df[df['type'] == 'expense']['amount'].sum()
        ]
    })

    print(stats.to_string(index=False, float_format='{:,.2f}'.format))

    # 3. Статистика по категориям
    print("\n3. СТАТИСТИКА ПО КАТЕГОРИЯМ:")
    print("-" * 80)

    category_stats = df.groupby(['category_name', 'category_type']).agg(
        operations_count=('id', 'count'),
        total_amount=('amount', 'sum')
    ).reset_index()

    category_stats['category_type'] = category_stats['category_type'].map(
        {'income': 'Доход', 'expense': 'Расход'}
    )

    category_stats = category_stats.rename(columns={
        'category_name': 'Категория',
        'category_type': 'Тип',
        'operations_count': 'Кол-во операций',
        'total_amount': 'Общая сумма'
    })

    print(category_stats.to_string(index=False, float_format='{:,.2f}'.format))

    # 4. Ежемесячная статистика
    print("\n4. ЕЖЕМЕСЯЧНАЯ СТАТИСТИКА:")
    print("-" * 80)

    # Преобразуем дату в месяц
    df['date'] = pd.to_datetime(df['date'])
    df['month'] = df['date'].dt.strftime('%Y-%m')

    monthly_stats = df.groupby('month').agg(
        operations_count=('id', 'count'),
        income=('amount', lambda x: x[df.loc[x.index, 'type'] == 'income'].sum()),
        expense=('amount', lambda x: x[df.loc[x.index, 'type'] == 'expense'].sum())
    ).reset_index()

    monthly_stats['balance'] = monthly_stats['income'] - monthly_stats['expense']
    monthly_stats = monthly_stats.rename(columns={
        'month': 'Месяц',
        'operations_count': 'Операций',
        'income': 'Доходы',
        'expense': 'Расходы',
        'balance': 'Баланс'
    })

    print(monthly_stats.to_string(index=False, float_format='{:,.2f}'.format))

    # 5. Топ-10 самых крупных операций
    print("\n5. ТОП-10 САМЫХ КРУПНЫХ ОПЕРАЦИЙ:")
    print("-" * 80)

    top_operations = df.nlargest(10, 'amount')[['date', 'type', 'amount', 'category_name', 'description']]
    top_operations['type'] = top_operations['type'].map({'income': '📈 Доход', 'expense': '📉 Расход'})

    top_operations = top_operations.rename(columns={
        'date': 'Дата',
        'type': 'Тип',
        'amount': 'Сумма',
        'category_name': 'Категория',
        'description': 'Описание'
    })

    print(top_operations.to_string(index=False, float_format='{:,.2f}'.format))

    # 6. Дополнительные аналитические срезы
    print("\n6. ДОПОЛНИТЕЛЬНАЯ АНАЛИТИКА:")
    print("-" * 80)

    # Средние значения
    avg_income = df[df['type'] == 'income']['amount'].mean()
    avg_expense = df[df['type'] == 'expense']['amount'].mean()

    print(f"Средний доход: {avg_income:,.2f}")
    print(f"Средний расход: {avg_expense:,.2f}")
    print(
        f"Соотношение доход/расход: {avg_income / avg_expense:.2f}:1" if avg_expense > 0 else "Нет расходов для расчета")

    # Медианные значения
    median_income = df[df['type'] == 'income']['amount'].median()
    median_expense = df[df['type'] == 'expense']['amount'].median()

    print(f"Медианный доход: {median_income:,.2f}")
    print(f"Медианный расход: {median_expense:,.2f}")

    print("\n" + "=" * 80)
    print("✅ Анализ завершен!")


def export_operations_to_excel():
    """Экспорт операций в Excel файл"""
    print("\n💾 ЭКСПОРТ ОПЕРАЦИЙ В EXCEL")
    print("-" * 80)

    df = get_operations_as_dataframe()

    if df is None or df.empty:
        print("❌ Нет данных для экспорта")
        return

    try:
        # Создаем Excel writer
        filename = f'operations_export_{pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")}.xlsx'

        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # 1. Основной лист с операциями
            df_export = df.copy()
            df_export['type'] = df_export['type'].map({'income': 'Доход', 'expense': 'Расход'})
            df_export['category_type'] = df_export['category_type'].map({'income': 'Доход', 'expense': 'Расход'})

            df_export.to_excel(writer, sheet_name='Операции', index=False)

            # 2. Лист со статистикой по категориям
            category_stats = df.groupby(['category_name', 'category_type']).agg(
                operations_count=('id', 'count'),
                total_amount=('amount', 'sum')
            ).reset_index()

            category_stats.to_excel(writer, sheet_name='Статистика по категориям', index=False)

            # 3. Лист с ежемесячной статистикой
            df['date'] = pd.to_datetime(df['date'])
            df['month'] = df['date'].dt.strftime('%Y-%m')

            monthly_stats = df.groupby('month').agg(
                operations_count=('id', 'count'),
                income=('amount', lambda x: x[df.loc[x.index, 'type'] == 'income'].sum()),
                expense=('amount', lambda x: x[df.loc[x.index, 'type'] == 'expense'].sum())
            ).reset_index()

            monthly_stats['balance'] = monthly_stats['income'] - monthly_stats['expense']
            monthly_stats.to_excel(writer, sheet_name='Ежемесячная статистика', index=False)

        print(f"✅ Данные успешно экспортированы в файл: {filename}")
        print(f"📁 Файл содержит 3 листа:")
        print("   1. Операции - полный список операций")
        print("   2. Статистика по категориям - группировка по категориям")
        print("   3. Ежемесячная статистика - статистика по месяцам")

    except Exception as e:
        print(f"❌ Ошибка при экспорте в Excel: {e}")


def interactive_pandas_analysis():
    """Интерактивный анализ с pandas"""
    print("🔍 ИНТЕРАКТИВНЫЙ АНАЛИЗ ОПЕРАЦИЙ С PANDAS")
    print("=" * 80)

    df = get_operations_as_dataframe()

    if df is None or df.empty:
        return

    while True:
        print("\n" + "-" * 80)
        print("МЕНЮ АНАЛИЗА:")
        print("1. Показать все операции")
        print("2. Показать только доходы")
        print("3. Показать только расходы")
        print("4. Показать операции за конкретный месяц")
        print("5. Показать операции по категории")
        print("6. Поиск операций по описанию")
        print("7. Экспорт в Excel")
        print("8. Выйти")

        choice = input("\nВыберите действие (1-8): ").strip()

        if choice == '1':
            # Все операции
            print("\n📋 ВСЕ ОПЕРАЦИИ:")
            print(df[['date', 'type', 'amount', 'category_name', 'description']].head(20).to_string())

        elif choice == '2':
            # Только доходы
            income_df = df[df['type'] == 'income']
            print(f"\n📈 ДОХОДЫ ({len(income_df)} операций):")
            print(income_df[['date', 'amount', 'category_name', 'description']].head(20).to_string())
            print(f"\nОбщая сумма доходов: {income_df['amount'].sum():,.2f}")

        elif choice == '3':
            # Только расходы
            expense_df = df[df['type'] == 'expense']
            print(f"\n📉 РАСХОДЫ ({len(expense_df)} операций):")
            print(expense_df[['date', 'amount', 'category_name', 'description']].head(20).to_string())
            print(f"\nОбщая сумма расходов: {expense_df['amount'].sum():,.2f}")

        elif choice == '4':
            # По месяцу
            month = input("Введите месяц в формате ГГГГ-ММ (например, 2024-01): ").strip()
            if month:
                month_df = df[df['date'].str.startswith(month)]
                if not month_df.empty:
                    print(f"\n📅 ОПЕРАЦИИ ЗА {month}:")
                    print(month_df[['date', 'type', 'amount', 'category_name', 'description']].to_string())

                    # Статистика за месяц
                    month_income = month_df[month_df['type'] == 'income']['amount'].sum()
                    month_expense = month_df[month_df['type'] == 'expense']['amount'].sum()
                    print(f"\nСтатистика за месяц:")
                    print(f"Доходы: {month_income:,.2f}")
                    print(f"Расходы: {month_expense:,.2f}")
                    print(f"Баланс: {month_income - month_expense:,.2f}")
                else:
                    print(f"❌ Операций за {month} не найдено")

        elif choice == '5':
            # По категории
            categories = df['category_name'].unique()
            print("\nДоступные категории:")
            for i, cat in enumerate(categories, 1):
                print(f"{i}. {cat}")

            cat_choice = input("\nВведите номер или название категории: ").strip()

            try:
                if cat_choice.isdigit():
                    cat_index = int(cat_choice) - 1
                    if 0 <= cat_index < len(categories):
                        selected_category = categories[cat_index]
                    else:
                        print("❌ Неверный номер категории")
                        continue
                else:
                    selected_category = cat_choice

                category_df = df[df['category_name'] == selected_category]
                if not category_df.empty:
                    print(f"\n📁 ОПЕРАЦИИ ПО КАТЕГОРИИ '{selected_category}':")
                    print(category_df[['date', 'type', 'amount', 'description']].to_string())

                    cat_income = category_df[category_df['type'] == 'income']['amount'].sum()
                    cat_expense = category_df[category_df['type'] == 'expense']['amount'].sum()
                    print(f"\nСтатистика по категории:")
                    print(f"Операций: {len(category_df)}")
                    print(f"Доходы: {cat_income:,.2f}")
                    print(f"Расходы: {cat_expense:,.2f}")
                else:
                    print(f"❌ Операций по категории '{selected_category}' не найдено")

            except Exception as e:
                print(f"❌ Ошибка: {e}")

        elif choice == '6':
            # Поиск по описанию
            search_term = input("Введите текст для поиска в описании: ").strip().lower()
            if search_term:
                search_df = df[df['description'].str.contains(search_term, case=False, na=False)]
                if not search_df.empty:
                    print(f"\n🔍 РЕЗУЛЬТАТЫ ПОИСКА '{search_term}':")
                    print(search_df[['date', 'type', 'amount', 'category_name', 'description']].to_string())
                else:
                    print(f"❌ Операций с текстом '{search_term}' не найдено")

        elif choice == '7':
            # Экспорт в Excel
            export_operations_to_excel()

        elif choice == '8':
            print("\n👋 Выход из анализа")
            break

        else:
            print("❌ Неверный выбор. Попробуйте снова.")


def main():
    """Основная функция"""
    print("\n" + "=" * 80)
    print("📊 АНАЛИЗ ОПЕРАЦИЙ С ИСПОЛЬЗОВАНИЕМ PANDAS")
    print("=" * 80)

    # Проверяем установлен ли pandas
    try:
        import pandas as pd
        print("✅ Pandas установлен")
    except ImportError:
        print("❌ Pandas не установлен. Установите его командой:")
        print("   pip install pandas openpyxl")
        return

    while True:
        print("\n" + "-" * 80)
        print("ГЛАВНОЕ МЕНЮ:")
        print("1. 📊 Показать полный анализ операций")
        print("2. 🔍 Интерактивный анализ")
        print("3. 💾 Экспорт в Excel")
        print("4. 📋 Показать информацию о данных")
        print("5. 🚪 Выход")

        choice = input("\nВыберите действие (1-5): ").strip()

        if choice == '1':
            display_operations_with_pandas()
        elif choice == '2':
            interactive_pandas_analysis()
        elif choice == '3':
            export_operations_to_excel()
        elif choice == '4':
            show_data_info()
        elif choice == '5':
            print("\n👋 До свидания!")
            break
        else:
            print("❌ Неверный выбор. Попробуйте снова.")


def show_data_info():
    """Показать информацию о данных"""
    df = get_operations_as_dataframe()

    if df is None or df.empty:
        return

    print("\n📋 ИНФОРМАЦИЯ О ДАННЫХ:")
    print("-" * 80)

    # Основная информация
    print("📊 ОСНОВНАЯ ИНФОРМАЦИЯ:")
    print(f"Количество операций: {len(df)}")
    print(f"Количество столбцов: {len(df.columns)}")
    print(f"Период данных: с {df['date'].min()} по {df['date'].max()}")

    print("\n📈 СТАТИСТИКА ПО ТИПАМ:")
    type_counts = df['type'].value_counts()
    for type_val, count in type_counts.items():
        type_name = 'Доход' if type_val == 'income' else 'Расход'
        print(f"{type_name}: {count} операций ({count / len(df) * 100:.1f}%)")

    print("\n🏷️ КАТЕГОРИИ:")
    print(f"Уникальных категорий: {df['category_name'].nunique()}")
    top_categories = df['category_name'].value_counts().head(5)
    print("Самые популярные категории:")
    for category, count in top_categories.items():
        print(f"  {category}: {count} операций")

    print("\n📅 РАСПРЕДЕЛЕНИЕ ПО МЕСЯЦАМ:")
    df['month'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m')
    month_counts = df['month'].value_counts().sort_index()
    for month, count in month_counts.items():
        print(f"  {month}: {count} операций")

    print("\n💰 СТАТИСТИКА ПО СУММАМ:")
    print(f"Минимальная сумма: {df['amount'].min():,.2f}")
    print(f"Максимальная сумма: {df['amount'].max():,.2f}")
    print(f"Средняя сумма: {df['amount'].mean():,.2f}")
    print(f"Медианная сумма: {df['amount'].median():,.2f}")

    print("\n📊 СТРУКТУРА ДАННЫХ:")
    print(df.info())

    print("\n" + "-" * 80)


if __name__ == "__main__":
    main()