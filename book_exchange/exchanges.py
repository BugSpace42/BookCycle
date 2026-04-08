from database import db
from auth import auth
from books import book_manager

class ExchangeManager:
    def __init__(self):
        pass

    def create_request(self, book_item_id):
        if not auth.is_authenticated():
            return False, "Пользователь не авторизован"

        item = book_manager.get_item_by_id(book_item_id)
        if not item:
            return False, "Книга не найдена"

        if item['status'] != 'available':
            return False, "Эта книга уже недоступна для обмена"

        if item['owner_id'] == auth.current_user['id']:
            return False, "Вы не можете запросить свою собственную книгу"

        existing_request = db.fetch_one(
            """SELECT id, status FROM ExchangeRequest 
               WHERE book_item_id = ? AND requester_id = ? AND status = 'pending'""",
            (book_item_id, auth.current_user['id'])
        )

        if existing_request:
            return False, "Вы уже отправили запрос на эту книгу и ожидаете ответа"

        try:
            request_id = db.execute(
                """INSERT INTO ExchangeRequest (book_item_id, requester_id, owner_id, status) 
                   VALUES (?, ?, ?, 'pending')""",
                (book_item_id, auth.current_user['id'], item['owner_id'])
            )

            if request_id:
                book_manager.update_item_status(book_item_id, 'pending')
                return True, f"Запрос на книгу '{item['title']}' успешно отправлен владельцу"
            else:
                return False, "Ошибка при создании запроса"
        except Exception as e:
            return False, f"Ошибка базы данных: {e}"

    def get_incoming_requests(self):
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
        if not auth.is_authenticated():
            return False, "Пользователь не авторизован"

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

        if request['owner_id'] != auth.current_user['id']:
            return False, "Вы не можете ответить на этот запрос"

        if request['status'] != 'pending':
            return False, "Этот запрос уже был обработан"

        item = book_manager.get_item_by_id(request['book_item_id'])
        if accept and item['status'] != 'pending':
            return False, "Книга больше недоступна для обмена"

        try:
            if accept:
                db.execute(
                    """UPDATE ExchangeRequest 
                       SET status = 'accepted', responded_at = CURRENT_TIMESTAMP
                       WHERE id = ?""",
                    (request_id,)
                )

                book_manager.update_item_status(request['book_item_id'], 'exchanged')

                db.execute(
                    """INSERT INTO ExchangeHistory (exchange_req_id) 
                       VALUES (?)""",
                    (request_id,)
                )

                return True, f"Запрос на книгу '{request['title']}' принят! Свяжитесь с пользователем для передачи книги."
            else:
                db.execute(
                    """UPDATE ExchangeRequest 
                       SET status = 'rejected', responded_at = CURRENT_TIMESTAMP
                       WHERE id = ?""",
                    (request_id,)
                )

                book_manager.update_item_status(request['book_item_id'], 'available')

                return True, f"Запрос на книгу '{request['title']}' отклонен"
        except Exception as e:
            return False, f"Ошибка базы данных: {e}"

    def cancel_request(self, request_id):
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
            db.execute("DELETE FROM ExchangeRequest WHERE id = ?", (request_id,))

            book_manager.update_item_status(request['book_item_id'], 'available')

            return True, f"Запрос на книгу '{request['title']}' успешно отменен"
        except Exception as e:
            return False, f"Ошибка базы данных: {e}"

    def get_history(self):
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
        if not auth.is_authenticated():
            return {}

        user_id = auth.current_user['id']

        received = db.fetch_one(
            "SELECT COUNT(*) as count FROM ExchangeRequest WHERE owner_id = ? AND status = 'pending'",
            (user_id,)
        )

        sent = db.fetch_one(
            "SELECT COUNT(*) as count FROM ExchangeRequest WHERE requester_id = ? AND status = 'pending'",
            (user_id,)
        )

        accepted = db.fetch_one(
            """SELECT COUNT(*) as count 
               FROM ExchangeRequest 
               WHERE (owner_id = ? OR requester_id = ?) AND status = 'accepted'""",
            (user_id, user_id)
        )

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

exchange_manager = ExchangeManager()