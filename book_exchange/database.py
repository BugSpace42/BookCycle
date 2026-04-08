"""
Модуль database.py
Отвечает за подключение к базе данных MySQL и выполнение SQL-запросов
"""

import mysql.connector
from mysql.connector import Error
from contextlib import contextmanager


class Database:
    """Класс для управления подключением к базе данных MySQL"""

    def __init__(self, host="localhost", user="root", password="", database="books_exchange"):
        """
        Инициализация базы данных

        Args:
            host (str): Хост MySQL сервера
            user (str): Имя пользователя MySQL
            password (str): Пароль пользователя MySQL
            database (str): Имя базы данных
        """
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self._init_database()

    def _get_connection_without_db(self):
        """Создает подключение к MySQL серверу без выбора базы данных"""
        try:
            conn = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password
            )
            return conn
        except Error as e:
            print(f"Ошибка подключения к MySQL серверу: {e}")
            return None

    def _create_database_if_not_exists(self):
        """Создает базу данных, если она не существует"""
        conn = self._get_connection_without_db()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database}")
                cursor.execute(f"USE {self.database}")
                conn.commit()
                print(f"База данных '{self.database}' проверена/создана")
            except Error as e:
                print(f"Ошибка при создании базы данных: {e}")
            finally:
                conn.close()

    def _init_database(self):
        """Создает таблицы, если они не существуют"""
        # Сначала создаем базу данных
        self._create_database_if_not_exists()

        # SQL-запросы для создания таблиц (адаптированные для MySQL)
        create_tables_queries = [
            # Таблица пользователей
            """
            CREATE TABLE IF NOT EXISTS Users (
                id INT PRIMARY KEY AUTO_INCREMENT,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                phone VARCHAR(20),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """,
            # Таблица книг (изданий)
            """
            CREATE TABLE IF NOT EXISTS Book (
                id INT PRIMARY KEY AUTO_INCREMENT,
                title VARCHAR(255) NOT NULL,
                author VARCHAR(255) NOT NULL,
                genre VARCHAR(100),
                year INT,
                description TEXT,
                INDEX idx_title_author (title, author)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """,
            # Таблица экземпляров книг
            """
            CREATE TABLE IF NOT EXISTS BookItem (
                id INT PRIMARY KEY AUTO_INCREMENT,
                book_id INT NOT NULL,
                owner_id INT NOT NULL,
                status ENUM('available', 'pending', 'exchanged') DEFAULT 'available',
                `condition` ENUM('new', 'good', 'fair', 'poor') DEFAULT 'good',
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (book_id) REFERENCES Book(id) ON DELETE CASCADE,
                FOREIGN KEY (owner_id) REFERENCES Users(id) ON DELETE CASCADE,
                INDEX idx_status (status),
                INDEX idx_owner (owner_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """,
            # Таблица запросов на обмен
            """
            CREATE TABLE IF NOT EXISTS ExchangeRequest (
                id INT PRIMARY KEY AUTO_INCREMENT,
                book_item_id INT NOT NULL,
                requester_id INT NOT NULL,
                owner_id INT NOT NULL,
                status ENUM('pending', 'accepted', 'rejected') DEFAULT 'pending',
                requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                responded_at TIMESTAMP NULL,
                FOREIGN KEY (book_item_id) REFERENCES BookItem(id) ON DELETE CASCADE,
                FOREIGN KEY (requester_id) REFERENCES Users(id) ON DELETE CASCADE,
                FOREIGN KEY (owner_id) REFERENCES Users(id) ON DELETE CASCADE,
                INDEX idx_status_owner (status, owner_id),
                INDEX idx_requester (requester_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """,
            # Таблица истории обменов
            """
            CREATE TABLE IF NOT EXISTS ExchangeHistory (
                id INT PRIMARY KEY AUTO_INCREMENT,
                exchange_req_id INT NOT NULL UNIQUE,
                completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (exchange_req_id) REFERENCES ExchangeRequest(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """
        ]

        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                for query in create_tables_queries:
                    cursor.execute(query)
                conn.commit()
                print("Таблицы успешно созданы/проверены")
        except Error as e:
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
        conn = None
        try:
            conn = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                autocommit=False
            )
            # Настройка для получения результатов в виде словарей
            conn.row_factory = self._dict_factory
            yield conn
            conn.commit()
        except Error as e:
            if conn:
                conn.rollback()
            print(f"Ошибка подключения к базе данных: {e}")
            raise
        finally:
            if conn:
                conn.close()

    def _dict_factory(self, cursor, row):
        """Преобразует строку результата в словарь"""
        return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}

    def execute(self, query, params=None):
        params = params or ()
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                # Преобразуем ? в %s для MySQL
                mysql_query = query.replace('?', '%s')
                cursor.execute(mysql_query, params)
                conn.commit()
                if query.strip().upper().startswith('INSERT'):
                    return cursor.lastrowid
                return cursor.rowcount
        except Error as e:
            print(f"Ошибка выполнения запроса: {e}")
            print(f"Запрос: {query}")
            print(f"Параметры: {params}")
            return None

    def fetch_all(self, query, params=None):
        params = params or ()
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor(dictionary=True)
                mysql_query = query.replace('?', '%s')
                cursor.execute(mysql_query, params)
                return cursor.fetchall()
        except Error as e:
            print(f"Ошибка выполнения запроса: {e}")
            return []

    def fetch_one(self, query, params=None):
        params = params or ()
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor(dictionary=True)
                mysql_query = query.replace('?', '%s')
                cursor.execute(mysql_query, params)
                return cursor.fetchone()
        except Error as e:
            print(f"Ошибка выполнения запроса: {e}")
            return None


# Создаем глобальный экземпляр базы данных
# ИЗМЕНИ ПАРАМЕТРЫ ПОД СВОИ НАСТРОЙКИ MySQL!
db = Database(
    host="localhost",     # Хост MySQL (обычно localhost)
    user="root",          # Имя пользователя MySQL
    password="cGnhD7!!",          # Пароль MySQL (если есть)
    database="books_exchange"  # Имя базы данных
)