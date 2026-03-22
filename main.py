"""
Модуль main.py
Точка входа в приложение. Содержит тестовый графический интерфейс
для проверки работы модулей аутентификации и базы данных.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from database import db
from auth import auth
from utils import hash_password, verify_password


class LoginWindow:
    """Окно авторизации"""

    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Книгообмен - Вход в систему")
        self.window.geometry("400x350")
        self.window.resizable(False, False)

        # Центрируем окно
        self.window.eval('tk::PlaceWindow . center')

        self.setup_ui()

    def setup_ui(self):
        """Настройка интерфейса"""
        # Заголовок
        title_label = tk.Label(
            self.window,
            text="Добро пожаловать!",
            font=("Arial", 18, "bold")
        )
        title_label.pack(pady=20)

        # Фрейм для формы
        form_frame = ttk.Frame(self.window, padding="20")
        form_frame.pack(fill="both", expand=True)

        # Поле для логина
        ttk.Label(form_frame, text="Имя пользователя или Email:", font=("Arial", 10)).grid(
            row=0, column=0, sticky="w", pady=5
        )
        self.username_entry = ttk.Entry(form_frame, width=30)
        self.username_entry.grid(row=1, column=0, pady=(0, 15))
        self.username_entry.focus()

        # Поле для пароля
        ttk.Label(form_frame, text="Пароль:", font=("Arial", 10)).grid(
            row=2, column=0, sticky="w", pady=5
        )
        self.password_entry = ttk.Entry(form_frame, width=30, show="*")
        self.password_entry.grid(row=3, column=0, pady=(0, 20))

        # Кнопка входа
        login_btn = ttk.Button(
            form_frame,
            text="Войти",
            command=self.login,
            width=25
        )
        login_btn.grid(row=4, column=0, pady=5)

        # Кнопка регистрации
        register_btn = ttk.Button(
            form_frame,
            text="Зарегистрироваться",
            command=self.open_register,
            width=25
        )
        register_btn.grid(row=5, column=0, pady=5)

        # Привязываем Enter к кнопке входа
        self.window.bind('<Return>', lambda e: self.login())

    def login(self):
        """Обработка входа"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()

        success, message = auth.login(username, password)

        if success:
            messagebox.showinfo("Успех", message)
            self.window.destroy()
            MainWindow().run()
        else:
            messagebox.showerror("Ошибка", message)

    def open_register(self):
        """Открытие окна регистрации"""
        RegisterWindow(self.window)

    def run(self):
        """Запуск окна"""
        self.window.mainloop()


class RegisterWindow:
    """Окно регистрации"""

    def __init__(self, parent):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("Книгообмен - Регистрация")
        self.window.geometry("400x500")
        self.window.resizable(False, False)

        # Делаем окно модальным
        self.window.transient(parent)
        self.window.grab_set()

        self.setup_ui()

    def setup_ui(self):
        """Настройка интерфейса"""
        # Заголовок
        title_label = tk.Label(
            self.window,
            text="Регистрация нового пользователя",
            font=("Arial", 14, "bold")
        )
        title_label.pack(pady=20)

        # Фрейм для формы
        form_frame = ttk.Frame(self.window, padding="20")
        form_frame.pack(fill="both", expand=True)

        # Имя пользователя
        ttk.Label(form_frame, text="Имя пользователя:*", font=("Arial", 10)).grid(
            row=0, column=0, sticky="w", pady=5
        )
        self.username_entry = ttk.Entry(form_frame, width=30)
        self.username_entry.grid(row=1, column=0, pady=(0, 10))

        # Email
        ttk.Label(form_frame, text="Email:*", font=("Arial", 10)).grid(
            row=2, column=0, sticky="w", pady=5
        )
        self.email_entry = ttk.Entry(form_frame, width=30)
        self.email_entry.grid(row=3, column=0, pady=(0, 10))

        # Пароль
        ttk.Label(form_frame, text="Пароль:*", font=("Arial", 10)).grid(
            row=4, column=0, sticky="w", pady=5
        )
        self.password_entry = ttk.Entry(form_frame, width=30, show="*")
        self.password_entry.grid(row=5, column=0, pady=(0, 5))

        # Подсказка по паролю
        hint_label = tk.Label(
            form_frame,
            text="Минимум 6 символов, заглавная буква, строчная буква, цифра",
            font=("Arial", 8),
            fg="gray"
        )
        hint_label.grid(row=6, column=0, pady=(0, 10))

        # Подтверждение пароля
        ttk.Label(form_frame, text="Подтверждение пароля:*", font=("Arial", 10)).grid(
            row=7, column=0, sticky="w", pady=5
        )
        self.confirm_entry = ttk.Entry(form_frame, width=30, show="*")
        self.confirm_entry.grid(row=8, column=0, pady=(0, 10))

        # Телефон
        ttk.Label(form_frame, text="Телефон (необязательно):", font=("Arial", 10)).grid(
            row=9, column=0, sticky="w", pady=5
        )
        self.phone_entry = ttk.Entry(form_frame, width=30)
        self.phone_entry.grid(row=10, column=0, pady=(0, 20))

        # Кнопка регистрации
        register_btn = ttk.Button(
            form_frame,
            text="Зарегистрироваться",
            command=self.register,
            width=25
        )
        register_btn.grid(row=11, column=0, pady=5)

        # Привязываем Enter к кнопке регистрации
        self.window.bind('<Return>', lambda e: self.register())

    def register(self):
        """Обработка регистрации"""
        username = self.username_entry.get().strip()
        email = self.email_entry.get().strip()
        password = self.password_entry.get()
        confirm = self.confirm_entry.get()
        phone = self.phone_entry.get().strip()

        # Проверка совпадения паролей
        if password != confirm:
            messagebox.showerror("Ошибка", "Пароли не совпадают")
            return

        success, message = auth.register(username, email, password, phone)

        if success:
            messagebox.showinfo("Успех", message)
            self.window.destroy()
        else:
            messagebox.showerror("Ошибка", message)


class MainWindow:
    """Главное окно приложения (после входа)"""

    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Книгообмен - Главное окно")
        self.window.geometry("600x400")

        self.setup_ui()

    def setup_ui(self):
        """Настройка интерфейса"""
        # Приветствие
        user = auth.get_current_user()
        if user:
            welcome_label = tk.Label(
                self.window,
                text=f"Здравствуйте, {user['username']}!",
                font=("Arial", 14)
            )
            welcome_label.pack(pady=20)

        # Информация о пользователе
        info_frame = ttk.LabelFrame(self.window, text="Информация о пользователе", padding="10")
        info_frame.pack(fill="x", padx=20, pady=10)

        if user:
            ttk.Label(info_frame, text=f"Email: {user['email']}").grid(row=0, column=0, sticky="w", pady=2)
            ttk.Label(info_frame, text=f"Телефон: {user.get('phone', 'не указан')}").grid(row=1, column=0, sticky="w",
                                                                                          pady=2)
            ttk.Label(info_frame, text=f"Дата регистрации: {user['created_at']}").grid(row=2, column=0, sticky="w",
                                                                                       pady=2)

        # Кнопки действий
        btn_frame = ttk.Frame(self.window)
        btn_frame.pack(pady=20)

        ttk.Button(btn_frame, text="Мои книги", command=self.show_books, width=20).pack(pady=5)
        ttk.Button(btn_frame, text="Каталог книг", command=self.show_catalog, width=20).pack(pady=5)
        ttk.Button(btn_frame, text="Запросы на обмен", command=self.show_requests, width=20).pack(pady=5)
        ttk.Button(btn_frame, text="История обменов", command=self.show_history, width=20).pack(pady=5)
        ttk.Button(btn_frame, text="Выйти", command=self.logout, width=20).pack(pady=5)

    def show_books(self):
        """Показать мои книги (заглушка)"""
        messagebox.showinfo("Информация", "Функция 'Мои книги' будет реализована позже")

    def show_catalog(self):
        """Показать каталог книг (заглушка)"""
        messagebox.showinfo("Информация", "Функция 'Каталог книг' будет реализована позже")

    def show_requests(self):
        """Показать запросы (заглушка)"""
        messagebox.showinfo("Информация", "Функция 'Запросы на обмен' будет реализована позже")

    def show_history(self):
        """Показать историю (заглушка)"""
        messagebox.showinfo("Информация", "Функция 'История обменов' будет реализована позже")

    def logout(self):
        """Выход из системы"""
        success, message = auth.logout()
        if success:
            messagebox.showinfo("Успех", message)
            self.window.destroy()
            LoginWindow().run()

    def run(self):
        """Запуск главного окна"""
        self.window.mainloop()


def main():
    """Точка входа в приложение"""
    # Проверяем, что база данных инициализирована
    print("Запуск приложения 'Книгообмен'...")
    print("Проверка базы данных...")

    # Небольшой тест: создаем тестового пользователя, если его нет
    test_user = db.fetch_one("SELECT * FROM Users WHERE username = 'test'")
    if not test_user:
        test_hash = hash_password("Test123")
        db.execute(
            "INSERT INTO Users (username, email, password_hash) VALUES (?, ?, ?)",
            ("test", "test@example.com", test_hash)
        )
        print("Создан тестовый пользователь: test / Test123")

    # Запускаем окно входа
    LoginWindow().run()


if __name__ == "__main__":
    main()