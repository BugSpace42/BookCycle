import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from database import db
from auth import auth
from books import book_manager
from exchanges import exchange_manager

class LoginWindow:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Книгообмен - Вход в систему")
        self.window.geometry("400x350")
        self.window.resizable(False, False)
        self.window.eval('tk::PlaceWindow . center')

        self.setup_ui()

    def setup_ui(self):
        title_label = tk.Label(
            self.window,
            text="Добро пожаловать!",
            font=("Arial", 18, "bold")
        )
        title_label.pack(pady=20)

        form_frame = ttk.Frame(self.window, padding="20")
        form_frame.pack(fill="both", expand=True)

        ttk.Label(form_frame, text="Имя пользователя или Email:", font=("Arial", 10)).grid(
            row=0, column=0, sticky="w", pady=(0, 5)
        )
        self.username_entry = ttk.Entry(form_frame, width=30)
        self.username_entry.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        self.username_entry.focus()

        ttk.Label(form_frame, text="Пароль:", font=("Arial", 10)).grid(
            row=2, column=0, sticky="w", pady=(0, 5)
        )
        self.password_entry = ttk.Entry(form_frame, width=30, show="*")
        self.password_entry.grid(row=3, column=0, sticky="ew", pady=(0, 20))

        login_btn = ttk.Button(
            form_frame,
            text="Войти",
            command=self.login,
            width=25
        )
        login_btn.grid(row=4, column=0, pady=5)

        register_btn = ttk.Button(
            form_frame,
            text="Зарегистрироваться",
            command=self.open_register,
            width=25
        )
        register_btn.grid(row=5, column=0, pady=5)

        form_frame.columnconfigure(0, weight=1)

        self.window.bind('<Return>', lambda e: self.login())

    def login(self):
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
        RegisterWindow(self.window)

    def run(self):
        self.window.mainloop()


class RegisterWindow:
    def __init__(self, parent):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("Книгообмен - Регистрация")
        self.window.geometry("450x550")
        self.window.resizable(False, False)

        self.window.transient(parent)
        self.window.grab_set()

        self.setup_ui()

    def setup_ui(self):
        title_label = tk.Label(
            self.window,
            text="Регистрация нового пользователя",
            font=("Arial", 14, "bold")
        )
        title_label.pack(pady=20)

        form_frame = ttk.Frame(self.window, padding="20")
        form_frame.pack(fill="both", expand=True)

        ttk.Label(form_frame, text="Имя пользователя:*", font=("Arial", 10)).grid(
            row=0, column=0, sticky="w", pady=(0, 5)
        )
        self.username_entry = ttk.Entry(form_frame, width=35)
        self.username_entry.grid(row=1, column=0, sticky="ew", pady=(0, 15))

        ttk.Label(form_frame, text="Email:*", font=("Arial", 10)).grid(
            row=2, column=0, sticky="w", pady=(0, 5)
        )
        self.email_entry = ttk.Entry(form_frame, width=35)
        self.email_entry.grid(row=3, column=0, sticky="ew", pady=(0, 15))

        ttk.Label(form_frame, text="Пароль:*", font=("Arial", 10)).grid(
            row=4, column=0, sticky="w", pady=(0, 5)
        )
        self.password_entry = ttk.Entry(form_frame, width=35, show="*")
        self.password_entry.grid(row=5, column=0, sticky="ew", pady=(0, 5))

        hint_label = tk.Label(
            form_frame,
            text="Минимум 6 символов, заглавная буква, строчная буква, цифра",
            font=("Arial", 8),
            fg="gray"
        )
        hint_label.grid(row=6, column=0, pady=(0, 15))

        ttk.Label(form_frame, text="Подтверждение пароля:*", font=("Arial", 10)).grid(
            row=7, column=0, sticky="w", pady=(0, 5)
        )
        self.confirm_entry = ttk.Entry(form_frame, width=35, show="*")
        self.confirm_entry.grid(row=8, column=0, sticky="ew", pady=(0, 15))

        ttk.Label(form_frame, text="Телефон (необязательно):", font=("Arial", 10)).grid(
            row=9, column=0, sticky="w", pady=(0, 5)
        )
        self.phone_entry = ttk.Entry(form_frame, width=35)
        self.phone_entry.grid(row=10, column=0, sticky="ew", pady=(0, 20))

        register_btn = ttk.Button(
            form_frame,
            text="Зарегистрироваться",
            command=self.register,
            width=25
        )
        register_btn.grid(row=11, column=0, pady=5)

        form_frame.columnconfigure(0, weight=1)

        self.window.bind('<Return>', lambda e: self.register())

    def register(self):
        username = self.username_entry.get().strip()
        email = self.email_entry.get().strip()
        password = self.password_entry.get()
        confirm = self.confirm_entry.get()
        phone = self.phone_entry.get().strip()

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
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Книгообмен - Главное окно")
        self.window.geometry("1200x800")

        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.setup_tabs()

    def setup_tabs(self):
        self.catalog_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.catalog_tab, text="Каталог для обмена")
        self.setup_catalog_tab()

        self.all_editions_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.all_editions_tab, text="Все издания")
        self.setup_all_editions_tab()

        self.my_books_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.my_books_tab, text="Мои книги")
        self.setup_my_books_tab()

        self.incoming_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.incoming_tab, text="Входящие запросы")
        self.setup_incoming_tab()

        self.outgoing_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.outgoing_tab, text="Исходящие запросы")
        self.setup_outgoing_tab()

        self.history_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.history_tab, text="История обменов")
        self.setup_history_tab()

        self.add_book_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.add_book_tab, text="Добавить книгу")
        self.setup_add_book_tab()

        self.stats_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.stats_tab, text="Статистика")
        self.setup_stats_tab()

        self.profile_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.profile_tab, text="Профиль")
        self.setup_profile_tab()

    def setup_catalog_tab(self):
        search_frame = ttk.Frame(self.catalog_tab)
        search_frame.pack(fill="x", padx=10, pady=10)

        ttk.Label(search_frame, text="Поиск:").pack(side="left", padx=5)
        self.search_entry = ttk.Entry(search_frame, width=30)
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind('<KeyRelease>', lambda e: self.search_books())

        ttk.Button(search_frame, text="Очистить", command=self.clear_search).pack(side="left", padx=5)

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

        self.catalog_tree.column("id", width=50, minwidth=50)
        self.catalog_tree.column("title", width=250, minwidth=150)
        self.catalog_tree.column("author", width=180, minwidth=120)
        self.catalog_tree.column("genre", width=100, minwidth=80)
        self.catalog_tree.column("year", width=60, minwidth=50)
        self.catalog_tree.column("owner", width=120, minwidth=100)
        self.catalog_tree.column("condition", width=90, minwidth=80)
        self.catalog_tree.column("status", width=90, minwidth=80)

        scrollbar = ttk.Scrollbar(self.catalog_tab, orient="vertical", command=self.catalog_tree.yview)
        self.catalog_tree.configure(yscrollcommand=scrollbar.set)

        self.catalog_tree.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side="right", fill="y", padx=(0, 10), pady=10)

        btn_frame = ttk.Frame(self.catalog_tab)
        btn_frame.pack(fill="x", padx=10, pady=5)

        ttk.Button(btn_frame, text="📩 Запросить обмен", command=self.request_exchange).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="🔄 Обновить", command=self.load_catalog).pack(side="left", padx=5)

        self.load_catalog()

    def setup_all_editions_tab(self):
        search_frame = ttk.Frame(self.all_editions_tab)
        search_frame.pack(fill="x", padx=10, pady=10)

        ttk.Label(search_frame, text="Поиск по изданиям:").pack(side="left", padx=5)
        self.editions_search_entry = ttk.Entry(search_frame, width=30)
        self.editions_search_entry.pack(side="left", padx=5)
        self.editions_search_entry.bind('<KeyRelease>', lambda e: self.search_editions())

        ttk.Button(search_frame, text="Очистить", command=self.clear_editions_search).pack(side="left", padx=5)

        info_label = ttk.Label(search_frame, text="Зеленым выделены книги, которые уже есть в вашей библиотеке",
                               foreground="green")
        info_label.pack(side="right", padx=10)

        columns = ("id", "title", "author", "genre", "year", "total_copies", "my_copies", "available_copies")
        self.editions_tree = ttk.Treeview(self.all_editions_tab, columns=columns, show="headings", height=20)

        self.editions_tree.heading("id", text="ID")
        self.editions_tree.heading("title", text="Название")
        self.editions_tree.heading("author", text="Автор")
        self.editions_tree.heading("genre", text="Жанр")
        self.editions_tree.heading("year", text="Год")
        self.editions_tree.heading("total_copies", text="Всего экз.")
        self.editions_tree.heading("my_copies", text="Мои экз.")
        self.editions_tree.heading("available_copies", text="Доступно для обмена")

        self.editions_tree.column("id", width=50, minwidth=50)
        self.editions_tree.column("title", width=280, minwidth=150)
        self.editions_tree.column("author", width=200, minwidth=120)
        self.editions_tree.column("genre", width=100, minwidth=80)
        self.editions_tree.column("year", width=60, minwidth=50)
        self.editions_tree.column("total_copies", width=90, minwidth=80)
        self.editions_tree.column("my_copies", width=90, minwidth=80)
        self.editions_tree.column("available_copies", width=130, minwidth=100)

        scrollbar = ttk.Scrollbar(self.all_editions_tab, orient="vertical", command=self.editions_tree.yview)
        self.editions_tree.configure(yscrollcommand=scrollbar.set)

        self.editions_tree.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side="right", fill="y", padx=(0, 10), pady=10)

        btn_frame = ttk.Frame(self.all_editions_tab)
        btn_frame.pack(fill="x", padx=10, pady=5)

        ttk.Button(btn_frame, text="📖 Добавить мой экземпляр",
                   command=self.add_copy_from_edition).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="🔄 Обновить",
                   command=self.load_all_editions).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="ℹ️ Подробнее о книге",
                   command=self.show_edition_details).pack(side="left", padx=5)

        self.editions_tree.bind('<Double-Button-1>', lambda e: self.add_copy_from_edition())

        self.load_all_editions()

    def setup_my_books_tab(self):
        columns = ("id", "title", "author", "condition", "status", "added_at")
        self.my_books_tree = ttk.Treeview(self.my_books_tab, columns=columns, show="headings", height=20)

        self.my_books_tree.heading("id", text="ID")
        self.my_books_tree.heading("title", text="Название")
        self.my_books_tree.heading("author", text="Автор")
        self.my_books_tree.heading("condition", text="Состояние")
        self.my_books_tree.heading("status", text="Статус")
        self.my_books_tree.heading("added_at", text="Дата добавления")

        self.my_books_tree.column("id", width=50, minwidth=50)
        self.my_books_tree.column("title", width=300, minwidth=200)
        self.my_books_tree.column("author", width=200, minwidth=150)
        self.my_books_tree.column("condition", width=100, minwidth=80)
        self.my_books_tree.column("status", width=100, minwidth=80)
        self.my_books_tree.column("added_at", width=170, minwidth=150)

        scrollbar = ttk.Scrollbar(self.my_books_tab, orient="vertical", command=self.my_books_tree.yview)
        self.my_books_tree.configure(yscrollcommand=scrollbar.set)

        self.my_books_tree.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side="right", fill="y", padx=(0, 10), pady=10)

        btn_frame = ttk.Frame(self.my_books_tab)
        btn_frame.pack(fill="x", padx=10, pady=5)

        ttk.Button(btn_frame, text="🗑️ Удалить", command=self.delete_my_book).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="🔄 Обновить", command=self.load_my_books).pack(side="left", padx=5)

        self.load_my_books()

    def setup_incoming_tab(self):
        columns = ("id", "book", "author", "requester", "requested_at")
        self.incoming_tree = ttk.Treeview(self.incoming_tab, columns=columns, show="headings", height=15)

        self.incoming_tree.heading("id", text="ID")
        self.incoming_tree.heading("book", text="Книга")
        self.incoming_tree.heading("author", text="Автор")
        self.incoming_tree.heading("requester", text="Запрашивает")
        self.incoming_tree.heading("requested_at", text="Дата запроса")

        self.incoming_tree.column("id", width=50, minwidth=50)
        self.incoming_tree.column("book", width=300, minwidth=200)
        self.incoming_tree.column("author", width=200, minwidth=150)
        self.incoming_tree.column("requester", width=150, minwidth=120)
        self.incoming_tree.column("requested_at", width=170, minwidth=150)

        scrollbar = ttk.Scrollbar(self.incoming_tab, orient="vertical", command=self.incoming_tree.yview)
        self.incoming_tree.configure(yscrollcommand=scrollbar.set)

        self.incoming_tree.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side="right", fill="y", padx=(0, 10), pady=10)

        btn_frame = ttk.Frame(self.incoming_tab)
        btn_frame.pack(fill="x", padx=10, pady=5)

        ttk.Button(btn_frame, text="✅ Принять", command=self.accept_request).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="❌ Отклонить", command=self.reject_request).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="🔄 Обновить", command=self.load_incoming).pack(side="left", padx=5)

        self.load_incoming()

    def setup_outgoing_tab(self):
        columns = ("id", "book", "author", "owner", "requested_at")
        self.outgoing_tree = ttk.Treeview(self.outgoing_tab, columns=columns, show="headings", height=15)

        self.outgoing_tree.heading("id", text="ID")
        self.outgoing_tree.heading("book", text="Книга")
        self.outgoing_tree.heading("author", text="Автор")
        self.outgoing_tree.heading("owner", text="Владелец")
        self.outgoing_tree.heading("requested_at", text="Дата запроса")

        self.outgoing_tree.column("id", width=50, minwidth=50)
        self.outgoing_tree.column("book", width=300, minwidth=200)
        self.outgoing_tree.column("author", width=200, minwidth=150)
        self.outgoing_tree.column("owner", width=150, minwidth=120)
        self.outgoing_tree.column("requested_at", width=170, minwidth=150)

        scrollbar = ttk.Scrollbar(self.outgoing_tab, orient="vertical", command=self.outgoing_tree.yview)
        self.outgoing_tree.configure(yscrollcommand=scrollbar.set)

        self.outgoing_tree.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side="right", fill="y", padx=(0, 10), pady=10)

        btn_frame = ttk.Frame(self.outgoing_tab)
        btn_frame.pack(fill="x", padx=10, pady=5)

        ttk.Button(btn_frame, text="Отменить запрос", command=self.cancel_request).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Обновить", command=self.load_outgoing).pack(side="left", padx=5)

        self.load_outgoing()

    def setup_history_tab(self):
        columns = ("id", "direction", "book", "author", "other_user", "completed_at")
        self.history_tree = ttk.Treeview(self.history_tab, columns=columns, show="headings", height=20)

        self.history_tree.heading("id", text="ID")
        self.history_tree.heading("direction", text="Тип")
        self.history_tree.heading("book", text="Книга")
        self.history_tree.heading("author", text="Автор")
        self.history_tree.heading("other_user", text="С кем")
        self.history_tree.heading("completed_at", text="Дата завершения")

        self.history_tree.column("id", width=50, minwidth=50)
        self.history_tree.column("direction", width=80, minwidth=70)
        self.history_tree.column("book", width=280, minwidth=200)
        self.history_tree.column("author", width=180, minwidth=150)
        self.history_tree.column("other_user", width=180, minwidth=150)
        self.history_tree.column("completed_at", width=170, minwidth=150)

        scrollbar = ttk.Scrollbar(self.history_tab, orient="vertical", command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)

        self.history_tree.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side="right", fill="y", padx=(0, 10), pady=10)

        btn_frame = ttk.Frame(self.history_tab)
        btn_frame.pack(fill="x", padx=10, pady=5)

        ttk.Button(btn_frame, text="Обновить", command=self.load_history).pack(side="left", padx=5)

        self.load_history()

    def setup_add_book_tab(self):
        form_frame = ttk.LabelFrame(self.add_book_tab, text="Информация о книге", padding="20")
        form_frame.pack(fill="both", expand=True, padx=20, pady=20)

        form_frame.columnconfigure(0, weight=0)
        form_frame.columnconfigure(1, weight=1)

        ttk.Label(form_frame, text="Название:*", font=("Arial", 10)).grid(
            row=0, column=0, sticky="w", pady=8, padx=(0, 10)
        )
        self.title_entry = ttk.Entry(form_frame)
        self.title_entry.grid(row=0, column=1, sticky="ew", pady=8)

        ttk.Label(form_frame, text="Автор:*", font=("Arial", 10)).grid(
            row=1, column=0, sticky="w", pady=8, padx=(0, 10)
        )
        self.author_entry = ttk.Entry(form_frame)
        self.author_entry.grid(row=1, column=1, sticky="ew", pady=8)

        ttk.Label(form_frame, text="Жанр:", font=("Arial", 10)).grid(
            row=2, column=0, sticky="w", pady=8, padx=(0, 10)
        )
        genres = ["Роман", "Детектив", "Фантастика", "Фэнтези", "Поэзия", "Драма", "Комедия", "Наука", "Учебник",
                  "Другое"]
        self.genre_combo = ttk.Combobox(form_frame, values=genres)
        self.genre_combo.grid(row=2, column=1, sticky="ew", pady=8)

        ttk.Label(form_frame, text="Год издания:", font=("Arial", 10)).grid(
            row=3, column=0, sticky="w", pady=8, padx=(0, 10)
        )
        self.year_entry = ttk.Entry(form_frame)
        self.year_entry.grid(row=3, column=1, sticky="ew", pady=8)

        ttk.Label(form_frame, text="Состояние книги:*", font=("Arial", 10)).grid(
            row=4, column=0, sticky="nw", pady=8, padx=(0, 10)
        )
        conditions = [("Новая", "new"), ("Хорошее", "good"), ("Удовлетворительное", "fair"), ("Плохое", "poor")]
        self.condition_var = tk.StringVar(value="good")
        condition_frame = ttk.Frame(form_frame)
        condition_frame.grid(row=4, column=1, sticky="w", pady=8)
        for i, (text, value) in enumerate(conditions):
            ttk.Radiobutton(condition_frame, text=text, variable=self.condition_var, value=value).pack(side="left",
                                                                                                       padx=10)

        ttk.Label(form_frame, text="Описание:", font=("Arial", 10)).grid(
            row=5, column=0, sticky="nw", pady=8, padx=(0, 10)
        )
        self.desc_text = scrolledtext.ScrolledText(form_frame, height=5)
        self.desc_text.grid(row=5, column=1, sticky="ew", pady=8)

        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=6, column=0, columnspan=2, pady=20)

        ttk.Button(btn_frame, text="Добавить книгу в каталог", command=self.add_book).pack(side="left", padx=10)
        ttk.Button(btn_frame, text="Очистить форму", command=self.clear_add_form).pack(side="left", padx=10)

    def setup_stats_tab(self):
        self.stats_text = scrolledtext.ScrolledText(
            self.stats_tab,
            font=("Courier", 11),
            height=25,
            wrap=tk.NONE
        )
        self.stats_text.pack(fill="both", expand=True, padx=20, pady=20)

        btn_frame = ttk.Frame(self.stats_tab)
        btn_frame.pack(pady=(0, 20))
        ttk.Button(btn_frame, text="Обновить статистику", command=self.load_stats).pack()

        self.load_stats()

    def setup_profile_tab(self):
        user = auth.get_current_user()

        form_frame = ttk.LabelFrame(self.profile_tab, text="Информация о пользователе", padding="20")
        form_frame.pack(fill="both", expand=True, padx=20, pady=20)

        form_frame.columnconfigure(0, weight=0)
        form_frame.columnconfigure(1, weight=1)

        ttk.Label(form_frame, text=f"ID:", font=("Arial", 10)).grid(
            row=0, column=0, sticky="w", pady=8, padx=(0, 10)
        )
        ttk.Label(form_frame, text=f"{user['id']}", font=("Arial", 10)).grid(
            row=0, column=1, sticky="w", pady=8
        )

        ttk.Label(form_frame, text=f"Имя пользователя:", font=("Arial", 10)).grid(
            row=1, column=0, sticky="w", pady=8, padx=(0, 10)
        )
        ttk.Label(form_frame, text=f"{user['username']}", font=("Arial", 10)).grid(
            row=1, column=1, sticky="w", pady=8
        )

        ttk.Label(form_frame, text="Email:", font=("Arial", 10)).grid(
            row=2, column=0, sticky="w", pady=8, padx=(0, 10)
        )
        self.profile_email = ttk.Entry(form_frame)
        self.profile_email.grid(row=2, column=1, sticky="ew", pady=8)
        self.profile_email.insert(0, user['email'])

        ttk.Label(form_frame, text="Телефон:", font=("Arial", 10)).grid(
            row=3, column=0, sticky="w", pady=8, padx=(0, 10)
        )
        self.profile_phone = ttk.Entry(form_frame)
        self.profile_phone.grid(row=3, column=1, sticky="ew", pady=8)
        self.profile_phone.insert(0, user.get('phone', ''))

        ttk.Label(form_frame, text="Дата регистрации:", font=("Arial", 10)).grid(
            row=4, column=0, sticky="w", pady=8, padx=(0, 10)
        )
        ttk.Label(form_frame, text=f"{user['created_at']}", font=("Arial", 10)).grid(
            row=4, column=1, sticky="w", pady=8
        )

        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=5, column=0, columnspan=2, pady=20)

        ttk.Button(btn_frame, text="Сохранить изменения", command=self.update_profile).pack(side="left", padx=10)
        ttk.Button(btn_frame, text="Выйти из системы", command=self.logout).pack(side="left", padx=10)

    def load_catalog(self):
        for item in self.catalog_tree.get_children():
            self.catalog_tree.delete(item)

        items = book_manager.get_available_items(exclude_user_id=auth.current_user['id'])

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

    def load_all_editions(self):
        # Очищаем таблицу
        for item in self.editions_tree.get_children():
            self.editions_tree.delete(item)

        books = book_manager.get_all_books()

        if not books:
            self.editions_tree.insert("", "end", values=(
                "", "Нет книг в каталоге", "", "", "", "", "", ""
            ))
            return

        user_id = auth.current_user['id']

        for book in books:
            try:
                total_result = db.fetch_one(
                    "SELECT COUNT(*) as count FROM BookItem WHERE book_id = ?",
                    (book['id'],)
                )
                total = total_result['count'] if total_result else 0

                my_copies_result = db.fetch_one(
                    "SELECT COUNT(*) as count FROM BookItem WHERE book_id = ? AND owner_id = ?",
                    (book['id'], user_id)
                )
                my_copies = my_copies_result['count'] if my_copies_result else 0

                available_result = db.fetch_one(
                    """SELECT COUNT(*) as count FROM BookItem 
                       WHERE book_id = ? AND status = 'available' AND owner_id != ?""",
                    (book['id'], user_id)
                )
                available = available_result['count'] if available_result else 0

                tag = 'has_copy' if my_copies > 0 else ''

                self.editions_tree.insert("", "end", values=(
                    book['id'],
                    book['title'],
                    book['author'],
                    book['genre'] or "-",
                    book['year'] or "-",
                    total,
                    my_copies,
                    available
                ), tags=(tag,))
            except Exception as e:
                print(f"Ошибка при загрузке книги {book.get('title')}: {e}")
                continue

        self.editions_tree.tag_configure('has_copy', background='#e6f3e6')  # Светло-зеленый

    def load_my_books(self):
        for item in self.my_books_tree.get_children():
            self.my_books_tree.delete(item)

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
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)

        history = exchange_manager.get_history()

        direction_map = {"Исходящий": "Отдал", "Входящий": "Получил"}

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
        keyword = self.search_entry.get().strip()
        if not keyword:
            self.load_catalog()
            return

        for item in self.catalog_tree.get_children():
            self.catalog_tree.delete(item)

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

    def search_editions(self):
        keyword = self.editions_search_entry.get().strip()

        if not keyword:
            self.load_all_editions()
            return

        for item in self.editions_tree.get_children():
            self.editions_tree.delete(item)

        books = book_manager.search_books(keyword)
        user_id = auth.current_user['id']

        for book in books:
            total = db.fetch_one(
                "SELECT COUNT(*) as count FROM BookItem WHERE book_id = ?",
                (book['id'],)
            )

            my_copies = db.fetch_one(
                "SELECT COUNT(*) as count FROM BookItem WHERE book_id = ? AND owner_id = ?",
                (book['id'], user_id)
            )

            available = db.fetch_one(
                """SELECT COUNT(*) as count FROM BookItem 
                   WHERE book_id = ? AND status = 'available' AND owner_id != ?""",
                (book['id'], user_id)
            )

            tag = 'has_copy' if my_copies and my_copies['count'] > 0 else ''

            self.editions_tree.insert("", "end", values=(
                book['id'],
                book['title'],
                book['author'],
                book['genre'] or "-",
                book['year'] or "-",
                total['count'] if total else 0,
                my_copies['count'] if my_copies else 0,
                available['count'] if available else 0
            ), tags=(tag,))

    def clear_search(self):
        self.search_entry.delete(0, tk.END)
        self.load_catalog()

    def clear_editions_search(self):
        self.editions_search_entry.delete(0, tk.END)
        self.load_all_editions()

    def request_exchange(self):
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
                self.load_all_editions()
            else:
                messagebox.showerror("Ошибка", message)

    def add_copy_from_edition(self):
        selected = self.editions_tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите издание книги")
            return

        values = self.editions_tree.item(selected[0])['values']
        book_id = values[0]
        book_title = values[1]
        book_author = values[2]

        my_copies = values[6]

        if my_copies >= 10:
            if not messagebox.askyesno("Подтверждение",
                                       f"У вас уже есть {my_copies} экземпляров этой книги.\n"
                                       "Вы уверены, что хотите добавить ещё один?"):
                return

        dialog = tk.Toplevel(self.window)
        dialog.title("Добавление экземпляра")
        dialog.geometry("400x320")
        dialog.transient(self.window)
        dialog.grab_set()
        dialog.resizable(False, False)

        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (dialog.winfo_screenheight() // 2) - (320 // 2)
        dialog.geometry(f"400x320+{x}+{y}")

        main_frame = ttk.Frame(dialog, padding="15")
        main_frame.pack(fill="both", expand=True)

        info_frame = ttk.LabelFrame(main_frame, text="Информация о книге", padding="10")
        info_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(info_frame, text="Название:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="w", pady=2)
        title_label = ttk.Label(info_frame, text=book_title, font=("Arial", 10), wraplength=250)
        title_label.grid(row=0, column=1, sticky="w", pady=2, padx=(10, 0))

        ttk.Label(info_frame, text="Автор:", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky="w", pady=2)
        ttk.Label(info_frame, text=book_author, font=("Arial", 10)).grid(row=1, column=1, sticky="w", pady=2,
                                                                         padx=(10, 0))

        info_frame.columnconfigure(1, weight=1)

        condition_frame = ttk.LabelFrame(main_frame, text="Состояние книги", padding="10")
        condition_frame.pack(fill="x", pady=(0, 15))

        condition_var = tk.StringVar(value="good")

        radio_frame = ttk.Frame(condition_frame)
        radio_frame.pack(fill="x")

        conditions = [
            ("Новая", "new"),
            ("Хорошее", "good"),
            ("Удовлетворительное", "fair"),
            ("Плохое", "poor")
        ]

        for i, (text, value) in enumerate(conditions):
            row = i // 2
            col = i % 2
            ttk.Radiobutton(radio_frame, text=text, variable=condition_var, value=value).grid(
                row=row, column=col, sticky="w", padx=(0, 20), pady=5
            )

        radio_frame.columnconfigure(0, weight=1)
        radio_frame.columnconfigure(1, weight=1)

        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill="x", pady=(10, 0))

        def confirm_add():
            condition = condition_var.get()
            success, message = book_manager.add_book_item(book_id, condition)

            if success:
                messagebox.showinfo("Успех", message)
                dialog.destroy()
                self.load_all_editions()
                self.load_my_books()
                self.load_catalog()
                self.load_stats()
            else:
                messagebox.showerror("Ошибка", message)

        ttk.Button(btn_frame, text="Добавить", command=confirm_add, width=15).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Отмена", command=dialog.destroy, width=15).pack(side="right", padx=5)

        dialog.focus_force()

        dialog.bind('<Return>', lambda e: confirm_add())
        dialog.bind('<Escape>', lambda e: dialog.destroy())

    def show_edition_details(self):
        selected = self.editions_tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите издание книги")
            return

        values = self.editions_tree.item(selected[0])['values']
        book_id = values[0]

        book = book_manager.get_book_by_id(book_id)
        if not book:
            messagebox.showerror("Ошибка", "Книга не найдена")
            return

        details = tk.Toplevel(self.window)
        details.title(f"Информация о книге: {book['title']}")
        details.geometry("550x500")
        details.transient(self.window)
        details.grab_set()

        details.update_idletasks()
        x = (details.winfo_screenwidth() // 2) - (550 // 2)
        y = (details.winfo_screenheight() // 2) - (500 // 2)
        details.geometry(f"550x500+{x}+{y}")

        text_widget = scrolledtext.ScrolledText(details, wrap=tk.WORD, font=("Arial", 10))
        text_widget.pack(fill="both", expand=True, padx=10, pady=10)

        # Формируем информацию
        info = f"""
                         ИНФОРМАЦИЯ О КНИГЕ

    Название: {book['title']}
    Автор: {book['author']}
    Жанр: {book['genre'] or 'Не указан'}
    Год издания: {book['year'] or 'Не указан'}

    Описание:
    {book['description'] or 'Описание отсутствует'}


    Статистика по экземплярам:
    """

        stats = db.fetch_all(
            """SELECT status, COUNT(*) as count 
               FROM BookItem 
               WHERE book_id = ? 
               GROUP BY status""",
            (book_id,)
        )

        status_names = {
            'available': 'Доступно для обмена',
            'pending': 'В процессе обмена',
            'exchanged': 'Обменено'
        }

        if stats:
            for stat in stats:
                status_name = status_names.get(stat['status'], stat['status'])
                info += f"\n   • {status_name}: {stat['count']} шт."
        else:
            info += "\n   • Нет экземпляров в системе"

        owners = db.fetch_all(
            """SELECT DISTINCT u.username, bi.condition, bi.status
               FROM BookItem bi
               JOIN Users u ON bi.owner_id = u.id
               WHERE bi.book_id = ? AND bi.status = 'available' AND bi.owner_id != ?
               LIMIT 5""",
            (book_id, auth.current_user['id'])
        )

        if owners:
            info += "\n\n"
            info += "Владельцы доступных экземпляров:\n"
            condition_map = {"new": "Новая", "good": "Хорошее", "fair": "Удовл.", "poor": "Плохое"}
            for owner in owners:
                info += f"\n   • {owner['username']} (Состояние: {condition_map.get(owner['condition'], owner['condition'])})"

        text_widget.insert("1.0", info)
        text_widget.configure(state='disabled')  # Делаем поле только для чтения

    def accept_request(self):
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
                self.load_all_editions()
            else:
                messagebox.showerror("Ошибка", message)

    def reject_request(self):
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
                self.load_all_editions()  # Обновляем список изданий
            else:
                messagebox.showerror("Ошибка", message)

    def cancel_request(self):
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
                self.load_all_editions()  # Обновляем список изданий
            else:
                messagebox.showerror("Ошибка", message)

    def add_book(self):
        title = self.title_entry.get().strip()
        author = self.author_entry.get().strip()
        genre = self.genre_combo.get().strip()
        year = self.year_entry.get().strip()
        description = self.desc_text.get("1.0", tk.END).strip()
        condition = self.condition_var.get()

        if not title or not author:
            messagebox.showerror("Ошибка", "Название и автор обязательны для заполнения")
            return

        year_int = None
        if year:
            try:
                year_int = int(year)
            except ValueError:
                messagebox.showerror("Ошибка", "Год должен быть числом")
                return

        success, message, book_id = book_manager.add_book(title, author, genre, year_int, description)

        if success:
            success2, message2 = book_manager.add_book_item(book_id, condition)
            if success2:
                messagebox.showinfo("Успех", f"{message}\n{message2}")
                self.clear_add_form()
                self.load_my_books()
                self.load_catalog()
                self.load_all_editions()  # Обновляем список изданий
                self.load_stats()
            else:
                messagebox.showwarning("Внимание", f"{message}\nНо не удалось добавить экземпляр: {message2}")
        else:
            if "уже существует" in message and book_id:
                success2, message2 = book_manager.add_book_item(book_id, condition)
                if success2:
                    messagebox.showinfo("Успех", f"Книга уже была в каталоге.\n{message2}")
                    self.clear_add_form()
                    self.load_my_books()
                    self.load_catalog()
                    self.load_all_editions()  # Обновляем список изданий
                    self.load_stats()
                else:
                    messagebox.showerror("Ошибка", message2)
            else:
                messagebox.showerror("Ошибка", message)

    def clear_add_form(self):
        self.title_entry.delete(0, tk.END)
        self.author_entry.delete(0, tk.END)
        self.genre_combo.set("")
        self.year_entry.delete(0, tk.END)
        self.desc_text.delete("1.0", tk.END)
        self.condition_var.set("good")

    def delete_my_book(self):
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
                self.load_all_editions()
                self.load_stats()
            else:
                messagebox.showerror("Ошибка", message)

    def load_stats(self):
        book_stats = book_manager.get_statistics()
        exchange_stats = exchange_manager.get_statistics()

        self.stats_text.delete("1.0", tk.END)
        self.stats_text.insert("1.0", f"""
                               СТАТИСТИКА ПОЛЬЗОВАТЕЛЯ
      БИБЛИОТЕКА:
      Всего книг в библиотеке: {book_stats.get('my_books', 0):>5}
      Доступно для обмена: {book_stats.get('available', 0):>5}

      ОБМЕНЫ:
      Входящих запросов (ожидают ответа): {exchange_stats.get('received_pending', 0):>5}
      Исходящих запросов (ожидают ответа): {exchange_stats.get('sent_pending', 0):>5}
      Принятых запросов: {exchange_stats.get('accepted', 0):>5}
      Отклоненных запросов: {exchange_stats.get('rejected', 0):>5}
        """)

    def update_profile(self):
        email = self.profile_email.get().strip()
        phone = self.profile_phone.get().strip()

        success, message = auth.update_profile(email=email, phone=phone)
        if success:
            messagebox.showinfo("Успех", message)
        else:
            messagebox.showerror("Ошибка", message)

    def logout(self):
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите выйти из системы?"):
            success, message = auth.logout()
            if success:
                messagebox.showinfo("Успех", message)
                self.window.destroy()
                LoginWindow().run()

    def run(self):
        self.window.mainloop()


def main():
    print("Запуск приложения 'Книгообмен'")
    LoginWindow().run()


if __name__ == "__main__":
    main()