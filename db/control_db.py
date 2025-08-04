

class ControlTable():
    def __init__(self, cursor):
        self.cursor = cursor

    def createTable(self, table_name:str, fields:list):
        """
        Создает таблицу с указанными полями.
        
        :param db_name: Название базы данных
        :param table_name: Название таблицы
        :param fields: список кортежей (имя_поля, тип_данных, ограничения)
                        например: [('login', 'VARCHAR(255)', 'NOT NULL CHECK (LENGTH(login) >= 3)'), ...]
        :param user: имя пользователя
        :param password: пароль
        :param host: хост базы данных (по умолчанию localhost)
        """

        # Формируем строку определения полей
        fields_str = ', '.join([f"{name} {dtype} {constraints or ''}".strip() for name, dtype, constraints in fields])
        
        query = f"CREATE TABLE IF NOT EXISTS {table_name} (id INTEGER PRIMARY KEY, {fields_str});"

        self.cursor.execute(query)

        print(f"Таблица '{table_name}' создана или уже существует.")
