from typing import Optional, List, Dict, Any
class ConsoleFormatter:
    """Класс для форматирования вывода в консоль"""

    @staticmethod
    def print_header(title: str):
        """Вывод красивого заголовка"""
        width = 70
        print("\n" + "═" * width)
        print(f"{'💰 ' + title + ' 💰':^{width}}")
        print("═" * width)

    @staticmethod
    def print_success(message: str):
        """Вывод успешного сообщения"""
        print(f"\n✅ {message}")

    @staticmethod
    def print_error(message: str):
        """Вывод сообщения об ошибке"""
        print(f"\n❌ {message}")

    @staticmethod
    def print_info(message: str):
        """Вывод информационного сообщения"""
        print(f"\nℹ️  {message}")

    @staticmethod
    def print_warning(message: str):
        """Вывод предупреждения"""
        print(f"\n⚠️  {message}")

    @staticmethod
    def print_menu(options: List[str], title: str = None):
        """Вывод меню с опциями"""
        if title:
            print(f"\n{title}:")
        for i, option in enumerate(options, 1):
            print(f"{i:>2}. {option}")

    @staticmethod
    def print_table(headers: List[str], rows: List[List[Any]], title: str = None,
                    show_full_ids: bool = False):
        """Вывод таблицы с данными"""
        if title:
            ConsoleFormatter.print_header(title)

        if not rows:
            ConsoleFormatter.print_info("Нет данных для отображения")
            return

        # Определяем ширину колонок
        col_widths = []
        for i, header in enumerate(headers):
            max_width = len(str(header))
            for row in rows:
                cell_width = len(str(row[i])) if i < len(row) else 0
                max_width = max(max_width, cell_width)
            col_widths.append(min(max_width, 50 if show_full_ids and i == 0 else 30))

        # Вывод разделителя
        total_width = sum(col_widths) + 3 * len(col_widths) + 1
        print("┌" + "─" * (total_width - 2) + "┐")

        # Вывод заголовков
        header_row = "│"
        for i, header in enumerate(headers):
            header_row += f" {str(header).ljust(col_widths[i])} │"
        print(header_row)

        # Вывод разделителя
        print("├" + "─" * (total_width - 2) + "┤")

        # Вывод строк
        for row in rows:
            row_str = "│"
            for i, cell in enumerate(row):
                cell_str = str(cell)
                if len(cell_str) > col_widths[i]:
                    cell_str = cell_str[:col_widths[i] - 3] + "..."
                row_str += f" {cell_str.ljust(col_widths[i])} │"
            print(row_str)

        # Вывод нижней границы
        print("└" + "─" * (total_width - 2) + "┘")

    @staticmethod
    def get_input(prompt: str, required: bool = False, input_type: type = str,
                  validation_func=None, default: str = None) -> Any:
        """Безопасный ввод данных с валидацией"""
        while True:
            try:
                if default:
                    value = input(f"\n{prompt} [{default}]: ").strip()
                    if not value:
                        value = default
                else:
                    value = input(f"\n{prompt}: ").strip()

                if required and not value:
                    ConsoleFormatter.print_error("Это поле обязательно для заполнения!")
                    continue

                if input_type == int:
                    value = int(value)
                elif input_type == float:
                    value = float(value)
                elif input_type == bool:
                    value = value.lower() in ['y', 'yes', 'да', 'д', 'true', '1']

                if validation_func and not validation_func(value):
                    continue

                return value

            except ValueError:
                ConsoleFormatter.print_error(f"Пожалуйста, введите корректное значение типа {input_type.__name__}")
            except KeyboardInterrupt:
                ConsoleFormatter.print_warning("Операция прервана пользователем")
                return None
