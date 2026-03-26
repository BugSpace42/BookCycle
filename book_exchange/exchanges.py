"""
Модуль exchanges.py
Управление обменами: создание запросов, обработка, история
"""

from database import db
from auth import auth
from books import book_manager
from datetime import datetime


class ExchangeManager:
    """Класс для управления обменами книгами"""

    def __init__(self):
        """Инициализация менеджера обменов"""
        pass

    def create_request(self, book_item_id):
        """
        Создание запроса на обмен

        Args:
            book_item_id (int): ID экземпляра книги, которую хотят получить

        Returns:
            tuple: (success: bool, message: str)
        """
        if not auth.is_authenticated():
            return False, "Пользователь не авторизован"

        # Получаем информацию об экземпляре
        item = book_manager.get_item_by_id(book_item_id)
        if not item:
            return False, "Книга не найдена"

        # Проверяем, что книга доступна
        if item['status'] != 'available':
            return False, "Эта книга уже недоступна для обмена"

        # Проверяем, что пользователь не пытается запросить свою книгу
        if item['owner_id'] == auth.current_user['id']:
            return False, "Вы не можете запросить свою собственную книгу"

        # Проверяем, нет ли уже активного запроса на эту книгу от этого пользователя
        existing_request = db.fetch_one(
            """SELECT id, status FROM ExchangeRequest 
               WHERE book_item_id = ? AND requester_id = ? AND status = 'pending'""",
            (book_item_id, auth.current_user['id'])
        )

        if existing_request:
            return False, "Вы уже отправили запрос на эту книгу и ожидаете ответа"

        # Создаем запрос
        try:
            request_id = db.execute(
                """INSERT INTO ExchangeRequest (book_item_id, requester_id, owner_id, status) 
                   VALUES (?, ?, ?, 'pending')""",
                (book_item_id, auth.current_user['id'], item['owner_id'])
            )

            if request_id:
                # Меняем статус книги на "ожидает обмена"
                book_manager.update_item_status(book_item_id, 'pending')
                return True, f"Запрос на книгу '{item['title']}' успешно отправлен владельцу"
            else:
                return False, "Ошибка при создании запроса"
        except Exception as e:
            return False, f"Ошибка базы данных: {e}"

    def get_incoming_requests(self):
        """
        Получение входящих запросов на обмен (для текущего пользователя)

        Returns:
            list: Список входящих запросов с информацией о книге и запрашивающем
        """
        if not auth.is_authenticated():
            return []

        return db.fetch_all(
            """SELECT er.*, 
                      b.title, b.author, b.genre, b.year,
                      u.username as requester_name,
                      u.email as requester_email,
                      u.phone as requester_phone,
                      bi.condition as book_condition
               FROM ExchangeRequest er
               JOIN BookItem bi ON er.book_item_id = bi.id
               JOIN Book b ON bi.book_id = b.id
               JOIN Users u ON er.requester_id = u.id
               WHERE er.owner_id = ? AND er.status = 'pending'
               ORDER BY er.requested_at DESC""",
            (auth.current_user['id'],)
        )

    def get_outgoing_requests(self):
        """
        Получение исходящих запросов на обмен (от текущего пользователя)

        Returns:
            list: Список исходящих запросов с информацией о книге и владельце
        """
        if not auth.is_authenticated():
            return []

        return db.fetch_all(
            """SELECT er.*, 
                      b.title, b.author, b.genre, b.year,
                      u.username as owner_name,
                      bi.condition as book_condition
               FROM ExchangeRequest er
               JOIN BookItem bi ON er.book_item_id = bi.id
               JOIN Book b ON bi.book_id = b.id
               JOIN Users u ON er.owner_id = u.id
               WHERE er.requester_id = ? AND er.status = 'pending'
               ORDER BY er.requested_at DESC""",
            (auth.current_user['id'],)
        )

    def respond_to_request(self, request_id, accept):
        """
        Ответ на запрос обмена (принять или отклонить)

        Args:
            request_id (int): ID запроса
            accept (bool): True - принять, False - отклонить

        Returns:
            tuple: (success: bool, message: str)
        """
        if not auth.is_authenticated():
            return False, "Пользователь не авторизован"

        # Получаем информацию о запросе
        request = db.fetch_one(
            """SELECT er.*, bi.book_id, b.title, bi.owner_id
               FROM ExchangeRequest er
               JOIN BookItem bi ON er.book_item_id = bi.id
               JOIN Book b ON bi.book_id = b.id
               WHERE er.id = ?""",
            (request_id,)
        )

        if not request:
            return False, "Запрос не найден"

        # Проверяем, что запрос адресован текущему пользователю
        if request['owner_id'] != auth.current_user['id']:
            return False, "Вы не можете ответить на этот запрос"

        # Проверяем, что запрос еще в статусе pending
        if request['status'] != 'pending':
            return False, "Этот запрос уже был обработан"

        # Проверяем, что книга все еще доступна
        item = book_manager.get_item_by_id(request['book_item_id'])
        if accept and item['status'] != 'pending':
            return False, "Книга больше недоступна для обмена"

        try:
            if accept:
                # Принимаем запрос
                db.execute(
                    """UPDATE ExchangeRequest 
                       SET status = 'accepted', responded_at = CURRENT_TIMESTAMP
                       WHERE id = ?""",
                    (request_id,)
                )

                # Меняем статус книги на "обменена"
                book_manager.update_item_status(request['book_item_id'], 'exchanged')

                # Добавляем в историю обменов
                db.execute(
                    """INSERT INTO ExchangeHistory (exchange_req_id) 
                       VALUES (?)""",
                    (request_id,)
                )

                return True, f"Запрос на книгу '{request['title']}' принят! Свяжитесь с пользователем для передачи книги."
            else:
                # Отклоняем запрос
                db.execute(
                    """UPDATE ExchangeRequest 
                       SET status = 'rejected', responded_at = CURRENT_TIMESTAMP
                       WHERE id = ?""",
                    (request_id,)
                )

                # Возвращаем книге статус "доступна"
                book_manager.update_item_status(request['book_item_id'], 'available')

                return True, f"Запрос на книгу '{request['title']}' отклонен"
        except Exception as e:
            return False, f"Ошибка базы данных: {e}"

    def cancel_request(self, request_id):
        """
        Отмена исходящего запроса на обмен

        Args:
            request_id (int): ID запроса

        Returns:
            tuple: (success: bool, message: str)
        """
        if not auth.is_authenticated():
            return False, "Пользователь не авторизован"

        # Получаем информацию о запросе
        request = db.fetch_one(
            """SELECT er.*, bi.book_id, b.title
               FROM ExchangeRequest er
               JOIN BookItem bi ON er.book_item_id = bi.id
               JOIN Book b ON bi.book_id = b.id
               WHERE er.id = ? AND er.requester_id = ?""",
            (request_id, auth.current_user['id'])
        )

        if not request:
            return False, "Запрос не найден или вы не являетесь его автором"

        if request['status'] != 'pending':
            return False, "Нельзя отменить уже обработанный запрос"

        try:
            # Удаляем запрос
            db.execute("DELETE FROM ExchangeRequest WHERE id = ?", (request_id,))

            # Возвращаем книге статус "доступна"
            book_manager.update_item_status(request['book_item_id'], 'available')

            return True, f"Запрос на книгу '{request['title']}' успешно отменен"
        except Exception as e:
            return False, f"Ошибка базы данных: {e}"

    def get_history(self):
        """
        Получение истории обменов для текущего пользователя

        Returns:
            list: Список завершенных обменов
        """
        if not auth.is_authenticated():
            return []

        user_id = auth.current_user['id']

        return db.fetch_all(
            """SELECT eh.*, 
                      er.requested_at, er.responded_at,
                      b.title, b.author, b.genre,
                      CASE 
                          WHEN er.requester_id = ? THEN 'Исходящий'
                          ELSE 'Входящий'
                      END as direction,
                      CASE 
                          WHEN er.requester_id = ? THEN u_owner.username
                          ELSE u_requester.username
                      END as other_user,
                      CASE 
                          WHEN er.requester_id = ? THEN u_owner.email
                          ELSE u_requester.email
                      END as other_email,
                      bi.condition as book_condition
               FROM ExchangeHistory eh
               JOIN ExchangeRequest er ON eh.exchange_req_id = er.id
               JOIN BookItem bi ON er.book_item_id = bi.id
               JOIN Book b ON bi.book_id = b.id
               JOIN Users u_owner ON er.owner_id = u_owner.id
               JOIN Users u_requester ON er.requester_id = u_requester.id
               WHERE er.owner_id = ? OR er.requester_id = ?
               ORDER BY eh.completed_at DESC""",
            (user_id, user_id, user_id, user_id, user_id)
        )

    def get_request_details(self, request_id):
        """
        Получение детальной информации о запросе

        Args:
            request_id (int): ID запроса

        Returns:
            dict: Детальная информация о запросе
        """
        return db.fetch_one(
            """SELECT er.*, 
                      b.title, b.author, b.genre, b.year, b.description,
                      u_requester.username as requester_name, 
                      u_requester.email as requester_email,
                      u_requester.phone as requester_phone,
                      u_owner.username as owner_name,
                      u_owner.email as owner_email,
                      u_owner.phone as owner_phone,
                      bi.condition as book_condition
               FROM ExchangeRequest er
               JOIN BookItem bi ON er.book_item_id = bi.id
               JOIN Book b ON bi.book_id = b.id
               JOIN Users u_requester ON er.requester_id = u_requester.id
               JOIN Users u_owner ON er.owner_id = u_owner.id
               WHERE er.id = ?""",
            (request_id,)
        )

    def get_statistics(self):
        """
        Получение статистики по обменам для текущего пользователя

        Returns:
            dict: Статистика обменов
        """
        if not auth.is_authenticated():
            return {}

        user_id = auth.current_user['id']

        # Полученные запросы (мне предлагают)
        received = db.fetch_one(
            "SELECT COUNT(*) as count FROM ExchangeRequest WHERE owner_id = ? AND status = 'pending'",
            (user_id,)
        )

        # Отправленные запросы (я предлагаю)
        sent = db.fetch_one(
            "SELECT COUNT(*) as count FROM ExchangeRequest WHERE requester_id = ? AND status = 'pending'",
            (user_id,)
        )

        # Принятые запросы
        accepted = db.fetch_one(
            """SELECT COUNT(*) as count 
               FROM ExchangeRequest 
               WHERE (owner_id = ? OR requester_id = ?) AND status = 'accepted'""",
            (user_id, user_id)
        )

        # Отклоненные запросы
        rejected = db.fetch_one(
            """SELECT COUNT(*) as count 
               FROM ExchangeRequest 
               WHERE (owner_id = ? OR requester_id = ?) AND status = 'rejected'""",
            (user_id, user_id)
        )

        return {
            'received_pending': received['count'] if received else 0,
            'sent_pending': sent['count'] if sent else 0,
            'accepted': accepted['count'] if accepted else 0,
            'rejected': rejected['count'] if rejected else 0
        }


# Создаем глобальный экземпляр менеджера обменов
exchange_manager = ExchangeManager()