import sqlite3
from config import DB_NAME


class DATABASE:
    def __init__(self):
        self.NAME = DB_NAME

    def execute_query(self, query, data=None):
        """
        Функция для выполнения запроса к базе данных.
        Принимает имя файла базы данных, SQL-запрос и опциональные данные для вставки.
        """
        try:
            connection = sqlite3.connect(self.NAME)
            cursor = connection.cursor()

            if data:
                cursor.execute(query, data)
            else:
                cursor.execute(query)
            cursor = cursor.fetchall()
            connection.commit()
            connection.close()
            return cursor

        except sqlite3.Error as e:
            print("Ошибка при выполнении запроса:", e)

        finally:
            connection.close()

    def create_table(self):

        sql_query = """CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            subject TEXT,
            level TEXT,
            answer TEXT
        );"""
        self.execute_query(sql_query)

    def add_data(self, user_id, subject):

        sql_query = 'INSERT INTO users (user_id, subject) VALUES (?, ?);'
        data = (user_id, subject,)

        self.execute_query(sql_query, data)

    def update_data(self, user_id, column, value):

        sql_query = f'UPDATE users SET {column} = ? WHERE user_id = ?;'
        data = (value, user_id,)
        self.execute_query(sql_query, data)

    def get_data(self, column, user_id):
        sql_query = f'SELECT {column} FROM users WHERE user_id = ?;'
        data = (user_id,)
        result = self.execute_query(sql_query, data)
        return result
