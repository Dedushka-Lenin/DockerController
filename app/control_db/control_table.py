from psycopg2 import sql

from typing import List
from app.models.schemas import CreateTableConf

class ControlTable():
    def __init__(self, cursor):
        self.cursor = cursor

    def createTable(self, table_name: str, fields: List[CreateTableConf]):
        """
        Создает таблицу с указанными полями.
        :param table_name: имя таблицы (строка)
        :param fields: список объектов CreateTableConf
        """

        # Формируем строку определения полей
        fields_str = sql.SQL(", ").join(
            sql.SQL("{} {} {}").format(
                sql.Identifier(field['name']),
                sql.SQL(field['dtype']),
                sql.SQL(field['constraints'])
            )
            for field in fields
        )

        # Формируем полный запрос
        query = sql.SQL("CREATE TABLE IF NOT EXISTS {table} (id BIGSERIAL PRIMARY KEY, {fields})").format(
            table=sql.Identifier(table_name),
            fields=fields_str
        )

        self.cursor.execute(query)

####################################################################################################
    
    # Функция проверки наличия таблицы
    def checkTableExists(self, table_name):
        query = """
            SELECT EXISTS (
                SELECT 1
                FROM information_schema.tables
                WHERE table_schema = 'public' AND table_name = %s
            );
        """

        self.cursor.execute(query, (table_name,))
        exists = self.cursor.fetchone()[0]

        if exists:
            return {"exists": True, "message": "Таблица найдена"}
        else:
            return {"exists": False, "message": "Таблица не найдена"}
        
    # # Функция проверки наличия записи
    def checkRecordExists(self, table_name, id):
        """
        Получает записи из таблицы по заданным условиям.
        :param table_name: имя таблицы (строка)
        :param id: id (число)
        """

        success = self.checkTableExists(table_name=table_name)
        if not success["exists"]:
            return success

        self.cursor.execute(f"SELECT 1 FROM {table_name} WHERE id = %s", (id,))
        exists = self.cursor.fetchone() is not None

        if not exists:
            return {"exists": exists, "message": f"Запись c id = {id} не найдена"}

        return {"exists":exists, "message": "Запись найдена"}

    
####################################################################################################
    
    # Функция создания записи
    def createRecordTable(self, table_name, data):
        """
        Получает записи из таблицы по заданным условиям.
        :param table_name: имя таблицы (строка)
        :param data: список ключ значение (dict)
        """

        success = self.checkTableExists(table_name=table_name)
        if not success["exists"]:
            return success

        columns = data.keys()
        values = [data[column] for column in columns]

        placeholders = ", ".join(["%s"] * len(values))
        columns_str = ", ".join(columns)
        
        query = f"INSERT INTO {table_name}({columns_str}) VALUES ({placeholders}) RETURNING id"
        self.cursor.execute(query, values)

        id = self.cursor.fetchone()[0]

        return {"exists": True, "message": "Запись успешно созданна", "id":id}

    # Функция удаления записи
    def deleteRecordTable(self, table_name, id):
        """
        Получает записи из таблицы по заданным условиям.
        :param table_name: имя таблицы (строка)
        :param id: id (число)
        """

        success = self.checkRecordExists(table_name=table_name, id=id)
        if not success["exists"]:
            return success
        
        # Удаление записи
        self.cursor.execute(f"DELETE FROM {table_name} WHERE id = %s", (id,))
        
        return {"exists": True, "message": "Запись успешно удалена"}
    
    # Функция изменения записи
    def updateRecordTable(self, table_name, update_fields, id):
        """
        Получает записи из таблицы по заданным условиям.
        :param table_name: имя таблицы (строка)
        :param update_fields: список ключ значение (dict)
        :param id: id (число)
        """

        success = self.checkRecordExists(table_name=table_name, id=id)
        if not success["exists"]:
            return success

        # Формируем часть SET запроса
        set_clause = sql.SQL(", ").join(
            sql.SQL("{} = %s").format(sql.Identifier(k)) for k in update_fields.keys()
        )

        # Формируем полный SQL-запрос
        query = sql.SQL("UPDATE {table_name} SET {set_clause} WHERE id = {id}").format(
            table_name=sql.Identifier(table_name),
            set_clause=set_clause,
            condition=sql.SQL(id)
        )

        # Значения для подстановки
        values = list(update_fields.values())

        # Выполняем запрос
        self.cursor.execute(query, values)

        return {"exists": True, "message": f"Запись в таблице '{table_name}' успешно обновлена."}

####################################################################################################

    # Функция вывода информации о записи
    def fetchRecordTable(self, table_name, conditions=None):
        """
        Получает записи из таблицы по заданным условиям.
        :param table_name: имя таблицы (строка)
        :param conditions: dict с условиями {column: value} или None для без условий
        :return: список кортежей с результатами
        """ 

        # Формируем условие WHERE, если есть

        if conditions:
            condition_clauses = []
            values = []
            for col, val in conditions.items():
                condition_clauses.append(sql.SQL("{} = %s").format(sql.Identifier(col)))
                values.append(val)
            where_clause = sql.SQL(" WHERE ") + sql.SQL(" AND ").join(condition_clauses)
        else:
            where_clause = sql.SQL("")
            values = []

        query = sql.SQL("SELECT * FROM {table_name}").format(
            table_name=sql.Identifier(table_name)
        )
        query += where_clause

        self.cursor.execute(query, values)
        rows = self.cursor.fetchall()

        # Получаем имена колонок
        col_names = [desc[0] for desc in self.cursor.description]

        # Преобразуем каждую строку в словарь
        result_list = [dict(zip(col_names, row)) for row in rows]

        return result_list