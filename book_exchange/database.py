"""
Модуль database.py
Отвечает за подключение к базе данных и выполнение SQL-запросов
"""

import sqlite3
import os
from contextlib import contextmanager


class Database:
    """Класс для управления подключением к базе данных"""

    def __init__(self, db_name="books.db"):
        """
        Инициализация базы данных

        Args:
            db_name (str): Имя файла базы данных
        """
        self.db_name = db_name
        self._init_database()

    def _init_database(self):
        """Создает таблицы, если они не существуют"""
        # SQL-запросы для создания таблиц
        create_tables_queries = [
            # Таблица пользователей
            """
            CREATE TABLE IF NOT EXISTS Users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                phone TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """,
            # Таблица книг (изданий)
            """
            CREATE TABLE IF NOT EXISTS Book (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                genre TEXT,
                year INTEGER,
                description TEXT
            )
            """,
            # Таблица экземпляров книг
            """
            CREATE TABLE IF NOT EXISTS BookItem (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                book_id INTEGER NOT NULL,
                owner_id INTEGER NOT NULL,
                status TEXT DEFAULT 'available',
                condition TEXT DEFAULT 'good',
                added_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (book_id) REFERENCES Book(id) ON DELETE CASCADE,
                FOREIGN KEY (owner_id) REFERENCES Users(id) ON DELETE CASCADE
            )
            """,
            # Таблица запросов на обмен
            """
            CREATE TABLE IF NOT EXISTS ExchangeRequest (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                book_item_id INTEGER NOT NULL,
                requester_id INTEGER NOT NULL,
                owner_id INTEGER NOT NULL,
                status TEXT DEFAULT 'pending',
                requested_at TEXT DEFAULT CURRENT_TIMESTAMP,
                responded_at TEXT,
                FOREIGN KEY (book_item_id) REFERENCES BookItem(id) ON DELETE CASCADE,
                FOREIGN KEY (requester_id) REFERENCES Users(id) ON DELETE CASCADE,
                FOREIGN KEY (owner_id) REFERENCES Users(id) ON DELETE CASCADE
            )
            """,
            # Таблица истории обменов
            """
            CREATE TABLE IF NOT EXISTS ExchangeHistory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                exchange_req_id INTEGER NOT NULL UNIQUE,
                completed_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (exchange_req_id) REFERENCES ExchangeRequest(id) ON DELETE CASCADE
            )
            """
        ]

        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                for query in create_tables_queries:
                    cursor.execute(query)
                conn.commit()
                print("База данных успешно инициализирована")
        except sqlite3.Error as e:
            print(f"Ошибка при создании таблиц: {e}")

    @contextmanager
    def get_connection(self):
        """
        Контекстный менеджер для работы с подключением к БД

        Использование:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM Users")
        """
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row  # Позволяет обращаться к колонкам по имени
        try:
            yield conn
        finally:
            conn.close()

    def execute(self, query, params=None):
        """
        Выполняет SQL-запрос (INSERT, UPDATE, DELETE)

        Args:
            query (str): SQL-запрос
            params (tuple/dict): Параметры запроса

        Returns:
            int: ID последней вставленной записи или None
        """
        params = params or ()
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                conn.commit()
                return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Ошибка выполнения запроса: {e}")
            print(f"Запрос: {query}")
            print(f"Параметры: {params}")
            return None

    def fetch_all(self, query, params=None):
        """
        Выполняет SELECT и возвращает все строки

        Args:
            query (str): SQL-запрос
            params (tuple/dict): Параметры запроса

        Returns:
            list: Список строк (каждая строка — объект Row)
        """
        params = params or ()
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Ошибка выполнения запроса: {e}")
            return []

    def fetch_one(self, query, params=None):
        """
        Выполняет SELECT и возвращает одну строку

        Args:
            query (str): SQL-запрос
            params (tuple/dict): Параметры запроса

        Returns:
            Row: Строка результата или None
        """
        params = params or ()
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                return cursor.fetchone()
        except sqlite3.Error as e:
            print(f"Ошибка выполнения запроса: {e}")
            return None


# Создаем глобальный экземпляр базы данных
db = Database()