from database import db
from auth import auth

class BookManager:
    def __init__(self):
        pass

    def add_book(self, title, author, genre=None, year=None, description=None):
        if not title or not author:
            return False, "Название и автор обязательны для заполнения", None

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
        return db.fetch_all(
            "SELECT * FROM Book ORDER BY author, title"
        )

    def get_book_by_id(self, book_id):
        return db.fetch_one("SELECT * FROM Book WHERE id = ?", (book_id,))

    def search_books(self, keyword):
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

    def add_book_item(self, book_id, condition="good"):
        if not auth.is_authenticated():
            return False, "Пользователь не авторизован"

        book = self.get_book_by_id(book_id)
        if not book:
            return False, "Книга не найдена"

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
        return db.fetch_one(
            """SELECT bi.*, b.title, b.author, b.genre, b.year, u.username as owner_name
               FROM BookItem bi
               JOIN Book b ON bi.book_id = b.id
               JOIN Users u ON bi.owner_id = u.id
               WHERE bi.id = ?""",
            (item_id,)
        )

    def update_item_status(self, item_id, status):
        valid_statuses = ["available", "pending", "exchanged"]
        if status not in valid_statuses:
            return False

        result = db.execute(
            "UPDATE BookItem SET status = ? WHERE id = ?",
            (status, item_id)
        )
        return result is not None

    def delete_item(self, item_id):
        if not auth.is_authenticated():
            return False, "Пользователь не авторизован"

        item = self.get_item_by_id(item_id)
        if not item:
            return False, "Экземпляр не найден"

        if item['owner_id'] != auth.current_user['id']:
            return False, "Вы не можете удалить чужой экземпляр книги"

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
        if not auth.is_authenticated():
            return {}

        user_id = auth.current_user['id']

        my_books = db.fetch_one(
            "SELECT COUNT(*) as count FROM BookItem WHERE owner_id = ?",
            (user_id,)
        )

        available = db.fetch_one(
            "SELECT COUNT(*) as count FROM BookItem WHERE owner_id = ? AND status = 'available'",
            (user_id,)
        )

        pending = db.fetch_one(
            "SELECT COUNT(*) as count FROM ExchangeRequest WHERE owner_id = ? AND status = 'pending'",
            (user_id,)
        )

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

book_manager = BookManager()