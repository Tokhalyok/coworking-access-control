import sys
from datetime import datetime
from PyQt5 import QtWidgets, QtGui, QtCore
from API import CoworkingAPI

ROLES = {0: "User", 1: "Admin", 2: "SuperAdmin"}
ROLE_COLORS = {0: "#4CAF50", 1: "#2196F3", 2: "#9C27B0"}
ROLE_BG = {0: "#E8F5E9", 1: "#E3F2FD", 2: "#F3E5F5"}


def is_valid_address(adr):
    return adr.startswith("0x") and len(adr) == 42


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.api = CoworkingAPI()
        self.accounts = self.api.get_accounts()
        self.setWindowTitle("🏢 Coworking Access Control")
        self.setMinimumSize(1100, 750)
        self.init_ui()

    def init_ui(self):
        central = QtWidgets.QWidget()
        central.setStyleSheet("background: #F0F4F8;")
        self.setCentralWidget(central)

        main = QtWidgets.QVBoxLayout(central)
        main.setSpacing(0)
        main.setContentsMargins(0, 0, 0, 0)

        # ── Шапка ──
        main.addWidget(self.build_header())

        # ── Контент ──
        content = QtWidgets.QWidget()
        content.setStyleSheet("background: #F0F4F8;")
        content_layout = QtWidgets.QVBoxLayout(content)
        content_layout.setContentsMargins(16, 16, 16, 16)
        content_layout.setSpacing(12)

        # ── Вкладки ──
        self.tabs = QtWidgets.QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background: transparent;
            }
            QTabBar {
                background: transparent;
            }
            QTabBar::tab {
                background: white;
                color: #546E7A;
                border: 1px solid #CFD8DC;
                padding: 10px 20px;
                margin-right: 4px;
                border-radius: 8px 8px 0 0;
                font-size: 12px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background: #1a237e;
                color: white;
                border-color: #1a237e;
            }
            QTabBar::tab:hover:!selected {
                background: #E8EAF6;
                color: #1a237e;
            }
        """)

        self.tabs.addTab(self.tab_search(),   "🔍  Поиск")
        self.tabs.addTab(self.tab_create(),   "➕  Регистрация")
        self.tabs.addTab(self.tab_update(),   "✏️  Редактировать")
        self.tabs.addTab(self.tab_access(),   "🔑  Доступ")
        self.tabs.addTab(self.tab_door(),     "🚪  Вход")
        self.tabs.addTab(self.tab_stats(),    "📊  Статистика")
        self.tabs.addTab(self.tab_log(),      "📋  Журнал")

        content_layout.addWidget(self.tabs)
        main.addWidget(content)

    # ─────────────────────────────────────────
    # ШАПКА
    # ─────────────────────────────────────────

    def build_header(self):
        frame = QtWidgets.QFrame()
        frame.setFixedHeight(64)
        frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1a237e, stop:0.5 #283593, stop:1 #3949AB);
            }
        """)
        layout = QtWidgets.QHBoxLayout(frame)
        layout.setContentsMargins(20, 0, 20, 0)

        lbl_icon = QtWidgets.QLabel("🏢")
        lbl_icon.setStyleSheet("font-size: 24px;")

        lbl_title = QtWidgets.QLabel("Coworking Access Control")
        lbl_title.setStyleSheet(
            "color: white; font-size: 18px; font-weight: bold; margin-left: 8px;"
        )

        layout.addWidget(lbl_icon)
        layout.addWidget(lbl_title)
        layout.addStretch()

        # Статус индикаторы
        self.lbl_status    = self.make_header_badge("⚪", "Подключение...")
        self.lbl_address   = self.make_header_badge("📍", "—")
        self.lbl_log_count = self.make_header_badge("📝", "Журнал: 0")

        btn_refresh = QtWidgets.QPushButton("⟳  Обновить")
        btn_refresh.setStyleSheet("""
            QPushButton {
                background: rgba(255,255,255,0.15);
                color: white; border: 1px solid rgba(255,255,255,0.3);
                border-radius: 6px; padding: 6px 14px;
                font-weight: bold; font-size: 12px;
            }
            QPushButton:hover { background: rgba(255,255,255,0.25); }
        """)
        btn_refresh.clicked.connect(self.refresh_header)

        for w in [self.lbl_status, self.lbl_address, self.lbl_log_count, btn_refresh]:
            layout.addWidget(w)

        self.refresh_header()
        return frame

    def make_header_badge(self, icon, text):
        lbl = QtWidgets.QLabel(f"{icon}  {text}")
        lbl.setStyleSheet("""
            color: rgba(255,255,255,0.85);
            font-size: 11px; font-weight: bold;
            background: rgba(255,255,255,0.1);
            border-radius: 4px; padding: 4px 10px;
            margin-right: 6px;
        """)
        return lbl

    def refresh_header(self):
        try:
            connected = self.api.is_connected()
            self.lbl_status.setText(
                "🟢  Подключено" if connected else "🔴  Нет подключения"
            )
            addr = self.accounts[0]
            self.lbl_address.setText(f"📍  {addr[:10]}...{addr[-4:]}")
            count = self.api.get_log_count()
            self.lbl_log_count.setText(f"📝  Журнал: {count}")
        except:
            self.lbl_status.setText("🔴  Ошибка")

    # ─────────────────────────────────────────
    # ВКЛАДКА: Поиск (READ)
    # ─────────────────────────────────────────

    def tab_search(self):
        w = QtWidgets.QWidget()
        w.setStyleSheet("background: transparent;")
        layout = QtWidgets.QHBoxLayout(w)
        layout.setContentsMargins(0, 12, 0, 0)
        layout.setSpacing(16)

        # Левая — форма поиска
        left = self.make_card()
        left.setMaximumWidth(380)
        ll = QtWidgets.QVBoxLayout(left)

        lbl_title = QtWidgets.QLabel("🔍  Найти пользователя")
        lbl_title.setStyleSheet(
            "font-size:15px; font-weight:bold; color:#1a237e; margin-bottom:8px;"
        )

        lbl_hint = QtWidgets.QLabel(
            "Введите адрес кошелька, имя или номер телефона"
        )
        lbl_hint.setStyleSheet("color:#78909C; font-size:11px;")
        lbl_hint.setWordWrap(True)

        self.inp_search = self.make_input("0x...  или  Алибек  или  +77001234567")
        btn = self.make_btn("🔍  Найти", "#1a237e")
        btn.clicked.connect(self.search_user)

        ll.addWidget(lbl_title)
        ll.addWidget(lbl_hint)
        ll.addSpacing(8)
        ll.addWidget(self.inp_search)
        ll.addWidget(btn)
        ll.addStretch()

        # Правая — карточка результата
        right = self.make_card()
        rl = QtWidgets.QVBoxLayout(right)

        lbl_card_title = QtWidgets.QLabel("Информация о пользователе")
        lbl_card_title.setStyleSheet(
            "font-size:14px; font-weight:bold; color:#1a237e; margin-bottom:8px;"
        )

        # Большой аватар с инициалами
        self.lbl_avatar = QtWidgets.QLabel("?")
        self.lbl_avatar.setFixedSize(80, 80)
        self.lbl_avatar.setAlignment(QtCore.Qt.AlignCenter)
        self.lbl_avatar.setStyleSheet("""
            background: #E8EAF6; border-radius: 40px;
            font-size: 28px; font-weight: bold; color: #1a237e;
        """)

        avatar_layout = QtWidgets.QHBoxLayout()
        avatar_layout.addStretch()
        avatar_layout.addWidget(self.lbl_avatar)
        avatar_layout.addStretch()

        # Поля результата
        self.lbl_s_name    = self.make_info_row("👤", "Имя", "—")
        self.lbl_s_phone   = self.make_info_row("📱", "Телефон", "—")
        self.lbl_s_role    = self.make_info_row("🎭", "Роль", "—")
        self.lbl_s_access  = self.make_info_row("🔑", "Доступ", "—")
        self.lbl_s_balance = self.make_info_row("💰", "Баланс", "—")
        self.lbl_s_status  = self.make_info_row("✅", "Статус", "—")

        rl.addWidget(lbl_card_title)
        rl.addLayout(avatar_layout)
        rl.addSpacing(8)
        for row in [self.lbl_s_name, self.lbl_s_phone, self.lbl_s_role,
                    self.lbl_s_access, self.lbl_s_balance, self.lbl_s_status]:
            rl.addWidget(row)
        rl.addStretch()

        layout.addWidget(left)
        layout.addWidget(right)
        return w

    # ─────────────────────────────────────────
    # ВКЛАДКА: Регистрация (CREATE)
    # ─────────────────────────────────────────

    def tab_create(self):
        w = QtWidgets.QWidget()
        w.setStyleSheet("background: transparent;")
        layout = QtWidgets.QHBoxLayout(w)
        layout.setContentsMargins(0, 12, 0, 0)

        card = self.make_card()
        card.setMaximumWidth(500)
        cl = QtWidgets.QVBoxLayout(card)

        lbl_title = QtWidgets.QLabel("➕  Регистрация нового пользователя")
        lbl_title.setStyleSheet(
            "font-size:15px; font-weight:bold; color:#1a237e; margin-bottom:12px;"
        )

        self.inp_c_sender = self.make_input("Адрес Admin/SuperAdmin (0x...)")
        self.inp_c_adr    = self.make_input("Адрес нового пользователя (0x...)")
        self.inp_c_name   = self.make_input("Уникальное имя")
        self.inp_c_phone  = self.make_input("Номер телефона (+77001234567)")

        # Роль с цветными кнопками
        lbl_role = QtWidgets.QLabel("Роль пользователя:")
        lbl_role.setStyleSheet("font-size:12px; font-weight:bold; color:#37474F;")

        role_layout = QtWidgets.QHBoxLayout()
        self.btn_role_user  = self.make_role_btn("👤  User",  "#4CAF50", 0)
        self.btn_role_admin = self.make_role_btn("🛡  Admin", "#2196F3", 1)
        self.selected_role  = 0
        self.btn_role_user.setProperty("selected", True)
        self.btn_role_user.setStyleSheet(self.role_btn_selected_style("#4CAF50"))
        role_layout.addWidget(self.btn_role_user)
        role_layout.addWidget(self.btn_role_admin)

        btn = self.make_btn("➕  Зарегистрировать", "#43A047")
        btn.setFixedHeight(44)
        btn.clicked.connect(self.register_user)

        cl.addWidget(lbl_title)
        for inp in [self.inp_c_sender, self.inp_c_adr,
                    self.inp_c_name, self.inp_c_phone]:
            cl.addWidget(inp)
            cl.addSpacing(4)
        cl.addWidget(lbl_role)
        cl.addLayout(role_layout)
        cl.addSpacing(8)
        cl.addWidget(btn)
        cl.addStretch()

        layout.addWidget(card)
        layout.addStretch()
        return w

    # ─────────────────────────────────────────
    # ВКЛАДКА: Редактировать (UPDATE)
    # ─────────────────────────────────────────

    def tab_update(self):
        w = QtWidgets.QWidget()
        w.setStyleSheet("background: transparent;")
        layout = QtWidgets.QHBoxLayout(w)
        layout.setContentsMargins(0, 12, 0, 0)
        layout.setSpacing(16)

        # Левая — поиск для заполнения
        left = self.make_card()
        left.setMaximumWidth(380)
        ll = QtWidgets.QVBoxLayout(left)

        lbl_title = QtWidgets.QLabel("✏️  Редактирование пользователя")
        lbl_title.setStyleSheet(
            "font-size:15px; font-weight:bold; color:#1a237e; margin-bottom:8px;"
        )

        lbl_hint = QtWidgets.QLabel(
            "Шаг 1: найдите пользователя чтобы загрузить текущие данные"
        )
        lbl_hint.setStyleSheet("color:#78909C; font-size:11px;")
        lbl_hint.setWordWrap(True)

        self.inp_u_find = self.make_input("Адрес / Имя / Телефон")
        btn_find = self.make_btn("📂  Загрузить данные", "#607D8B")
        btn_find.clicked.connect(self.load_user_for_edit)

        ll.addWidget(lbl_title)
        ll.addWidget(lbl_hint)
        ll.addSpacing(8)
        ll.addWidget(self.inp_u_find)
        ll.addWidget(btn_find)
        ll.addStretch()

        # Правая — форма редактирования
        right = self.make_card()
        rl = QtWidgets.QVBoxLayout(right)

        lbl_title2 = QtWidgets.QLabel("Шаг 2: измените данные и сохраните")
        lbl_title2.setStyleSheet(
            "font-size:13px; font-weight:bold; color:#37474F; margin-bottom:8px;"
        )

        self.inp_u_sender = self.make_input("Адрес SuperAdmin (0x...)")
        self.inp_u_name   = self.make_input("Новое имя")
        self.inp_u_phone  = self.make_input("Новый телефон")

        lbl_role = QtWidgets.QLabel("Новая роль:")
        lbl_role.setStyleSheet("font-size:12px; font-weight:bold; color:#37474F;")

        role_layout = QtWidgets.QHBoxLayout()
        self.btn_u_role_user  = self.make_role_btn("👤  User",  "#4CAF50", 0, update=True)
        self.btn_u_role_admin = self.make_role_btn("🛡  Admin", "#2196F3", 1, update=True)
        self.selected_u_role  = 0
        self.btn_u_role_user.setProperty("selected", True)
        self.btn_u_role_user.setStyleSheet(self.role_btn_selected_style("#4CAF50"))
        role_layout.addWidget(self.btn_u_role_user)
        role_layout.addWidget(self.btn_u_role_admin)

        btn_save = self.make_btn("💾  Сохранить изменения", "#7B1FA2")
        btn_save.setFixedHeight(44)
        btn_save.clicked.connect(self.update_user)

        self.lbl_u_result = QtWidgets.QLabel("")
        self.lbl_u_result.setAlignment(QtCore.Qt.AlignCenter)
        self.lbl_u_result.setStyleSheet(
            "font-size:12px; font-weight:bold; padding:8px; border-radius:6px;"
        )

        rl.addWidget(lbl_title2)
        rl.addWidget(self.inp_u_sender)
        rl.addSpacing(4)
        rl.addWidget(self.inp_u_name)
        rl.addSpacing(4)
        rl.addWidget(self.inp_u_phone)
        rl.addSpacing(4)
        rl.addWidget(lbl_role)
        rl.addLayout(role_layout)
        rl.addSpacing(8)
        rl.addWidget(btn_save)
        rl.addWidget(self.lbl_u_result)
        rl.addStretch()

        layout.addWidget(left)
        layout.addWidget(right)
        return w

    # ─────────────────────────────────────────
    # ВКЛАДКА: Доступ
    # ─────────────────────────────────────────

    def tab_access(self):
        w = QtWidgets.QWidget()
        w.setStyleSheet("background: transparent;")
        layout = QtWidgets.QHBoxLayout(w)
        layout.setContentsMargins(0, 12, 0, 0)
        layout.setSpacing(16)

        card = self.make_card()
        card.setMaximumWidth(480)
        cl = QtWidgets.QVBoxLayout(card)

        lbl_title = QtWidgets.QLabel("🔑  Управление доступом")
        lbl_title.setStyleSheet(
            "font-size:15px; font-weight:bold; color:#1a237e; margin-bottom:12px;"
        )

        lbl_admin = QtWidgets.QLabel("Admin (кто выдаёт):")
        lbl_admin.setStyleSheet("font-size:12px; font-weight:bold; color:#37474F;")
        self.inp_ac_sender = self.make_input("Адрес Admin (0x...)")

        lbl_user = QtWidgets.QLabel("Пользователь:")
        lbl_user.setStyleSheet("font-size:12px; font-weight:bold; color:#37474F;")
        self.inp_ac_user = self.make_input("Адрес / Имя / Телефон")

        # Кнопки
        btn_grant  = self.make_btn("✅  Выдать доступ",    "#2E7D32")
        btn_revoke = self.make_btn("🚫  Отозвать доступ",  "#C62828")
        btn_check  = self.make_btn("🔍  Проверить доступ", "#E65100")

        btn_grant.setFixedHeight(42)
        btn_revoke.setFixedHeight(42)
        btn_check.setFixedHeight(42)

        btn_grant.clicked.connect(self.grant_access)
        btn_revoke.clicked.connect(self.revoke_access)
        btn_check.clicked.connect(self.check_access)

        self.lbl_ac_result = QtWidgets.QLabel("")
        self.lbl_ac_result.setAlignment(QtCore.Qt.AlignCenter)
        self.lbl_ac_result.setFixedHeight(44)
        self.lbl_ac_result.setStyleSheet(
            "font-size:13px; font-weight:bold; padding:8px; border-radius:8px;"
        )

        cl.addWidget(lbl_title)
        cl.addWidget(lbl_admin)
        cl.addWidget(self.inp_ac_sender)
        cl.addSpacing(8)
        cl.addWidget(lbl_user)
        cl.addWidget(self.inp_ac_user)
        cl.addSpacing(12)
        cl.addWidget(btn_grant)
        cl.addSpacing(4)
        cl.addWidget(btn_revoke)
        cl.addSpacing(4)
        cl.addWidget(btn_check)
        cl.addSpacing(8)
        cl.addWidget(self.lbl_ac_result)
        cl.addStretch()

        layout.addWidget(card)
        layout.addStretch()
        return w

    # ─────────────────────────────────────────
    # ВКЛАДКА: Вход (эмулятор замка)
    # ─────────────────────────────────────────

    def tab_door(self):
        w = QtWidgets.QWidget()
        w.setStyleSheet("background: transparent;")
        layout = QtWidgets.QVBoxLayout(w)
        layout.setContentsMargins(0, 12, 0, 0)
        layout.setAlignment(QtCore.Qt.AlignCenter)

        card = self.make_card()
        card.setMaximumWidth(460)
        cl = QtWidgets.QVBoxLayout(card)
        cl.setAlignment(QtCore.Qt.AlignCenter)

        lbl_title = QtWidgets.QLabel("🚪  Эмулятор замка коворкинга")
        lbl_title.setStyleSheet(
            "font-size:15px; font-weight:bold; color:#1a237e; margin-bottom:4px;"
        )
        lbl_title.setAlignment(QtCore.Qt.AlignCenter)

        lbl_hint = QtWidgets.QLabel(
            "Введите адрес, имя или телефон и нажмите кнопку входа"
        )
        lbl_hint.setStyleSheet("color:#78909C; font-size:11px;")
        lbl_hint.setAlignment(QtCore.Qt.AlignCenter)
        lbl_hint.setWordWrap(True)

        self.inp_door = self.make_input("Адрес / Имя / Телефон")

        # Большая кнопка входа
        btn_enter = QtWidgets.QPushButton("🚶  Войти в коворкинг")
        btn_enter.setFixedHeight(56)
        btn_enter.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1a237e, stop:1 #3949AB);
                color: white; font-weight: bold; font-size: 15px;
                border-radius: 10px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #283593, stop:1 #3F51B5);
            }
        """)
        btn_enter.clicked.connect(self.try_entry)

        # Замок — большой индикатор
        self.lbl_lock = QtWidgets.QLabel("🔒")
        self.lbl_lock.setAlignment(QtCore.Qt.AlignCenter)
        self.lbl_lock.setStyleSheet("font-size: 80px; padding: 16px;")

        self.lbl_lock_msg = QtWidgets.QLabel("Ожидание...")
        self.lbl_lock_msg.setAlignment(QtCore.Qt.AlignCenter)
        self.lbl_lock_msg.setStyleSheet(
            "font-size:15px; font-weight:bold; color:#78909C;"
        )

        cl.addWidget(lbl_title)
        cl.addWidget(lbl_hint)
        cl.addSpacing(12)
        cl.addWidget(self.inp_door)
        cl.addSpacing(8)
        cl.addWidget(btn_enter)
        cl.addWidget(self.lbl_lock)
        cl.addWidget(self.lbl_lock_msg)

        layout.addStretch()
        layout.addWidget(card, alignment=QtCore.Qt.AlignCenter)
        layout.addStretch()
        return w

    # ─────────────────────────────────────────
    # ВКЛАДКА: Статистика (комиссия)
    # ─────────────────────────────────────────

    def tab_stats(self):
        w = QtWidgets.QWidget()
        w.setStyleSheet("background: transparent;")
        layout = QtWidgets.QVBoxLayout(w)
        layout.setContentsMargins(0, 12, 0, 0)

        lbl_title = QtWidgets.QLabel("📊  Статистика комиссий")
        lbl_title.setStyleSheet(
            "font-size:15px; font-weight:bold; color:#1a237e; margin-bottom:12px;"
        )

        # Карточки комиссии
        cards_layout = QtWidgets.QHBoxLayout()

        self.card_percent = self.make_stat_card(
            "Процент комиссии", "—", "#1a237e", "💹"
        )
        self.card_fee = self.make_stat_card(
            "Базовая стоимость", "—", "#1565C0", "💵"
        )
        self.card_amount = self.make_stat_card(
            "Сумма комиссии", "—", "#2E7D32", "💸"
        )
        self.card_total = self.make_stat_card(
            "Всего собрано", "—", "#E65100", "🏦"
        )

        for card in [self.card_percent, self.card_fee,
                     self.card_amount, self.card_total]:
            cards_layout.addWidget(card)

        btn_refresh = self.make_btn("🔄  Обновить статистику", "#546E7A")
        btn_refresh.setMaximumWidth(220)
        btn_refresh.clicked.connect(self.load_commission)

        layout.addWidget(lbl_title)
        layout.addLayout(cards_layout)
        layout.addSpacing(12)
        layout.addWidget(btn_refresh)
        layout.addStretch()

        self.load_commission()
        return w

    def make_stat_card(self, title, value, color, icon):
        frame = QtWidgets.QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background: {color};
                border-radius: 12px;
                padding: 16px;
                margin: 4px;
            }}
        """)
        fl = QtWidgets.QVBoxLayout(frame)
        fl.setAlignment(QtCore.Qt.AlignCenter)

        lbl_icon = QtWidgets.QLabel(icon)
        lbl_icon.setStyleSheet("font-size: 28px;")
        lbl_icon.setAlignment(QtCore.Qt.AlignCenter)

        lbl_title = QtWidgets.QLabel(title)
        lbl_title.setStyleSheet(
            "color: rgba(255,255,255,0.8); font-size:11px; font-weight:bold;"
        )
        lbl_title.setAlignment(QtCore.Qt.AlignCenter)

        lbl_value = QtWidgets.QLabel(value)
        lbl_value.setObjectName("value")
        lbl_value.setStyleSheet(
            "color: white; font-size:22px; font-weight:bold;"
        )
        lbl_value.setAlignment(QtCore.Qt.AlignCenter)

        fl.addWidget(lbl_icon)
        fl.addWidget(lbl_value)
        fl.addWidget(lbl_title)
        return frame

    # ─────────────────────────────────────────
    # ВКЛАДКА: Журнал
    # ─────────────────────────────────────────

    def tab_log(self):
        w = QtWidgets.QWidget()
        w.setStyleSheet("background: transparent;")
        layout = QtWidgets.QVBoxLayout(w)
        layout.setContentsMargins(0, 12, 0, 0)

        top = QtWidgets.QHBoxLayout()
        lbl_title = QtWidgets.QLabel("📋  Журнал посещений (ончейн)")
        lbl_title.setStyleSheet(
            "font-size:15px; font-weight:bold; color:#1a237e;"
        )
        btn_refresh = self.make_btn("🔄  Обновить", "#546E7A")
        btn_refresh.setMaximumWidth(140)
        btn_refresh.clicked.connect(self.load_log)
        top.addWidget(lbl_title)
        top.addStretch()
        top.addWidget(btn_refresh)

        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels([
            "№", "Адрес пользователя", "Время", "Результат"
        ])
        self.table.horizontalHeader().setSectionResizeMode(
            1, QtWidgets.QHeaderView.Stretch
        )
        self.table.setColumnWidth(0, 60)
        self.table.setColumnWidth(2, 170)
        self.table.setColumnWidth(3, 140)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table.setStyleSheet("""
            QTableWidget {
                border: none; border-radius: 8px;
                background: white; font-size: 12px;
                gridline-color: #F5F5F5;
            }
            QHeaderView::section {
                background: #1a237e; color: white;
                font-weight: bold; padding: 10px;
                border: none; font-size: 12px;
            }
            QTableWidget::item {
                padding: 8px; border-bottom: 1px solid #F5F5F5;
            }
            QTableWidget::item:selected {
                background: #E8EAF6; color: #1a237e;
            }
            QTableWidget::item:alternate { background: #FAFAFA; }
        """)

        layout.addLayout(top)
        layout.addSpacing(8)
        layout.addWidget(self.table)
        return w

    # ─────────────────────────────────────────
    # ВСПОМОГАТЕЛЬНЫЕ UI
    # ─────────────────────────────────────────

    def make_card(self):
        frame = QtWidgets.QFrame()
        frame.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 12px;
                padding: 16px;
            }
        """)
        return frame

    def make_input(self, placeholder):
        inp = QtWidgets.QLineEdit()
        inp.setPlaceholderText(placeholder)
        inp.setFixedHeight(40)
        inp.setStyleSheet("""
            QLineEdit {
                border: 1.5px solid #CFD8DC;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 12px;
                background: #FAFAFA;
            }
            QLineEdit:focus {
                border-color: #1a237e;
                background: white;
            }
        """)
        return inp

    def make_btn(self, text, color):
        btn = QtWidgets.QPushButton(text)
        btn.setFixedHeight(38)
        btn.setStyleSheet(f"""
            QPushButton {{
                background: {color};
                color: white; font-weight: bold;
                border-radius: 8px; font-size: 12px;
            }}
            QPushButton:hover {{
                background: {color}CC;
            }}
        """)
        return btn

    def make_role_btn(self, text, color, role_id, update=False):
        btn = QtWidgets.QPushButton(text)
        btn.setFixedHeight(38)
        btn.setStyleSheet(f"""
            QPushButton {{
                background: #F5F5F5; color: #546E7A;
                border: 1.5px solid #CFD8DC;
                border-radius: 8px; font-size: 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{ background: #ECEFF1; }}
        """)
        if update:
            btn.clicked.connect(lambda: self.select_update_role(role_id, color))
        else:
            btn.clicked.connect(lambda: self.select_role(role_id, color))
        return btn

    def role_btn_selected_style(self, color):
        return f"""
            QPushButton {{
                background: {color};
                color: white;
                border: 1.5px solid {color};
                border-radius: 8px; font-size: 12px;
                font-weight: bold;
            }}
        """

    def role_btn_default_style(self):
        return """
            QPushButton {
                background: #F5F5F5; color: #546E7A;
                border: 1.5px solid #CFD8DC;
                border-radius: 8px; font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover { background: #ECEFF1; }
        """

    def select_role(self, role_id, color):
        self.selected_role = role_id
        self.btn_role_user.setStyleSheet(self.role_btn_default_style())
        self.btn_role_admin.setStyleSheet(self.role_btn_default_style())
        if role_id == 0:
            self.btn_role_user.setStyleSheet(self.role_btn_selected_style(color))
        else:
            self.btn_role_admin.setStyleSheet(self.role_btn_selected_style(color))

    def select_update_role(self, role_id, color):
        self.selected_u_role = role_id
        self.btn_u_role_user.setStyleSheet(self.role_btn_default_style())
        self.btn_u_role_admin.setStyleSheet(self.role_btn_default_style())
        if role_id == 0:
            self.btn_u_role_user.setStyleSheet(self.role_btn_selected_style(color))
        else:
            self.btn_u_role_admin.setStyleSheet(self.role_btn_selected_style(color))

    def make_info_row(self, icon, label, value):
        frame = QtWidgets.QFrame()
        frame.setStyleSheet("""
            QFrame {
                background: #F8F9FA;
                border-radius: 6px;
                padding: 2px;
                margin: 2px 0;
            }
        """)
        layout = QtWidgets.QHBoxLayout(frame)
        layout.setContentsMargins(8, 6, 8, 6)

        lbl_icon = QtWidgets.QLabel(icon)
        lbl_icon.setFixedWidth(24)
        lbl_icon.setStyleSheet("font-size:14px;")

        lbl_label = QtWidgets.QLabel(f"{label}:")
        lbl_label.setFixedWidth(70)
        lbl_label.setStyleSheet("font-size:11px; color:#78909C; font-weight:bold;")

        lbl_value = QtWidgets.QLabel(value)
        lbl_value.setObjectName("val")
        lbl_value.setStyleSheet("font-size:12px; color:#263238; font-weight:bold;")

        layout.addWidget(lbl_icon)
        layout.addWidget(lbl_label)
        layout.addWidget(lbl_value)
        layout.addStretch()
        return frame

    def update_info_row(self, frame, value, color="#263238"):
        lbl = frame.findChild(QtWidgets.QLabel, "val")
        if lbl:
            lbl.setText(value)
            lbl.setStyleSheet(f"font-size:12px; color:{color}; font-weight:bold;")

    # ─────────────────────────────────────────
    # ВАЛИДАЦИЯ
    # ─────────────────────────────────────────

    def validate_address(self, adr, field):
        if not adr:
            self.warn(f"Поле '{field}' не может быть пустым!")
            return False
        if not is_valid_address(adr):
            self.warn(
                f"Неверный адрес в поле '{field}'!\n"
                f"Должен начинаться с 0x и содержать 42 символа."
            )
            return False
        return True

    def validate_identity(self, value, field):
        if not value or len(value.strip()) < 2:
            self.warn(f"Поле '{field}' не может быть пустым!")
            return False
        return True

    def validate_phone(self, phone):
        if not phone:
            self.warn("Поле 'Телефон' не может быть пустым!")
            return False
        if not (phone.startswith("+") or phone.isdigit()):
            self.warn("Неверный формат телефона!\nПример: +77001234567")
            return False
        return True

    # ─────────────────────────────────────────
    # ОБРАБОТЧИКИ
    # ─────────────────────────────────────────

    def search_user(self):
        value = self.inp_search.text().strip()
        if not self.validate_identity(value, "Поиск"):
            return
        try:
            d, address = self.api.get_user_by_identity(value)
            # d = (name, phone, role, hasAccess, isRegistered, balance)
            role_name  = ROLES.get(d[2], str(d[2]))
            role_color = ROLE_COLORS.get(d[2], "#263238")

            # Аватар с первой буквой имени
            initial = d[0][0].upper() if d[0] else "?"
            self.lbl_avatar.setText(initial)
            bg = ROLE_BG.get(d[2], "#E8EAF6")
            self.lbl_avatar.setStyleSheet(f"""
                background: {bg}; border-radius: 40px;
                font-size: 28px; font-weight: bold; color: {role_color};
            """)

            self.update_info_row(self.lbl_s_name, d[0])
            self.update_info_row(self.lbl_s_phone, d[1])
            self.update_info_row(self.lbl_s_role, role_name, role_color)
            self.update_info_row(
                self.lbl_s_access,
                "✅ Есть" if d[3] else "❌ Нет",
                "#2E7D32" if d[3] else "#C62828"
            )
            self.update_info_row(self.lbl_s_balance, f"{d[5]} wei")
            self.update_info_row(
                self.lbl_s_status,
                "Зарегистрирован" if d[4] else "Не зарегистрирован",
                "#2E7D32" if d[4] else "#C62828"
            )
        except Exception as e:
            self.err(e)

    def register_user(self):
        sender = self.inp_c_sender.text().strip()
        adr    = self.inp_c_adr.text().strip()
        name   = self.inp_c_name.text().strip()
        phone  = self.inp_c_phone.text().strip()

        if not self.validate_address(sender, "Адрес Admin"): return
        if not self.validate_address(adr, "Адрес пользователя"): return
        if not name or len(name) < 2:
            self.warn("Имя должно быть минимум 2 символа!"); return
        if not self.validate_phone(phone): return
        if sender == adr:
            self.warn("Адрес Admin и нового пользователя не могут совпадать!"); return

        try:
            self.api.register_user(sender, adr, name, phone, self.selected_role)
            self.ok(f"✅ Пользователь '{name}' зарегистрирован!")
            self.refresh_header()
            # Очищаем поля
            for inp in [self.inp_c_adr, self.inp_c_name, self.inp_c_phone]:
                inp.clear()
        except Exception as e:
            self.err(e)

    def load_user_for_edit(self):
        value = self.inp_u_find.text().strip()
        if not self.validate_identity(value, "Поиск"): return
        try:
            d, address = self.api.get_user_by_identity(value)
            # Заполняем форму текущими данными
            self.inp_u_name.setText(d[0])
            self.inp_u_phone.setText(d[1])
            # Устанавливаем роль
            self.select_update_role(d[2], ROLE_COLORS.get(d[2], "#4CAF50"))
            self.lbl_u_result.setText(f"Загружены данные: {d[0]}")
            self.lbl_u_result.setStyleSheet(
                "font-size:12px; font-weight:bold; padding:8px; "
                "border-radius:6px; background:#E8F5E9; color:#2E7D32;"
            )
        except Exception as e:
            self.err(e)

    def update_user(self):
        sender   = self.inp_u_sender.text().strip()
        identity = self.inp_u_find.text().strip()
        new_name  = self.inp_u_name.text().strip()
        new_phone = self.inp_u_phone.text().strip()

        if not self.validate_address(sender, "Адрес SuperAdmin"): return
        if not self.validate_identity(identity, "Пользователь"): return
        if not new_name or len(new_name) < 2:
            self.warn("Имя должно быть минимум 2 символа!"); return
        if not self.validate_phone(new_phone): return

        try:
            self.api.update_user(sender, identity, new_name, new_phone, self.selected_u_role)
            role_name = ROLES.get(self.selected_u_role, "User")
            self.lbl_u_result.setText(f"✅ Данные обновлены! Роль: {role_name}")
            self.lbl_u_result.setStyleSheet(
                "font-size:12px; font-weight:bold; padding:8px; "
                "border-radius:6px; background:#F3E5F5; color:#7B1FA2;"
            )
        except Exception as e:
            self.err(e)

    def grant_access(self):
        sender   = self.inp_ac_sender.text().strip()
        identity = self.inp_ac_user.text().strip()
        if not self.validate_address(sender, "Адрес Admin"): return
        if not self.validate_identity(identity, "Пользователь"): return
        try:
            self.api.grant_access(sender, identity)
            self.lbl_ac_result.setText("✅  Доступ выдан! (списана комиссия 2%)")
            self.lbl_ac_result.setStyleSheet(
                "font-size:13px; font-weight:bold; padding:8px; "
                "border-radius:8px; background:#E8F5E9; color:#2E7D32;"
            )
            self.load_commission()
        except Exception as e:
            self.err(e)

    def revoke_access(self):
        sender   = self.inp_ac_sender.text().strip()
        identity = self.inp_ac_user.text().strip()
        if not self.validate_address(sender, "Адрес Admin"): return
        if not self.validate_identity(identity, "Пользователь"): return
        try:
            self.api.revoke_access(sender, identity)
            self.lbl_ac_result.setText("🚫  Доступ отозван!")
            self.lbl_ac_result.setStyleSheet(
                "font-size:13px; font-weight:bold; padding:8px; "
                "border-radius:8px; background:#FFEBEE; color:#C62828;"
            )
        except Exception as e:
            self.err(e)

    def check_access(self):
        identity = self.inp_ac_user.text().strip()
        if not self.validate_identity(identity, "Пользователь"): return
        try:
            address = self.api.resolve_identity(identity)
            has = self.api.check_access(address)
            if has:
                self.lbl_ac_result.setText("🔍  Доступ: ЕСТЬ ✅")
                self.lbl_ac_result.setStyleSheet(
                    "font-size:13px; font-weight:bold; padding:8px; "
                    "border-radius:8px; background:#E8F5E9; color:#2E7D32;"
                )
            else:
                self.lbl_ac_result.setText("🔍  Доступ: НЕТ ❌")
                self.lbl_ac_result.setStyleSheet(
                    "font-size:13px; font-weight:bold; padding:8px; "
                    "border-radius:8px; background:#FFEBEE; color:#C62828;"
                )
        except Exception as e:
            self.err(e)

    def try_entry(self):
        identity = self.inp_door.text().strip()
        if not self.validate_identity(identity, "Пользователь"): return
        try:
            granted = self.api.try_entry(identity)
            if granted:
                self.lbl_lock.setText("🔓")
                self.lbl_lock_msg.setText("Добро пожаловать!")
                self.lbl_lock_msg.setStyleSheet(
                    "font-size:16px; font-weight:bold; color:#2E7D32;"
                )
                QtCore.QTimer.singleShot(3000, self.close_lock)
            else:
                self.lbl_lock.setText("🔒")
                self.lbl_lock_msg.setText("Доступ запрещён!")
                self.lbl_lock_msg.setStyleSheet(
                    "font-size:16px; font-weight:bold; color:#C62828;"
                )
            self.load_log()
            self.refresh_header()
        except Exception as e:
            self.err(e)

    def close_lock(self):
        self.lbl_lock.setText("🔒")
        self.lbl_lock_msg.setText("Замок закрыт")
        self.lbl_lock_msg.setStyleSheet(
            "font-size:15px; font-weight:bold; color:#78909C;"
        )

    def load_commission(self):
        try:
            d = self.api.get_commission_info()
            self.card_percent.findChild(QtWidgets.QLabel, "value").setText(f"{d[0]}%")
            self.card_fee.findChild(QtWidgets.QLabel, "value").setText(f"{d[1]} wei")
            self.card_amount.findChild(QtWidgets.QLabel, "value").setText(f"{d[2]} wei")
            self.card_total.findChild(QtWidgets.QLabel, "value").setText(f"{d[3]} wei")
        except Exception as e:
            self.err(e)

    def load_log(self):
        try:
            log = self.api.get_full_log()
            self.table.setRowCount(0)
            self.table.setRowHeight(0, 44)

            for entry in reversed(log):
                row = self.table.rowCount()
                self.table.insertRow(row)
                self.table.setRowHeight(row, 44)

                self.table.setItem(row, 0,
                    QtWidgets.QTableWidgetItem(str(entry["id"])))
                self.table.setItem(row, 1,
                    QtWidgets.QTableWidgetItem(entry["user"]))

                dt = datetime.fromtimestamp(entry["timestamp"])
                self.table.setItem(row, 2,
                    QtWidgets.QTableWidgetItem(dt.strftime("%Y-%m-%d  %H:%M:%S")))

                result = "✅  Разрешён" if entry["granted"] else "❌  Запрещён"
                item = QtWidgets.QTableWidgetItem(result)
                item.setForeground(
                    QtGui.QColor("#2E7D32") if entry["granted"]
                    else QtGui.QColor("#C62828")
                )
                self.table.setItem(row, 3, item)
        except Exception as e:
            self.err(e)

    # ─────────────────────────────────────────
    # ДИАЛОГИ
    # ─────────────────────────────────────────

    def ok(self, msg):
        QtWidgets.QMessageBox.information(self, "✅ Успех", msg)

    def warn(self, msg):
        QtWidgets.QMessageBox.warning(self, "⚠️ Внимание", msg)

    def err(self, e):
        QtWidgets.QMessageBox.critical(self, "❌ Ошибка", str(e))


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())