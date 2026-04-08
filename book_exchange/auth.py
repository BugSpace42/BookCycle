from database import db
from utils import hash_password, verify_password, validate_email, validate_username, validate_password, validate_phone


class AuthManager:

    def __init__(self):
        self.current_user = None  # Хранит информацию о текущем пользователе

    def register(self, username, email, password, phone=""):
        if not username or not email or not password:
            return False, "Все поля, кроме телефона, обязательны для заполнения"

        if not validate_username(username):
            return False, "Имя пользователя должно содержать 3-20 символов (буквы, цифры, _)"

        if not validate_email(email):
            return False, "Введите корректный email адрес"

        password_valid, password_msg = validate_password(password)
        if not password_valid:
            return False, password_msg

        if phone and not validate_phone(phone):
            return False, "Введите корректный номер телефона"

        existing_user = db.fetch_one(
            "SELECT id FROM Users WHERE username = ? OR email = ?",
            (username, email)
        )

        if existing_user:
            return False, "Пользователь с таким именем или email уже существует"

        password_hash = hash_password(password)
        user_id = db.execute(
            "INSERT INTO Users (username, email, password_hash, phone) VALUES (?, ?, ?, ?)",
            (username, email, password_hash, phone)
        )

        if user_id:
            return True, "Регистрация успешно завершена!"
        else:
            return False, "Ошибка при регистрации. Попробуйте позже."

    def login(self, username, password):
        if not username or not password:
            return False, "Введите имя пользователя и пароль"

        user = db.fetch_one(
            "SELECT * FROM Users WHERE username = ? OR email = ?",
            (username, username)
        )

        if not user:
            return False, "Пользователь не найден"

        if not verify_password(password, user['password_hash']):
            return False, "Неверный пароль"

        self.current_user = dict(user)
        self.current_user.pop('password_hash', None)

        return True, f"Добро пожаловать, {self.current_user['username']}!"

    def logout(self):
        self.current_user = None
        return True, "Вы вышли из системы"

    def get_current_user(self):
        return self.current_user

    def is_authenticated(self):
        return self.current_user is not None

    def update_profile(self, phone=None, email=None):
        if not self.is_authenticated():
            return False, "Пользователь не авторизован"

        updates = []
        params = []

        if email:
            if not validate_email(email):
                return False, "Введите корректный email"

            existing = db.fetch_one(
                "SELECT id FROM Users WHERE email = ? AND id != ?",
                (email, self.current_user['id'])
            )
            if existing:
                return False, "Этот email уже используется другим пользователем"

            updates.append("email = ?")
            params.append(email)
            self.current_user['email'] = email

        if phone:
            if not validate_phone(phone):
                return False, "Введите корректный номер телефона"
            updates.append("phone = ?")
            params.append(phone)
            self.current_user['phone'] = phone

        if not updates:
            return False, "Нет данных для обновления"

        params.append(self.current_user['id'])
        query = f"UPDATE Users SET {', '.join(updates)} WHERE id = ?"

        success = db.execute(query, params)
        if success is not None:
            return True, "Профиль успешно обновлен!"
        else:
            return False, "Ошибка при обновлении профиля"

auth = AuthManager()