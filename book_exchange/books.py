"""
Модуль books.py
Управление книгами: добавление, редактирование, удаление, поиск книг и экземпляров
"""

from database import db
from auth import auth
from datetime import datetime


class BookManager:
    """Класс для управления книгами и экземплярами"""

    def __init__(self):
        """Инициализация менеджера книг"""
        pass

    # ==================== РАБОТА С КНИГАМИ (ИЗДАНИЯМИ) ====================

    def add_book(self, title, author, genre=None, year=None, description=None):
        """
        Добавление новой книги (издания)

        Args:
            title (str): Название книги
            author (str): Автор
            genre (str): Жанр
            year (int): Год издания
            description (str): Описание

        Returns:
            tuple: (success: bool, message: str, book_id: int)
        """
        if not title or not author:
            return False, "Название и автор обязательны для заполнения", None

        # Проверяем, существует ли уже такая книга
        existing = db.fetch_one(
            "SELECT id FROM Book WHERE title = ? AND author = ?",
            (title.strip(), author.strip())
        )

        if existing:
            return False, f"Книга '{title}' автора {author} уже существует в каталоге", existing['id']

        try:
            book_id = db.execute(
                """INSERT INTO Book (title, author, genre, year, description) 
                   VALUES (?, ?, ?, ?, ?)""",
                (title.strip(), author.strip(), genre, year, description)
            )
            if book_id:
                return True, f"Книга '{title}' успешно добавлена в каталог", book_id
            else:
                return False, "Ошибка при добавлении книги", None
        except Exception as e:
            return False, f"Ошибка базы данных: {e}", None

    def get_all_books(self):
        """
        Получение всех книг из каталога

        Returns:
            list: Список книг
        """
        return db.fetch_all(
            "SELECT * FROM Book ORDER BY author, title"
        )

    def get_book_by_id(self, book_id):
        """
        Получение книги по ID

        Args:
            book_id (int): ID книги

        Returns:
            dict: Информация о книге или None
        """
        return db.fetch_one("SELECT * FROM Book WHERE id = ?", (book_id,))

    def search_books(self, keyword):
        """
        Поиск книг по ключевому слову (название, автор, жанр)

        Args:
            keyword (str): Ключевое слово для поиска

        Returns:
            list: Список найденных книг
        """
        if not keyword:
            return self.get_all_books()

        search_term = f"%{keyword}%"
        return db.fetch_all(
            """SELECT * FROM Book 
               WHERE title LIKE ? OR author LIKE ? OR genre LIKE ?
               ORDER BY author, title""",
            (search_term, search_term, search_term)
        )

    def update_book(self, book_id, title=None, author=None, genre=None, year=None, description=None):
        """
        Обновление информации о книге

        Args:
            book_id (int): ID книги
            title (str): Новое название
            author (str): Новый автор
            genre (str): Новый жанр
            year (int): Новый год издания
            description (str): Новое описание

        Returns:
            tuple: (success: bool, message: str)
        """
        # Проверяем, существует ли книга
        book = self.get_book_by_id(book_id)
        if not book:
            return False, "Книга не найдена"

        updates = []
        params = []

        if title:
            updates.append("title = ?")
            params.append(title.strip())
        if author:
            updates.append("author = ?")
            params.append(author.strip())
        if genre is not None:
            updates.append("genre = ?")
            params.append(genre if genre else None)
        if year is not None:
            updates.append("year = ?")
            params.append(year if year else None)
        if description is not None:
            updates.append("description = ?")
            params.append(description if description else None)

        if not updates:
            return False, "Нет данных для обновления"

        params.append(book_id)
        query = f"UPDATE Book SET {', '.join(updates)} WHERE id = ?"

        try:
            result = db.execute(query, params)
            if result is not None:
                return True, "Информация о книге успешно обновлена"
            else:
                return False, "Ошибка при обновлении книги"
        except Exception as e:
            return False, f"Ошибка базы данных: {e}"

    def delete_book(self, book_id):
        """
        Удаление книги и всех её экземпляров (каскадное удаление)

        Args:
            book_id (int): ID книги

        Returns:
            tuple: (success: bool, message: str)
        """
        # Проверяем, есть ли экземпляры этой книги
        items = db.fetch_all(
            "SELECT * FROM BookItem WHERE book_id = ?",
            (book_id,)
        )

        if items:
            return False, f"Невозможно удалить книгу: существует {len(items)} экземпляр(ов). Сначала удалите все экземпляры."

        try:
            result = db.execute("DELETE FROM Book WHERE id = ?", (book_id,))
            if result is not None:
                return True, "Книга успешно удалена"
            else:
                return False, "Ошибка при удалении книги"
        except Exception as e:
            return False, f"Ошибка базы данных: {e}"

    # ==================== РАБОТА С ЭКЗЕМПЛЯРАМИ КНИГ ====================

    def add_book_item(self, book_id, condition="good"):
        """
        Добавление экземпляра книги (для текущего пользователя)

        Args:
            book_id (int): ID книги
            condition (str): Состояние (new, good, fair, poor)

        Returns:
            tuple: (success: bool, message: str)
        """
        if not auth.is_authenticated():
            return False, "Пользователь не авторизован"

        # Проверяем, существует ли книга
        book = self.get_book_by_id(book_id)
        if not book:
            return False, "Книга не найдена"

        # Проверяем валидность состояния
        valid_conditions = ["new", "good", "fair", "poor"]
        if condition not in valid_conditions:
            condition = "good"

        try:
            item_id = db.execute(
                """INSERT INTO BookItem (book_id, owner_id, `condition`, status) 
                   VALUES (?, ?, ?, 'available')""",
                (book_id, auth.current_user['id'], condition)
            )
            if item_id:
                return True, f"Экземпляр книги '{book['title']}' успешно добавлен в вашу библиотеку"
            else:
                return False, "Ошибка при добавлении экземпляра"
        except Exception as e:
            return False, f"Ошибка базы данных: {e}"

    def get_user_items(self, user_id=None):
        """
        Получение всех экземпляров книг пользователя

        Args:
            user_id (int): ID пользователя (если None, берет текущего)

        Returns:
            list: Список экземпляров с информацией о книгах
        """
        if user_id is None:
            if not auth.is_authenticated():
                return []
            user_id = auth.current_user['id']

        return db.fetch_all(
            """SELECT bi.*, b.title, b.author, b.genre, b.year 
               FROM BookItem bi
               JOIN Book b ON bi.book_id = b.id
               WHERE bi.owner_id = ?
               ORDER BY bi.added_at DESC""",
            (user_id,)
        )

    def get_available_items(self, exclude_user_id=None):
        """
        Получение всех доступных для обмена экземпляров книг

        Args:
            exclude_user_id (int): ID пользователя, чьи книги исключить

        Returns:
            list: Список доступных экземпляров
        """
        query = """
            SELECT bi.*, b.title, b.author, b.genre, b.year, u.username as owner_name
            FROM BookItem bi
            JOIN Book b ON bi.book_id = b.id
            JOIN Users u ON bi.owner_id = u.id
            WHERE bi.status = 'available'
        """
        params = []

        if exclude_user_id:
            query += " AND bi.owner_id != ?"
            params.append(exclude_user_id)

        query += " ORDER BY b.author, b.title"

        return db.fetch_all(query, params)

    def get_item_by_id(self, item_id):
        """
        Получение экземпляра книги по ID

        Args:
            item_id (int): ID экземпляра

        Returns:
            dict: Информация об экземпляре
        """
        return db.fetch_one(
            """SELECT bi.*, b.title, b.author, b.genre, b.year, u.username as owner_name
               FROM BookItem bi
               JOIN Book b ON bi.book_id = b.id
               JOIN Users u ON bi.owner_id = u.id
               WHERE bi.id = ?""",
            (item_id,)
        )

    def update_item_status(self, item_id, status):
        """
        Обновление статуса экземпляра книги

        Args:
            item_id (int): ID экземпляра
            status (str): Новый статус (available, pending, exchanged)

        Returns:
            bool: True если успешно
        """
        valid_statuses = ["available", "pending", "exchanged"]
        if status not in valid_statuses:
            return False

        result = db.execute(
            "UPDATE BookItem SET status = ? WHERE id = ?",
            (status, item_id)
        )
        return result is not None

    def delete_item(self, item_id):
        """
        Удаление экземпляра книги

        Args:
            item_id (int): ID экземпляра

        Returns:
            tuple: (success: bool, message: str)
        """
        if not auth.is_authenticated():
            return False, "Пользователь не авторизован"

        # Проверяем, принадлежит ли экземпляр текущему пользователю
        item = self.get_item_by_id(item_id)
        if not item:
            return False, "Экземпляр не найден"

        if item['owner_id'] != auth.current_user['id']:
            return False, "Вы не можете удалить чужой экземпляр книги"

        # Проверяем, не находится ли экземпляр в процессе обмена
        if item['status'] == 'pending':
            return False, "Нельзя удалить экземпляр, который участвует в активном обмене"

        try:
            result = db.execute("DELETE FROM BookItem WHERE id = ?", (item_id,))
            if result is not None:
                return True, "Экземпляр книги успешно удален"
            else:
                return False, "Ошибка при удалении экземпляра"
        except Exception as e:
            return False, f"Ошибка базы данных: {e}"

    def get_statistics(self):
        """
        Получение статистики для текущего пользователя

        Returns:
            dict: Статистика пользователя
        """
        if not auth.is_authenticated():
            return {}

        user_id = auth.current_user['id']

        # Количество книг пользователя
        my_books = db.fetch_one(
            "SELECT COUNT(*) as count FROM BookItem WHERE owner_id = ?",
            (user_id,)
        )

        # Количество доступных для обмена книг пользователя
        available = db.fetch_one(
            "SELECT COUNT(*) as count FROM BookItem WHERE owner_id = ? AND status = 'available'",
            (user_id,)
        )

        # Количество книг в процессе обмена
        pending = db.fetch_one(
            "SELECT COUNT(*) as count FROM ExchangeRequest WHERE owner_id = ? AND status = 'pending'",
            (user_id,)
        )

        # Количество завершенных обменов
        completed = db.fetch_one(
            """SELECT COUNT(*) as count 
               FROM ExchangeHistory eh
               JOIN ExchangeRequest er ON eh.exchange_req_id = er.id
               WHERE er.owner_id = ? OR er.requester_id = ?""",
            (user_id, user_id)
        )

        return {
            'my_books': my_books['count'] if my_books else 0,
            'available': available['count'] if available else 0,
            'pending': pending['count'] if pending else 0,
            'completed': completed['count'] if completed else 0
        }


# Создаем глобальный экземпляр менеджера книг
book_manager = BookManager()