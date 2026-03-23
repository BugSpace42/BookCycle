"""
Модуль main.py
Точка входа в приложение. Полная версия с функцией обмена книгами.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from database import db
from auth import auth
from books import book_manager
from exchanges import exchange_manager
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
    """Главное окно приложения"""

    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Книгообмен - Главное окно")
        self.window.geometry("1000x700")

        # Создаем вкладки
        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.setup_tabs()

    def setup_tabs(self):
        """Настройка вкладок"""
        # Вкладка "Каталог книг"
        self.catalog_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.catalog_tab, text="📚 Каталог книг")
        self.setup_catalog_tab()

        # Вкладка "Мои книги"
        self.my_books_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.my_books_tab, text="📖 Мои книги")
        self.setup_my_books_tab()

        # Вкладка "Входящие запросы"
        self.incoming_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.incoming_tab, text="📩 Входящие запросы")
        self.setup_incoming_tab()

        # Вкладка "Исходящие запросы"
        self.outgoing_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.outgoing_tab, text="📤 Исходящие запросы")
        self.setup_outgoing_tab()

        # Вкладка "История обменов"
        self.history_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.history_tab, text="📜 История обменов")
        self.setup_history_tab()

        # Вкладка "Добавить книгу"
        self.add_book_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.add_book_tab, text="➕ Добавить книгу")
        self.setup_add_book_tab()

        # Вкладка "Статистика"
        self.stats_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.stats_tab, text="📊 Статистика")
        self.setup_stats_tab()

        # Вкладка "Профиль"
        self.profile_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.profile_tab, text="👤 Профиль")
        self.setup_profile_tab()

    def setup_catalog_tab(self):
        """Настройка вкладки каталога книг"""
        # Верхняя панель с поиском
        search_frame = ttk.Frame(self.catalog_tab)
        search_frame.pack(fill="x", padx=10, pady=10)

        ttk.Label(search_frame, text="Поиск:").pack(side="left", padx=5)
        self.search_entry = ttk.Entry(search_frame, width=30)
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind('<KeyRelease>', lambda e: self.search_books())

        ttk.Button(search_frame, text="Очистить", command=self.clear_search).pack(side="left", padx=5)

        # Таблица с книгами
        columns = ("id", "title", "author", "genre", "year", "owner", "condition", "status")
        self.catalog_tree = ttk.Treeview(self.catalog_tab, columns=columns, show="headings", height=20)

        self.catalog_tree.heading("id", text="ID")
        self.catalog_tree.heading("title", text="Название")
        self.catalog_tree.heading("author", text="Автор")
        self.catalog_tree.heading("genre", text="Жанр")
        self.catalog_tree.heading("year", text="Год")
        self.catalog_tree.heading("owner", text="Владелец")
        self.catalog_tree.heading("condition", text="Состояние")
        self.catalog_tree.heading("status", text="Статус")

        self.catalog_tree.column("id", width=50)
        self.catalog_tree.column("title", width=200)
        self.catalog_tree.column("author", width=150)
        self.catalog_tree.column("genre", width=100)
        self.catalog_tree.column("year", width=60)
        self.catalog_tree.column("owner", width=120)
        self.catalog_tree.column("condition", width=80)
        self.catalog_tree.column("status", width=80)

        scrollbar = ttk.Scrollbar(self.catalog_tab, orient="vertical", command=self.catalog_tree.yview)
        self.catalog_tree.configure(yscrollcommand=scrollbar.set)

        self.catalog_tree.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side="right", fill="y", padx=(0, 10), pady=10)

        # Кнопка запроса на обмен
        btn_frame = ttk.Frame(self.catalog_tab)
        btn_frame.pack(fill="x", padx=10, pady=5)

        ttk.Button(btn_frame, text="📩 Запросить обмен", command=self.request_exchange).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="🔄 Обновить", command=self.load_catalog).pack(side="left", padx=5)

        # Загружаем данные
        self.load_catalog()

    def setup_my_books_tab(self):
        """Настройка вкладки моих книг"""
        # Таблица с моими книгами
        columns = ("id", "title", "author", "condition", "status", "added_at")
        self.my_books_tree = ttk.Treeview(self.my_books_tab, columns=columns, show="headings", height=20)

        self.my_books_tree.heading("id", text="ID")
        self.my_books_tree.heading("title", text="Название")
        self.my_books_tree.heading("author", text="Автор")
        self.my_books_tree.heading("condition", text="Состояние")
        self.my_books_tree.heading("status", text="Статус")
        self.my_books_tree.heading("added_at", text="Дата добавления")

        self.my_books_tree.column("id", width=50)
        self.my_books_tree.column("title", width=250)
        self.my_books_tree.column("author", width=150)
        self.my_books_tree.column("condition", width=80)
        self.my_books_tree.column("status", width=80)
        self.my_books_tree.column("added_at", width=150)

        scrollbar = ttk.Scrollbar(self.my_books_tab, orient="vertical", command=self.my_books_tree.yview)
        self.my_books_tree.configure(yscrollcommand=scrollbar.set)

        self.my_books_tree.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side="right", fill="y", padx=(0, 10), pady=10)

        # Кнопки управления
        btn_frame = ttk.Frame(self.my_books_tab)
        btn_frame.pack(fill="x", padx=10, pady=5)

        ttk.Button(btn_frame, text="🗑️ Удалить", command=self.delete_my_book).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="🔄 Обновить", command=self.load_my_books).pack(side="left", padx=5)

        # Загружаем данные
        self.load_my_books()

    def setup_incoming_tab(self):
        """Настройка вкладки входящих запросов"""
        # Таблица с входящими запросами
        columns = ("id", "book", "author", "requester", "requested_at")
        self.incoming_tree = ttk.Treeview(self.incoming_tab, columns=columns, show="headings", height=15)

        self.incoming_tree.heading("id", text="ID")
        self.incoming_tree.heading("book", text="Книга")
        self.incoming_tree.heading("author", text="Автор")
        self.incoming_tree.heading("requester", text="Запрашивает")
        self.incoming_tree.heading("requested_at", text="Дата запроса")

        self.incoming_tree.column("id", width=50)
        self.incoming_tree.column("book", width=250)
        self.incoming_tree.column("author", width=150)
        self.incoming_tree.column("requester", width=120)
        self.incoming_tree.column("requested_at", width=150)

        scrollbar = ttk.Scrollbar(self.incoming_tab, orient="vertical", command=self.incoming_tree.yview)
        self.incoming_tree.configure(yscrollcommand=scrollbar.set)

        self.incoming_tree.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side="right", fill="y", padx=(0, 10), pady=10)

        # Кнопки управления
        btn_frame = ttk.Frame(self.incoming_tab)
        btn_frame.pack(fill="x", padx=10, pady=5)

        ttk.Button(btn_frame, text="✅ Принять", command=self.accept_request).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="❌ Отклонить", command=self.reject_request).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="🔄 Обновить", command=self.load_incoming).pack(side="left", padx=5)

        # Загружаем данные
        self.load_incoming()

    def setup_outgoing_tab(self):
        """Настройка вкладки исходящих запросов"""
        # Таблица с исходящими запросами
        columns = ("id", "book", "author", "owner", "requested_at")
        self.outgoing_tree = ttk.Treeview(self.outgoing_tab, columns=columns, show="headings", height=15)

        self.outgoing_tree.heading("id", text="ID")
        self.outgoing_tree.heading("book", text="Книга")
        self.outgoing_tree.heading("author", text="Автор")
        self.outgoing_tree.heading("owner", text="Владелец")
        self.outgoing_tree.heading("requested_at", text="Дата запроса")

        self.outgoing_tree.column("id", width=50)
        self.outgoing_tree.column("book", width=250)
        self.outgoing_tree.column("author", width=150)
        self.outgoing_tree.column("owner", width=120)
        self.outgoing_tree.column("requested_at", width=150)

        scrollbar = ttk.Scrollbar(self.outgoing_tab, orient="vertical", command=self.outgoing_tree.yview)
        self.outgoing_tree.configure(yscrollcommand=scrollbar.set)

        self.outgoing_tree.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side="right", fill="y", padx=(0, 10), pady=10)

        # Кнопки управления
        btn_frame = ttk.Frame(self.outgoing_tab)
        btn_frame.pack(fill="x", padx=10, pady=5)

        ttk.Button(btn_frame, text="❌ Отменить запрос", command=self.cancel_request).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="🔄 Обновить", command=self.load_outgoing).pack(side="left", padx=5)

        # Загружаем данные
        self.load_outgoing()

    def setup_history_tab(self):
        """Настройка вкладки истории обменов"""
        # Таблица с историей
        columns = ("id", "direction", "book", "author", "other_user", "completed_at")
        self.history_tree = ttk.Treeview(self.history_tab, columns=columns, show="headings", height=20)

        self.history_tree.heading("id", text="ID")
        self.history_tree.heading("direction", text="Тип")
        self.history_tree.heading("book", text="Книга")
        self.history_tree.heading("author", text="Автор")
        self.history_tree.heading("other_user", text="С кем")
        self.history_tree.heading("completed_at", text="Дата завершения")

        self.history_tree.column("id", width=50)
        self.history_tree.column("direction", width=80)
        self.history_tree.column("book", width=250)
        self.history_tree.column("author", width=150)
        self.history_tree.column("other_user", width=150)
        self.history_tree.column("completed_at", width=150)

        scrollbar = ttk.Scrollbar(self.history_tab, orient="vertical", command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)

        self.history_tree.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side="right", fill="y", padx=(0, 10), pady=10)

        # Кнопки управления
        btn_frame = ttk.Frame(self.history_tab)
        btn_frame.pack(fill="x", padx=10, pady=5)

        ttk.Button(btn_frame, text="🔄 Обновить", command=self.load_history).pack(side="left", padx=5)

        # Загружаем данные
        self.load_history()

    def setup_add_book_tab(self):
        """Настройка вкладки добавления книги"""
        # Фрейм для формы
        form_frame = ttk.LabelFrame(self.add_book_tab, text="Информация о книге", padding="20")
        form_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Название
        ttk.Label(form_frame, text="Название:*").grid(row=0, column=0, sticky="w", pady=5, padx=5)
        self.title_entry = ttk.Entry(form_frame, width=40)
        self.title_entry.grid(row=0, column=1, pady=5, padx=5)

        # Автор
        ttk.Label(form_frame, text="Автор:*").grid(row=1, column=0, sticky="w", pady=5, padx=5)
        self.author_entry = ttk.Entry(form_frame, width=40)
        self.author_entry.grid(row=1, column=1, pady=5, padx=5)

        # Жанр
        ttk.Label(form_frame, text="Жанр:").grid(row=2, column=0, sticky="w", pady=5, padx=5)
        genres = ["Роман", "Детектив", "Фантастика", "Фэнтези", "Поэзия", "Драма", "Комедия", "Наука", "Учебник", "Другое"]
        self.genre_combo = ttk.Combobox(form_frame, values=genres, width=37)
        self.genre_combo.grid(row=2, column=1, pady=5, padx=5)

        # Год
        ttk.Label(form_frame, text="Год издания:").grid(row=3, column=0, sticky="w", pady=5, padx=5)
        self.year_entry = ttk.Entry(form_frame, width=40)
        self.year_entry.grid(row=3, column=1, pady=5, padx=5)

        # Состояние экземпляра
        ttk.Label(form_frame, text="Состояние книги:*").grid(row=4, column=0, sticky="w", pady=5, padx=5)
        conditions = [("Новая", "new"), ("Хорошее", "good"), ("Удовлетворительное", "fair"), ("Плохое", "poor")]
        self.condition_var = tk.StringVar(value="good")
        condition_frame = ttk.Frame(form_frame)
        condition_frame.grid(row=4, column=1, sticky="w", pady=5, padx=5)
        for i, (text, value) in enumerate(conditions):
            ttk.Radiobutton(condition_frame, text=text, variable=self.condition_var, value=value).pack(side="left", padx=5)

        # Описание
        ttk.Label(form_frame, text="Описание:").grid(row=5, column=0, sticky="nw", pady=5, padx=5)
        self.desc_text = scrolledtext.ScrolledText(form_frame, width=40, height=5)
        self.desc_text.grid(row=5, column=1, pady=5, padx=5)

        # Кнопка добавления
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=6, column=0, columnspan=2, pady=20)

        ttk.Button(btn_frame, text="➕ Добавить книгу в каталог", command=self.add_book).pack(side="left", padx=10)
        ttk.Button(btn_frame, text="Очистить форму", command=self.clear_add_form).pack(side="left", padx=10)

    def setup_stats_tab(self):
        """Настройка вкладки статистики"""
        self.stats_text = scrolledtext.ScrolledText(self.stats_tab, font=("Courier", 10), height=25)
        self.stats_text.pack(fill="both", expand=True, padx=20, pady=20)

        ttk.Button(self.stats_tab, text="Обновить статистику", command=self.load_stats).pack(pady=10)

        self.load_stats()

    def setup_profile_tab(self):
        """Настройка вкладки профиля"""
        user = auth.get_current_user()

        form_frame = ttk.LabelFrame(self.profile_tab, text="Информация о пользователе", padding="20")
        form_frame.pack(fill="both", expand=True, padx=20, pady=20)

        ttk.Label(form_frame, text=f"ID: {user['id']}").grid(row=0, column=0, sticky="w", pady=5, padx=5)
        ttk.Label(form_frame, text=f"Имя пользователя: {user['username']}").grid(row=1, column=0, sticky="w", pady=5, padx=5)

        ttk.Label(form_frame, text="Email:").grid(row=2, column=0, sticky="w", pady=5, padx=5)
        self.profile_email = ttk.Entry(form_frame, width=40)
        self.profile_email.grid(row=2, column=1, pady=5, padx=5)
        self.profile_email.insert(0, user['email'])

        ttk.Label(form_frame, text="Телефон:").grid(row=3, column=0, sticky="w", pady=5, padx=5)
        self.profile_phone = ttk.Entry(form_frame, width=40)
        self.profile_phone.grid(row=3, column=1, pady=5, padx=5)
        self.profile_phone.insert(0, user.get('phone', ''))

        ttk.Label(form_frame, text=f"Дата регистрации: {user['created_at']}").grid(row=4, column=0, columnspan=2, sticky="w", pady=10, padx=5)

        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=5, column=0, columnspan=2, pady=20)

        ttk.Button(btn_frame, text="💾 Сохранить изменения", command=self.update_profile).pack(side="left", padx=10)
        ttk.Button(btn_frame, text="🚪 Выйти", command=self.logout).pack(side="left", padx=10)

    def load_catalog(self):
        """Загрузка каталога доступных книг"""
        # Очищаем таблицу
        for item in self.catalog_tree.get_children():
            self.catalog_tree.delete(item)

        # Получаем доступные книги (исключая свои)
        items = book_manager.get_available_items(exclude_user_id=auth.current_user['id'])

        # Статусы на русском
        status_map = {"available": "Доступна", "pending": "В обмене", "exchanged": "Обменена"}
        condition_map = {"new": "Новая", "good": "Хорошее", "fair": "Удовл.", "poor": "Плохое"}

        for item in items:
            self.catalog_tree.insert("", "end", values=(
                item['id'],
                item['title'],
                item['author'],
                item['genre'] or "-",
                item['year'] or "-",
                item['owner_name'],
                condition_map.get(item['condition'], item['condition']),
                status_map.get(item['status'], item['status'])
            ))

    def load_my_books(self):
        """Загрузка моих книг"""
        # Очищаем таблицу
        for item in self.my_books_tree.get_children():
            self.my_books_tree.delete(item)

        # Получаем мои экземпляры
        items = book_manager.get_user_items()

        status_map = {"available": "Доступна", "pending": "В обмене", "exchanged": "Обменена"}
        condition_map = {"new": "Новая", "good": "Хорошее", "fair": "Удовл.", "poor": "Плохое"}

        for item in items:
            self.my_books_tree.insert("", "end", values=(
                item['id'],
                item['title'],
                item['author'],
                condition_map.get(item['condition'], item['condition']),
                status_map.get(item['status'], item['status']),
                item['added_at']
            ))

    def load_incoming(self):
        """Загрузка входящих запросов"""
        # Очищаем таблицу
        for item in self.incoming_tree.get_children():
            self.incoming_tree.delete(item)

        requests = exchange_manager.get_incoming_requests()

        for req in requests:
            self.incoming_tree.insert("", "end", values=(
                req['id'],
                req['title'],
                req['author'],
                req['requester_name'],
                req['requested_at']
            ))

    def load_outgoing(self):
        """Загрузка исходящих запросов"""
        # Очищаем таблицу
        for item in self.outgoing_tree.get_children():
            self.outgoing_tree.delete(item)

        requests = exchange_manager.get_outgoing_requests()

        for req in requests:
            self.outgoing_tree.insert("", "end", values=(
                req['id'],
                req['title'],
                req['author'],
                req['owner_name'],
                req['requested_at']
            ))

    def load_history(self):
        """Загрузка истории обменов"""
        # Очищаем таблицу
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)

        history = exchange_manager.get_history()

        direction_map = {"Исходящий": "📤 Отдал", "Входящий": "📥 Получил"}

        for record in history:
            self.history_tree.insert("", "end", values=(
                record['id'],
                direction_map.get(record['direction'], record['direction']),
                record['title'],
                record['author'],
                record['other_user'],
                record['completed_at']
            ))

    def search_books(self):
        """Поиск книг в каталоге"""
        keyword = self.search_entry.get().strip()
        if not keyword:
            self.load_catalog()
            return

        # Очищаем таблицу
        for item in self.catalog_tree.get_children():
            self.catalog_tree.delete(item)

        # Ищем книги (только доступные, не свои)
        all_books = book_manager.search_books(keyword)

        status_map = {"available": "Доступна", "pending": "В обмене", "exchanged": "Обменена"}
        condition_map = {"new": "Новая", "good": "Хорошее", "fair": "Удовл.", "poor": "Плохое"}

        for book in all_books:
            items = db.fetch_all(
                """SELECT bi.*, u.username as owner_name
                   FROM BookItem bi
                   JOIN Users u ON bi.owner_id = u.id
                   WHERE bi.book_id = ? AND bi.status = 'available' AND bi.owner_id != ?""",
                (book['id'], auth.current_user['id'])
            )
            for item in items:
                self.catalog_tree.insert("", "end", values=(
                    item['id'],
                    book['title'],
                    book['author'],
                    book['genre'] or "-",
                    book['year'] or "-",
                    item['owner_name'],
                    condition_map.get(item['condition'], item['condition']),
                    status_map.get(item['status'], item['status'])
                ))

    def clear_search(self):
        """Очистка поиска"""
        self.search_entry.delete(0, tk.END)
        self.load_catalog()

    def request_exchange(self):
        """Запрос на обмен"""
        selected = self.catalog_tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите книгу для запроса")
            return

        item_id = self.catalog_tree.item(selected[0])['values'][0]

        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите запросить эту книгу?"):
            success, message = exchange_manager.create_request(item_id)
            if success:
                messagebox.showinfo("Успех", message)
                self.load_catalog()
                self.load_outgoing()
            else:
                messagebox.showerror("Ошибка", message)

    def accept_request(self):
        """Принять запрос на обмен"""
        selected = self.incoming_tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите запрос")
            return

        request_id = self.incoming_tree.item(selected[0])['values'][0]

        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите принять этот запрос?"):
            success, message = exchange_manager.respond_to_request(request_id, accept=True)
            if success:
                messagebox.showinfo("Успех", message)
                self.load_incoming()
                self.load_my_books()
                self.load_history()
            else:
                messagebox.showerror("Ошибка", message)

    def reject_request(self):
        """Отклонить запрос на обмен"""
        selected = self.incoming_tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите запрос")
            return

        request_id = self.incoming_tree.item(selected[0])['values'][0]

        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите отклонить этот запрос?"):
            success, message = exchange_manager.respond_to_request(request_id, accept=False)
            if success:
                messagebox.showinfo("Успех", message)
                self.load_incoming()
                self.load_my_books()
            else:
                messagebox.showerror("Ошибка", message)

    def cancel_request(self):
        """Отменить исходящий запрос"""
        selected = self.outgoing_tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите запрос")
            return

        request_id = self.outgoing_tree.item(selected[0])['values'][0]

        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите отменить этот запрос?"):
            success, message = exchange_manager.cancel_request(request_id)
            if success:
                messagebox.showinfo("Успех", message)
                self.load_outgoing()
                self.load_catalog()
            else:
                messagebox.showerror("Ошибка", message)

    def add_book(self):
        """Добавление книги"""
        title = self.title_entry.get().strip()
        author = self.author_entry.get().strip()
        genre = self.genre_combo.get().strip()
        year = self.year_entry.get().strip()
        description = self.desc_text.get("1.0", tk.END).strip()
        condition = self.condition_var.get()

        if not title or not author:
            messagebox.showerror("Ошибка", "Название и автор обязательны для заполнения")
            return

        # Преобразуем год
        year_int = None
        if year:
            try:
                year_int = int(year)
            except ValueError:
                messagebox.showerror("Ошибка", "Год должен быть числом")
                return

        # Добавляем книгу
        success, message, book_id = book_manager.add_book(title, author, genre, year_int, description)

        if success:
            # Добавляем экземпляр
            success2, message2 = book_manager.add_book_item(book_id, condition)
            if success2:
                messagebox.showinfo("Успех", f"{message}\n{message2}")
                self.clear_add_form()
                self.load_my_books()
                self.load_catalog()
                self.load_stats()
            else:
                messagebox.showwarning("Внимание", f"{message}\nНо не удалось добавить экземпляр: {message2}")
        else:
            # Если книга уже существует, пробуем добавить только экземпляр
            if "уже существует" in message and book_id:
                success2, message2 = book_manager.add_book_item(book_id, condition)
                if success2:
                    messagebox.showinfo("Успех", f"Книга уже была в каталоге.\n{message2}")
                    self.clear_add_form()
                    self.load_my_books()
                    self.load_catalog()
                    self.load_stats()
                else:
                    messagebox.showerror("Ошибка", message2)
            else:
                messagebox.showerror("Ошибка", message)

    def clear_add_form(self):
        """Очистка формы добавления книги"""
        self.title_entry.delete(0, tk.END)
        self.author_entry.delete(0, tk.END)
        self.genre_combo.set("")
        self.year_entry.delete(0, tk.END)
        self.desc_text.delete("1.0", tk.END)
        self.condition_var.set("good")

    def delete_my_book(self):
        """Удаление выбранного экземпляра книги"""
        selected = self.my_books_tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите книгу для удаления")
            return

        item_id = self.my_books_tree.item(selected[0])['values'][0]

        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить этот экземпляр книги?"):
            success, message = book_manager.delete_item(item_id)
            if success:
                messagebox.showinfo("Успех", message)
                self.load_my_books()
                self.load_catalog()
                self.load_stats()
            else:
                messagebox.showerror("Ошибка", message)

    def load_stats(self):
        """Загрузка статистики"""
        book_stats = book_manager.get_statistics()
        exchange_stats = exchange_manager.get_statistics()

        self.stats_text.delete("1.0", tk.END)
        self.stats_text.insert("1.0", """
╔════════════════════════════════════════════════════════════╗
║                    📊 МОЯ СТАТИСТИКА                       ║
╠════════════════════════════════════════════════════════════╣
║                                                            ║
║  📚 БИБЛИОТЕКА:                                            ║
║     Всего книг в библиотеке:          {:>5}                   ║
║     Доступно для обмена:              {:>5}                   ║
║                                                            ║
║  🔄 ОБМЕНЫ:                                                ║
║     Входящих запросов (ожидают):      {:>5}                   ║
║     Исходящих запросов (ожидают):     {:>5}                   ║
║     Принятых запросов:                {:>5}                   ║
║     Отклоненных запросов:             {:>5}                   ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
        """.format(
            book_stats.get('my_books', 0),
            book_stats.get('available', 0),
            exchange_stats.get('received_pending', 0),
            exchange_stats.get('sent_pending', 0),
            exchange_stats.get('accepted', 0),
            exchange_stats.get('rejected', 0)
        ))

    def update_profile(self):
        """Обновление профиля"""
        email = self.profile_email.get().strip()
        phone = self.profile_phone.get().strip()

        success, message = auth.update_profile(email=email, phone=phone)
        if success:
            messagebox.showinfo("Успех", message)
        else:
            messagebox.showerror("Ошибка", message)

    def logout(self):
        """Выход из системы"""
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите выйти?"):
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