import tkinter as tk
from tkinter import ttk, messagebox
import requests

API_URL = "http://127.0.0.1:8000"
TOUR_TYPES = ["cruise", "resort", "tourist", "business", "exclusive"]
STATUSES = ["created", "confirmed", "paid", "cancelled"]


class TravelAgencyApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.geometry("1180x720")
        self.minsize(1050, 650)
        self.configure(bg="#eef3f8")
        self.user_role = None
        self.user_id = None
        self.client_id = None
        self.setup_style()
        self.show_login_window()

    # ---------- COMMON UI ----------
    def setup_style(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background="#eef3f8")
        style.configure("Card.TFrame", background="#ffffff", relief="flat")
        style.configure("TLabel", background="#eef3f8", font=("Segoe UI", 10))
        style.configure("Card.TLabel", background="#ffffff", font=("Segoe UI", 10))
        style.configure("Title.TLabel", background="#2f5d8c", foreground="white", font=("Segoe UI", 22, "bold"))
        style.configure("Subtitle.TLabel", background="#2f5d8c", foreground="white", font=("Segoe UI", 10))
        style.configure("Accent.TButton", font=("Segoe UI", 10, "bold"), padding=7)
        style.configure("TButton", font=("Segoe UI", 10), padding=6)
        style.configure("Treeview", rowheight=28, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        style.configure("TNotebook.Tab", padding=(15, 7), font=("Segoe UI", 10, "bold"))

    def api(self, method, path, **kwargs):
        try:
            return requests.request(method, API_URL + path, timeout=6, **kwargs)
        except requests.exceptions.ConnectionError:
            messagebox.showerror("Ошибка подключения", "Сервер не запущен. Запусти: uvicorn server.main:app --reload")
        except requests.exceptions.RequestException as exc:
            messagebox.showerror("Ошибка", str(exc))
        return None

    def clear_window(self):
        for widget in self.winfo_children():
            widget.destroy()

    def make_header(self, title, subtitle):
        header = ttk.Frame(self, padding=18)
        header.configure(style="TFrame")
        header.pack(fill="x")
        inner = tk.Frame(header, bg="#2f5d8c", padx=24, pady=16)
        inner.pack(fill="x")
        ttk.Label(inner, text=title, style="Title.TLabel").pack(anchor="w")
        ttk.Label(inner, text=subtitle, style="Subtitle.TLabel").pack(anchor="w", pady=(5, 0))

    def card(self, parent, padding=16):
        return ttk.Frame(parent, style="Card.TFrame", padding=padding)

    def labeled_entry(self, parent, label, row, show=None, width=35, value=""):
        ttk.Label(parent, text=label, style="Card.TLabel").grid(row=row, column=0, sticky="w", pady=6, padx=(0, 10))
        entry = ttk.Entry(parent, width=width, show=show)
        entry.grid(row=row, column=1, sticky="ew", pady=6)
        if value:
            entry.insert(0, value)
        return entry

    def create_tree(self, parent, columns, headings, widths):
        box = ttk.Frame(parent)
        box.pack(fill="both", expand=True, padx=10, pady=10)
        tree = ttk.Treeview(box, columns=columns, show="headings")
        yscroll = ttk.Scrollbar(box, orient="vertical", command=tree.yview)
        xscroll = ttk.Scrollbar(box, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)
        for col, heading, width in zip(columns, headings, widths):
            tree.heading(col, text=heading)
            tree.column(col, width=width, anchor="w")
        tree.grid(row=0, column=0, sticky="nsew")
        yscroll.grid(row=0, column=1, sticky="ns")
        xscroll.grid(row=1, column=0, sticky="ew")
        box.rowconfigure(0, weight=1)
        box.columnconfigure(0, weight=1)
        return tree

    def fill_tree(self, tree, rows, columns):
        for item in tree.get_children():
            tree.delete(item)
        for row in rows:
            tree.insert("", "end", values=[row.get(col, "") for col in columns])

    def selected_id(self, tree):
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Выбор записи", "Выберите строку в таблице")
            return None
        return tree.item(selected[0], "values")[0]

    def logout_bar(self):
        bar = ttk.Frame(self, padding=(18, 0, 18, 10))
        bar.pack(fill="x")
        ttk.Button(bar, text="Выйти", command=self.show_login_window).pack(side="right")

    # ---------- AUTH ----------
    def show_login_window(self):
        self.clear_window()
        self.title("Travel Agency — вход")
        self.make_header("Travel Agency", "Авторизация администратора и клиента")
        wrap = ttk.Frame(self, padding=30)
        wrap.pack(expand=True)
        form = self.card(wrap, padding=30)
        form.pack()
        ttk.Label(form, text="Вход в систему", style="Card.TLabel", font=("Segoe UI", 18, "bold")).grid(row=0, column=0, columnspan=2, pady=(0, 18))
        self.login_entry = self.labeled_entry(form, "Логин", 1)
        self.password_entry = self.labeled_entry(form, "Пароль", 2, show="*")
        ttk.Button(form, text="Войти", style="Accent.TButton", command=self.login).grid(row=3, column=0, columnspan=2, sticky="ew", pady=(15, 8))
        ttk.Button(form, text="Регистрация клиента", command=self.show_register_window).grid(row=4, column=0, columnspan=2, sticky="ew")
        ttk.Label(form, text="Администратор: admin / admin123", style="Card.TLabel").grid(row=5, column=0, columnspan=2, pady=(18, 0))
        form.columnconfigure(1, weight=1)

    def show_register_window(self):
        self.clear_window()
        self.title("Travel Agency — регистрация")
        self.make_header("Регистрация клиента", "После регистрации клиент сможет выбрать тур и оформить бронирование")
        wrap = ttk.Frame(self, padding=25)
        wrap.pack(expand=True)
        form = self.card(wrap, padding=28)
        form.pack()
        self.reg_entries = {}
        for i, label in enumerate(["Логин", "Пароль", "ФИО", "Телефон", "Email", "Паспорт"]):
            self.reg_entries[label] = self.labeled_entry(form, label, i, show="*" if label == "Пароль" else None, width=42)
        ttk.Button(form, text="Зарегистрироваться", style="Accent.TButton", command=self.register_client).grid(row=6, column=0, columnspan=2, sticky="ew", pady=(15, 8))
        ttk.Button(form, text="Назад", command=self.show_login_window).grid(row=7, column=0, columnspan=2, sticky="ew")

    def register_client(self):
        data = {
            "login": self.reg_entries["Логин"].get().strip(),
            "password": self.reg_entries["Пароль"].get().strip(),
            "full_name": self.reg_entries["ФИО"].get().strip(),
            "phone": self.reg_entries["Телефон"].get().strip(),
            "email": self.reg_entries["Email"].get().strip(),
            "passport_number": self.reg_entries["Паспорт"].get().strip(),
        }
        if not all(data.values()):
            messagebox.showwarning("Проверка", "Заполните все поля")
            return
        response = self.api("POST", "/auth/register-client", json=data)
        if response and response.status_code == 200:
            messagebox.showinfo("Готово", "Клиент зарегистрирован. Теперь можно войти.")
            self.show_login_window()
        elif response:
            messagebox.showerror("Ошибка", response.json().get("detail", response.text))

    def login(self):
        data = {"login": self.login_entry.get().strip(), "password": self.password_entry.get().strip()}
        if not data["login"] or not data["password"]:
            messagebox.showwarning("Проверка", "Введите логин и пароль")
            return
        response = self.api("POST", "/auth/login", json=data)
        if response and response.status_code == 200:
            result = response.json()
            self.user_role = result["role"]
            self.user_id = result["user_id"]
            self.client_id = result.get("client_id")
            if self.user_role == "admin":
                self.show_admin_window()
            else:
                self.show_client_window()
        elif response:
            messagebox.showerror("Ошибка", "Неверный логин или пароль")

    # ---------- ADMIN ----------
    def show_admin_window(self):
        self.clear_window()
        self.title("Travel Agency — администратор")
        self.make_header("Панель администратора", "Клиенты, бронирования, туры, маршруты, отели, перевозчики, договоры и статистика")
        self.logout_bar()
        tabs = ttk.Notebook(self)
        tabs.pack(fill="both", expand=True, padx=18, pady=(0, 18))
        pages = {}
        for name in ["Клиенты", "Бронирования", "Туры", "Маршруты", "Отзывы", "Отели", "Перевозчики", "Договоры", "Статистика"]:
            pages[name] = ttk.Frame(tabs, padding=10)
            tabs.add(pages[name], text=name)
        self.admin_clients_tab(pages["Клиенты"])
        self.admin_bookings_tab(pages["Бронирования"])
        self.admin_tours_tab(pages["Туры"])
        self.admin_routes_tab(pages["Маршруты"])
        self.admin_reviews_tab(pages["Отзывы"])
        self.admin_simple_tab(pages["Отели"], "hotels", "/hotels", ["id", "name", "country", "city", "stars", "address"], ["ID", "Название", "Страна", "Город", "Звезды", "Адрес"], [50, 190, 130, 130, 80, 260], {"Название": "name", "Страна": "country", "Город": "city", "Звезды": "stars", "Адрес": "address"})
        self.admin_simple_tab(pages["Перевозчики"], "carriers", "/carriers", ["id", "name", "transport_type", "phone"], ["ID", "Название", "Тип транспорта", "Телефон"], [50, 250, 160, 180], {"Название": "name", "Тип транспорта": "transport_type", "Телефон": "phone"})
        self.admin_contracts_tab(pages["Договоры"])
        self.admin_stats_tab(pages["Статистика"])

    def admin_clients_tab(self, tab):
        panel = ttk.Frame(tab, padding=10)
        panel.pack(fill="x")
        ttk.Label(panel, text="Поиск по ФИО").pack(side="left")
        self.client_search = ttk.Entry(panel, width=35)
        self.client_search.pack(side="left", padx=8)
        ttk.Button(panel, text="Найти", command=self.load_clients).pack(side="left")
        ttk.Button(panel, text="Обновить", command=self.load_clients).pack(side="left", padx=8)
        ttk.Button(panel, text="Удалить клиента", command=self.delete_client).pack(side="right")
        self.clients_tree = self.create_tree(tab, ["id", "full_name", "phone", "email", "passport_number"], ["ID", "ФИО", "Телефон", "Email", "Паспорт"], [60, 260, 160, 220, 150])
        self.load_clients()

    def load_clients(self):
        params = {}
        if hasattr(self, "client_search") and self.client_search.get().strip():
            params["name"] = self.client_search.get().strip()
        r = self.api("GET", "/clients", params=params)
        if r and r.status_code == 200:
            self.fill_tree(self.clients_tree, r.json(), ["id", "full_name", "phone", "email", "passport_number"])

    def delete_client(self):
        item_id = self.selected_id(self.clients_tree)
        if item_id and messagebox.askyesno("Удаление", "Удалить выбранного клиента?"):
            r = self.api("DELETE", f"/clients/{item_id}")
            if r and r.status_code == 200:
                self.load_clients()

    def admin_bookings_tab(self, tab):
        panel = ttk.Frame(tab, padding=10)
        panel.pack(fill="x")
        ttk.Label(panel, text="Статус").pack(side="left")
        self.booking_status = ttk.Combobox(panel, values=[""] + STATUSES, width=15, state="readonly")
        self.booking_status.pack(side="left", padx=8)
        ttk.Button(panel, text="Фильтр", command=self.load_bookings).pack(side="left")
        ttk.Button(panel, text="Подтвердить", command=lambda: self.update_booking_status("confirmed")).pack(side="left", padx=8)
        ttk.Button(panel, text="Отменить", command=lambda: self.update_booking_status("cancelled")).pack(side="left")
        ttk.Button(panel, text="Удалить", command=self.delete_booking).pack(side="right")
        self.bookings_tree = self.create_tree(
            tab,
            ["id", "client_full_name", "client_phone", "tour_name", "booking_date", "status", "total_price"],
            ["ID", "ФИО клиента", "Телефон", "Тур", "Дата", "Статус", "Сумма"],
            [60, 180, 140, 240, 170, 120, 120]
        )
        self.load_bookings()

    def load_bookings(self):
        params = {}
        if hasattr(self, "booking_status") and self.booking_status.get():
            params["status"] = self.booking_status.get()
        r = self.api("GET", "/bookings", params=params)
        if r and r.status_code == 200:
            self.fill_tree(
                self.bookings_tree,
                r.json(),
                ["id", "client_full_name", "client_phone", "tour_name", "booking_date", "status", "total_price"]
            )

    def update_booking_status(self, status):
        item_id = self.selected_id(self.bookings_tree)
        if item_id:
            r = self.api("PUT", f"/bookings/{item_id}", json={"status": status})
            if r and r.status_code == 200:
                self.load_bookings()

    def delete_booking(self):
        item_id = self.selected_id(self.bookings_tree)
        if item_id and messagebox.askyesno("Удаление", "Удалить бронирование?"):
            r = self.api("DELETE", f"/bookings/{item_id}")
            if r and r.status_code == 200:
                self.load_bookings()

    def admin_tours_tab(self, tab):
        form = ttk.LabelFrame(tab, text="Туры: добавление через ORM или SQL", padding=12)
        form.pack(fill="x", padx=10, pady=10)
        self.tour_entries = {}
        labels = ["Название", "Тип", "Описание", "Цена", "Дата начала", "Дата окончания"]
        for i, label in enumerate(labels):
            ttk.Label(form, text=label).grid(row=i // 3, column=(i % 3) * 2, sticky="w", padx=(0, 6), pady=6)
            if label == "Тип":
                e = ttk.Combobox(form, values=TOUR_TYPES, state="readonly", width=22)
                e.set("tourist")
            else:
                e = ttk.Entry(form, width=25)
            e.grid(row=i // 3, column=(i % 3) * 2 + 1, sticky="ew", padx=(0, 12), pady=6)
            self.tour_entries[label] = e
        self.tour_entries["Дата начала"].insert(0, "2026-07-01")
        self.tour_entries["Дата окончания"].insert(0, "2026-07-07")
        self.tour_mode = tk.StringVar(value="orm")
        ttk.Radiobutton(form, text="ORM", variable=self.tour_mode, value="orm").grid(row=2, column=0, sticky="w")
        ttk.Radiobutton(form, text="SQL", variable=self.tour_mode, value="sql").grid(row=2, column=1, sticky="w")
        ttk.Button(form, text="Добавить", style="Accent.TButton", command=self.add_tour).grid(row=2, column=2, columnspan=2, sticky="ew")
        ttk.Button(form, text="Удалить", command=self.delete_tour).grid(row=2, column=4, sticky="ew", padx=6)
        ttk.Button(form, text="Обновить", command=self.load_admin_tours).grid(row=2, column=5, sticky="ew")
        self.admin_tours_tree = self.create_tree(tab, ["id", "name", "type", "price", "start_date", "end_date", "description"], ["ID", "Название", "Тип", "Цена", "Начало", "Окончание", "Описание"], [55, 230, 110, 90, 115, 115, 300])
        self.load_admin_tours()

    def tour_data_from_form(self):
        return {
            "name": self.tour_entries["Название"].get().strip(),
            "type": self.tour_entries["Тип"].get().strip(),
            "description": self.tour_entries["Описание"].get().strip(),
            "price": self.tour_entries["Цена"].get().strip(),
            "start_date": self.tour_entries["Дата начала"].get().strip(),
            "end_date": self.tour_entries["Дата окончания"].get().strip(),
        }

    def add_tour(self):
        data = self.tour_data_from_form()
        if not all([data["name"], data["type"], data["price"], data["start_date"], data["end_date"]]):
            messagebox.showwarning("Проверка", "Заполните обязательные поля тура")
            return
        r = self.api("POST", "/tours", params={"mode": self.tour_mode.get()}, json=data)
        if r and r.status_code == 200:
            messagebox.showinfo("Готово", "Тур добавлен")
            self.load_admin_tours()
        elif r:
            messagebox.showerror("Ошибка", r.text)

    def load_admin_tours(self):
        r = self.api("GET", "/tours")
        if r and r.status_code == 200:
            self.fill_tree(self.admin_tours_tree, r.json(), ["id", "name", "type", "price", "start_date", "end_date", "description"])

    def delete_tour(self):
        item_id = self.selected_id(self.admin_tours_tree)
        if item_id and messagebox.askyesno("Удаление", "Удалить выбранный тур?"):
            r = self.api("DELETE", f"/tours/{item_id}", params={"mode": self.tour_mode.get()})
            if r and r.status_code == 200:
                self.load_admin_tours()

    def admin_routes_tab(self, tab):
        form = ttk.LabelFrame(tab, text="Маршрут тура", padding=12)
        form.pack(fill="x", padx=10, pady=10)
        self.route_entries = {}
        for i, label in enumerate(["ID тура", "Страна", "Город", "Порядок", "Описание"]):
            ttk.Label(form, text=label).grid(row=0, column=i * 2, sticky="w", padx=(0, 5))
            e = ttk.Entry(form, width=18)
            e.grid(row=0, column=i * 2 + 1, sticky="ew", padx=(0, 8))
            self.route_entries[label] = e
        ttk.Button(form, text="Добавить", style="Accent.TButton", command=self.add_route).grid(row=1, column=0, columnspan=2, sticky="ew", pady=8)
        ttk.Button(form, text="Удалить", command=self.delete_route).grid(row=1, column=2, columnspan=2, sticky="ew", pady=8)
        ttk.Button(form, text="Обновить", command=self.load_routes).grid(row=1, column=4, columnspan=2, sticky="ew", pady=8)
        self.routes_tree = self.create_tree(tab, ["id", "tour_id", "country", "city", "visit_order", "description"], ["ID", "Тур", "Страна", "Город", "Порядок", "Описание"], [50, 70, 140, 140, 90, 350])
        self.load_routes()

    def add_route(self):
        data = {"tour_id": self.route_entries["ID тура"].get(), "country": self.route_entries["Страна"].get(), "city": self.route_entries["Город"].get(), "visit_order": self.route_entries["Порядок"].get(), "description": self.route_entries["Описание"].get()}
        r = self.api("POST", "/routes", json=data)
        if r and r.status_code == 200:
            self.load_routes()
        elif r:
            messagebox.showerror("Ошибка", r.text)

    def load_routes(self):
        r = self.api("GET", "/routes")
        if r and r.status_code == 200:
            self.fill_tree(self.routes_tree, r.json(), ["id", "tour_id", "country", "city", "visit_order", "description"])

    def delete_route(self):
        item_id = self.selected_id(self.routes_tree)
        if item_id:
            r = self.api("DELETE", f"/routes/{item_id}")
            if r and r.status_code == 200:
                self.load_routes()

    def admin_reviews_tab(self, tab):
        ttk.Button(tab, text="Обновить отзывы", command=self.load_reviews).pack(anchor="w", padx=10, pady=10)
        self.reviews_tree = self.create_tree(tab, ["id", "client_id", "tour_id", "rating", "text", "created_at"], ["ID", "Клиент", "Тур", "Оценка", "Текст", "Дата"], [50, 80, 80, 80, 430, 220])
        self.load_reviews()

    def load_reviews(self):
        r = self.api("GET", "/reviews")
        if r and r.status_code == 200:
            self.fill_tree(self.reviews_tree, r.json(), ["id", "client_id", "tour_id", "rating", "text", "created_at"])

    def admin_simple_tab(self, tab, key, path, columns, headings, widths, fields):
        form = ttk.LabelFrame(tab, text="Добавление / удаление", padding=12)
        form.pack(fill="x", padx=10, pady=10)
        entries = {}
        for i, (label, field) in enumerate(fields.items()):
            ttk.Label(form, text=label).grid(row=0, column=i * 2, sticky="w", padx=(0, 5))
            e = ttk.Entry(form, width=18)
            e.grid(row=0, column=i * 2 + 1, sticky="ew", padx=(0, 8))
            entries[field] = e
        tree = self.create_tree(tab, columns, headings, widths)
        setattr(self, f"{key}_entries", entries)
        setattr(self, f"{key}_tree", tree)

        def load():
            r = self.api("GET", path)
            if r and r.status_code == 200:
                self.fill_tree(tree, r.json(), columns)

        def add():
            data = {field: entry.get().strip() for field, entry in entries.items()}
            r = self.api("POST", path, json=data)
            if r and r.status_code == 200:
                load()
            elif r:
                messagebox.showerror("Ошибка", r.text)

        def delete():
            item_id = self.selected_id(tree)
            if item_id:
                r = self.api("DELETE", f"{path}/{item_id}")
                if r and r.status_code == 200:
                    load()

        ttk.Button(form, text="Добавить", style="Accent.TButton", command=add).grid(row=1, column=0, columnspan=2, sticky="ew", pady=8)
        ttk.Button(form, text="Удалить", command=delete).grid(row=1, column=2, columnspan=2, sticky="ew", pady=8)
        ttk.Button(form, text="Обновить", command=load).grid(row=1, column=4, columnspan=2, sticky="ew", pady=8)
        load()

    def admin_contracts_tab(self, tab):
        tabs = ttk.Notebook(tab)
        tabs.pack(fill="both", expand=True)
        hotel_tab = ttk.Frame(tabs, padding=10)
        carrier_tab = ttk.Frame(tabs, padding=10)
        tabs.add(hotel_tab, text="Договоры с отелями")
        tabs.add(carrier_tab, text="Договоры с перевозчиками")
        self.admin_simple_tab(hotel_tab, "hotel_contracts", "/hotel-contracts", ["id", "hotel_id", "contract_number", "start_date", "end_date", "terms"], ["ID", "ID отеля", "Номер", "Начало", "Окончание", "Условия"], [50, 90, 150, 120, 120, 350], {"ID отеля": "hotel_id", "Номер": "contract_number", "Начало": "start_date", "Окончание": "end_date", "Условия": "terms"})
        self.admin_simple_tab(carrier_tab, "carrier_contracts", "/carrier-contracts", ["id", "carrier_id", "contract_number", "start_date", "end_date", "terms"], ["ID", "ID перевозчика", "Номер", "Начало", "Окончание", "Условия"], [50, 120, 150, 120, 120, 350], {"ID перевозчика": "carrier_id", "Номер": "contract_number", "Начало": "start_date", "Окончание": "end_date", "Условия": "terms"})

    def admin_stats_tab(self, tab):
        self.stats_frame = ttk.Frame(tab, padding=25)
        self.stats_frame.pack(fill="both", expand=True)
        ttk.Button(self.stats_frame, text="Обновить статистику", style="Accent.TButton", command=self.load_stats).pack(anchor="w")
        self.stats_text = tk.Text(self.stats_frame, height=12, font=("Segoe UI", 13), bg="white", relief="flat", padx=18, pady=18)
        self.stats_text.pack(fill="x", pady=15)
        self.load_stats()

    def load_stats(self):
        r = self.api("GET", "/stats")
        if r and r.status_code == 200:
            s = r.json()
            text = (
                f"Всего клиентов: {s['clients']}\n"
                f"Всего туров: {s['tours']}\n"
                f"Всего бронирований: {s['bookings']}\n"
                f"Всего отзывов: {s['reviews']}\n"
                f"Отелей: {s['hotels']}\n"
                f"Перевозчиков: {s['carriers']}\n"
                f"Самый популярный тур: {s['popular_tour']} ({s['popular_tour_bookings']} бронир.)\n"
            )
            self.stats_text.delete("1.0", tk.END)
            self.stats_text.insert(tk.END, text)

    # ---------- CLIENT ----------
    def show_client_window(self):
        self.clear_window()
        self.title("Travel Agency — клиент")
        self.make_header("Личный кабинет клиента", "Выбор тура, мои бронирования и отзывы")
        self.logout_bar()
        tabs = ttk.Notebook(self)
        tabs.pack(fill="both", expand=True, padx=18, pady=(0, 18))
        tours = ttk.Frame(tabs, padding=10)
        bookings = ttk.Frame(tabs, padding=10)
        reviews = ttk.Frame(tabs, padding=10)
        tabs.add(tours, text="Выбор тура")
        tabs.add(bookings, text="Мои бронирования")
        tabs.add(reviews, text="Отзывы")
        self.client_tours_tab(tours)
        self.client_bookings_tab(bookings)
        self.client_reviews_tab(reviews)

    def client_tours_tab(self, tab):
        # Верхняя панель поиска
        panel = ttk.LabelFrame(tab, text="Поиск и фильтрация туров", padding=12)
        panel.pack(fill="x", padx=10, pady=10)

        ttk.Label(panel, text="Название").pack(side="left")
        self.ct_name = ttk.Entry(panel, width=22)
        self.ct_name.pack(side="left", padx=8)

        ttk.Label(panel, text="Тип").pack(side="left")
        self.ct_type = ttk.Combobox(
            panel,
            values=[""] + TOUR_TYPES,
            width=15,
            state="readonly"
        )
        self.ct_type.pack(side="left", padx=8)

        ttk.Label(panel, text="Мин. цена").pack(side="left")
        self.ct_min_price = ttk.Entry(panel, width=10)
        self.ct_min_price.pack(side="left", padx=8)

        ttk.Label(panel, text="Макс. цена").pack(side="left")
        self.ct_max_price = ttk.Entry(panel, width=10)
        self.ct_max_price.pack(side="left", padx=8)

        ttk.Button(
            panel,
            text="Найти",
            command=self.load_client_tours
        ).pack(side="left", padx=8)

        ttk.Button(
            panel,
            text="Показать все",
            command=self.reset_client_tour_filter
        ).pack(side="left", padx=4)

        ttk.Button(
            panel,
            text="Забронировать выбранный тур",
            style="Accent.TButton",
            command=self.book_selected_tour
        ).pack(side="right")

        # Отдельная область вывода: сначала здесь видны все туры,
        # после поиска здесь же показываются результаты фильтрации.
        tours_frame = ttk.LabelFrame(tab, text="Все туры / результаты поиска", padding=10)
        tours_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # ID клиенту не показываем. Он хранится скрыто в iid строки Treeview.
        self.client_tours_tree = self.create_tree(
            tours_frame,
            ["name", "type", "price", "start_date", "end_date", "description"],
            ["Название", "Тип", "Цена", "Начало", "Окончание", "Описание"],
            [280, 120, 100, 120, 120, 380]
        )

        # При открытии вкладки сразу загружаются все туры.
        self.load_client_tours()

    def load_client_tours(self):
        params = {}

        name = self.ct_name.get().strip()
        tour_type = self.ct_type.get().strip()
        min_price = self.ct_min_price.get().strip()
        max_price = self.ct_max_price.get().strip()

        if name:
            params["name"] = name

        if tour_type:
            params["type"] = tour_type

        if min_price:
            try:
                params["min_price"] = float(min_price)
            except ValueError:
                messagebox.showwarning("Ошибка", "Минимальная цена должна быть числом")
                return

        if max_price:
            try:
                params["max_price"] = float(max_price)
            except ValueError:
                messagebox.showwarning("Ошибка", "Максимальная цена должна быть числом")
                return

        r = self.api("GET", "/tours", params=params)

        if r and r.status_code == 200:
            tours = r.json()

            # Полностью очищаем таблицу перед новой загрузкой.
            for item in self.client_tours_tree.get_children():
                self.client_tours_tree.delete(item)

            # Заполняем таблицу без видимого ID.
            # ID тура сохраняется в iid, чтобы потом можно было оформить бронирование.
            for tour in tours:
                self.client_tours_tree.insert(
                    "",
                    "end",
                    iid=str(tour["id"]),
                    values=[
                        tour.get("name", ""),
                        tour.get("type", ""),
                        tour.get("price", ""),
                        tour.get("start_date", ""),
                        tour.get("end_date", ""),
                        tour.get("description", "")
                    ]
                )

            if len(tours) == 0:
                messagebox.showinfo("Поиск", "По заданным параметрам туры не найдены")

        elif r:
            messagebox.showerror("Ошибка", r.text)

    def reset_client_tour_filter(self):
        self.ct_name.delete(0, tk.END)
        self.ct_type.set("")
        self.ct_min_price.delete(0, tk.END)
        self.ct_max_price.delete(0, tk.END)

        # После очистки фильтров снова отображаются все туры.
        self.load_client_tours()

    def book_selected_tour(self):
        if not self.client_id:
            messagebox.showerror("Ошибка", "У пользователя не найден client_id")
            return

        selected = self.client_tours_tree.selection()

        if not selected:
            messagebox.showwarning("Выбор тура", "Выберите тур из списка")
            return

        # ID тура скрыт от клиента, но хранится в iid выбранной строки.
        tour_id = int(selected[0])

        r = self.api(
            "POST",
            "/bookings",
            json={
                "client_id": self.client_id,
                "tour_id": tour_id,
                "status": "created"
            }
        )

        if r and r.status_code == 200:
            messagebox.showinfo("Готово", "Тур забронирован")
            self.load_client_bookings()
        elif r:
            messagebox.showerror("Ошибка", r.text)

    def client_bookings_tab(self, tab):
        ttk.Button(tab, text="Обновить", command=self.load_client_bookings).pack(anchor="w", padx=10, pady=10)
        self.client_bookings_tree = self.create_tree(
            tab,
            ["id", "tour_name", "booking_date", "status", "total_price"],
            ["ID", "Тур", "Дата", "Статус", "Сумма"],
            [60, 300, 170, 130, 120]
        )
        self.load_client_bookings()

    def load_client_bookings(self):
        if not hasattr(self, "client_bookings_tree") or not self.client_id:
            return
        r = self.api("GET", f"/bookings/client/{self.client_id}")
        if r and r.status_code == 200:
            self.fill_tree(
                self.client_bookings_tree,
                r.json(),
                ["id", "tour_name", "booking_date", "status", "total_price"]
            )

    def client_reviews_tab(self, tab):
        form = ttk.LabelFrame(tab, text="Оставить отзыв", padding=12)
        form.pack(fill="x", padx=10, pady=10)
        ttk.Label(form, text="ID тура").grid(row=0, column=0, sticky="w")
        self.rev_tour_id = ttk.Entry(form, width=12)
        self.rev_tour_id.grid(row=0, column=1, padx=8)
        ttk.Label(form, text="Оценка 1-5").grid(row=0, column=2, sticky="w")
        self.rev_rating = ttk.Combobox(form, values=[1, 2, 3, 4, 5], width=8, state="readonly")
        self.rev_rating.set(5)
        self.rev_rating.grid(row=0, column=3, padx=8)
        ttk.Label(form, text="Текст").grid(row=0, column=4, sticky="w")
        self.rev_text = ttk.Entry(form, width=45)
        self.rev_text.grid(row=0, column=5, padx=8)
        ttk.Button(form, text="Добавить отзыв", style="Accent.TButton", command=self.add_review).grid(row=0, column=6, padx=8)
        ttk.Button(tab, text="Обновить мои отзывы", command=self.load_client_reviews).pack(anchor="w", padx=10)
        self.client_reviews_tree = self.create_tree(tab, ["id", "client_id", "tour_id", "rating", "text", "created_at"], ["ID", "Клиент", "Тур", "Оценка", "Текст", "Дата"], [50, 80, 80, 80, 430, 220])
        self.load_client_reviews()

    def add_review(self):
        data = {"client_id": self.client_id, "tour_id": self.rev_tour_id.get().strip(), "rating": self.rev_rating.get(), "text": self.rev_text.get().strip()}
        if not data["tour_id"]:
            messagebox.showwarning("Проверка", "Укажите ID тура")
            return
        r = self.api("POST", "/reviews", json=data)
        if r and r.status_code == 200:
            messagebox.showinfo("Готово", "Отзыв добавлен")
            self.load_client_reviews()
        elif r:
            messagebox.showerror("Ошибка", r.text)

    def load_client_reviews(self):
        if not hasattr(self, "client_reviews_tree") or not self.client_id:
            return
        r = self.api("GET", "/reviews", params={"client_id": self.client_id})
        if r and r.status_code == 200:
            self.fill_tree(self.client_reviews_tree, r.json(), ["id", "client_id", "tour_id", "rating", "text", "created_at"])


if __name__ == "__main__":
    app = TravelAgencyApp()
    app.mainloop()
