from psycopg2 import sql

from app.db.dbConnector import DbConnector


class RecordManager(DbConnector):
    def __init__(self, table_name):
        super().__init__()

        self.table_name = table_name
    
    def check(self, conditions):
        columns = conditions.keys()
        values = [conditions[column] for column in columns]

        placeholders = ", ".join(["%s"] * len(values))
        columns_str = ", ".join(columns)

        query = f"SELECT 1 FROM {self.table_name} WHERE ({columns_str}) = ({placeholders})"

        self.cursor.execute(query, values)
        exists = self.cursor.fetchone() is not None

        return exists


    def create(self, data):
        columns = data.keys()
        values = [data[column] for column in columns]

        placeholders = ", ".join(["%s"] * len(values))
        columns_str = ", ".join(columns)
        
        query = f"INSERT INTO {self.table_name}({columns_str}) VALUES ({placeholders}) RETURNING id"
        self.cursor.execute(query, values)

        id = self.cursor.fetchone()[0]

        return id


    def delete(self, id):
        self.cursor.execute(f"DELETE FROM {self.table_name} WHERE id = %s", (id,))
    

    def update(self, update_fields, id):
        set_clause = sql.SQL(", ").join(
            sql.SQL("{} = %s").format(sql.Identifier(k)) for k in update_fields.keys()
        )


        query = sql.SQL("UPDATE {table_name} SET {set_clause} WHERE id = {id}").format(
            table_name=sql.Identifier(self.table_name),
            set_clause=set_clause,
            condition=sql.SQL(id)
        )


        values = list(update_fields.values())

        # Выполняем запрос
        self.cursor.execute(query, values)


    def get(self, conditions=None):
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
            table_name=sql.Identifier(self.table_name)
        )
        query += where_clause

        self.cursor.execute(query, values)
        rows = self.cursor.fetchall()

        col_names = [desc[0] for desc in self.cursor.description]

        result_list = [dict(zip(col_names, row)) for row in rows]

        return result_list