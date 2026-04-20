import sys
from datetime import datetime
from PyQt5 import QtWidgets, QtGui, QtCore
from API import CoworkingAPI

ROLES = {0: "User", 1: "Admin", 2: "SuperAdmin"}
ROLE_COLORS = {0: "#4CAF50", 1: "#2196F3", 2: "#9C27B0"}


def is_valid_address(adr):
    # Адрес Ethereum: начинается с 0x и длина 42 символа
    return adr.startswith("0x") and len(adr) == 42


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.api = CoworkingAPI()
        self.accounts = self.api.get_accounts()
        self.setWindowTitle("🏢 Coworking Access Control")
        self.setFixedSize(1000, 850)
        self.init_ui()

    def init_ui(self):
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        container = QtWidgets.QWidget()
        container.setStyleSheet("background-color: #ECEFF1;")
        scroll.setWidget(container)
        self.setCentralWidget(scroll)

        main = QtWidgets.QVBoxLayout(container)
        main.setSpacing(10)
        main.setContentsMargins(12, 12, 12, 12)

        main.addWidget(self.build_header())

        row1 = QtWidgets.QHBoxLayout()
        row1.addWidget(self.block_user_info())
        row1.addWidget(self.block_register_user())

        row2 = QtWidgets.QHBoxLayout()
        row2.addWidget(self.block_access_control())
        row2.addWidget(self.block_door())

        main.addLayout(row1)
        main.addLayout(row2)
        main.addWidget(self.block_log())


    def build_header(self):
        frame = QtWidgets.QFrame()
        frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1a237e, stop:1 #283593);
                border-radius: 10px;
                padding: 6px;
            }
        """)
        layout = QtWidgets.QHBoxLayout(frame)

        lbl_title = QtWidgets.QLabel("🏢  Coworking Access Control")
        lbl_title.setStyleSheet("color:white; font-size:16px; font-weight:bold;")

        self.lbl_status    = QtWidgets.QLabel()
        self.lbl_address   = QtWidgets.QLabel()
        self.lbl_log_count = QtWidgets.QLabel()

        for lbl in [self.lbl_status, self.lbl_address, self.lbl_log_count]:
            lbl.setStyleSheet("color:#B3E5FC; font-size:11px; font-weight:bold;")

        btn_refresh = QtWidgets.QPushButton("⟳ Обновить")
        btn_refresh.setStyleSheet("""
            QPushButton {
                background: white; color: #1a237e;
                font-weight: bold; border-radius: 6px;
                padding: 5px 12px;
            }
            QPushButton:hover { background: #E3F2FD; }
        """)
        btn_refresh.clicked.connect(self.refresh_header)

        layout.addWidget(lbl_title)
        layout.addStretch()
        layout.addWidget(self.lbl_status)
        layout.addWidget(self.lbl_address)
        layout.addWidget(self.lbl_log_count)
        layout.addWidget(btn_refresh)

        self.refresh_header()
        return frame

    def refresh_header(self):
        try:
            connected = self.api.is_connected()
            self.lbl_status.setText(
                "🟢 Подключено" if connected else "🔴 Нет подключения"
            )
            self.lbl_address.setText("│  " + self.accounts[0][:18] + "...")
            count = self.api.get_log_count()
            self.lbl_log_count.setText(f"│  Записей в журнале: {count}")
        except:
            self.lbl_status.setText("🔴 Ошибка подключения")


    def block_user_info(self):
        gb = self.make_group("👤  Информация о пользователе")
        layout = QtWidgets.QVBoxLayout(gb)

        self.inp_info_adr = self.make_input("Адрес пользователя (0x...)")
        btn = self.make_btn("Получить информацию", "#2196F3")
        btn.clicked.connect(self.get_user_info)

        card = QtWidgets.QFrame()
        card.setStyleSheet("""
            QFrame {
                background: #F5F5F5;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                padding: 4px;
            }
        """)
        card_layout = QtWidgets.QVBoxLayout(card)

        self.lbl_u_name   = QtWidgets.QLabel("Имя: —")
        self.lbl_u_role   = QtWidgets.QLabel("Роль: —")
        self.lbl_u_access = QtWidgets.QLabel("Доступ: —")
        self.lbl_u_exist  = QtWidgets.QLabel("Статус: —")

        for lbl in [self.lbl_u_name, self.lbl_u_role,
                    self.lbl_u_access, self.lbl_u_exist]:
            lbl.setStyleSheet("font-size:12px; padding:2px;")
            card_layout.addWidget(lbl)

        layout.addWidget(self.inp_info_adr)
        layout.addWidget(btn)
        layout.addWidget(card)
        layout.addStretch()
        return gb


    def block_register_user(self):
        gb = self.make_group("📝  Регистрация пользователя")
        layout = QtWidgets.QVBoxLayout(gb)

        self.inp_reg_sender = self.make_input("Адрес Admin/SuperAdmin")
        self.inp_reg_adr    = self.make_input("Адрес нового пользователя")
        self.inp_reg_name   = self.make_input("Имя пользователя")

        role_layout = QtWidgets.QHBoxLayout()
        lbl_role = QtWidgets.QLabel("Роль:")
        lbl_role.setStyleSheet("font-size:12px; font-weight:bold;")
        self.cmb_role = QtWidgets.QComboBox()
        self.cmb_role.addItems(["0 — User", "1 — Admin"])
        self.cmb_role.setStyleSheet("""
            QComboBox {
                border: 1px solid #BDBDBD;
                border-radius: 4px;
                padding: 5px;
                font-size:12px;
            }
        """)
        role_layout.addWidget(lbl_role)
        role_layout.addWidget(self.cmb_role)

        btn = self.make_btn("Зарегистрировать", "#43A047")
        btn.clicked.connect(self.register_user)

        layout.addWidget(self.inp_reg_sender)
        layout.addWidget(self.inp_reg_adr)
        layout.addWidget(self.inp_reg_name)
        layout.addLayout(role_layout)
        layout.addWidget(btn)
        layout.addStretch()
        return gb


    def block_access_control(self):
        gb = self.make_group("🔑  Управление доступом")
        layout = QtWidgets.QVBoxLayout(gb)

        self.inp_ac_sender = self.make_input("Адрес Admin (кто выдаёт/отзывает)")
        self.inp_ac_user   = self.make_input("Адрес пользователя")

        btn_grant  = self.make_btn("✅  Выдать доступ",    "#4CAF50")
        btn_revoke = self.make_btn("❌  Отозвать доступ",  "#f44336")
        btn_check  = self.make_btn("🔍  Проверить доступ", "#FF9800")

        btn_grant.clicked.connect(self.grant_access)
        btn_revoke.clicked.connect(self.revoke_access)
        btn_check.clicked.connect(self.check_access)

        self.lbl_access_result = QtWidgets.QLabel("")
        self.lbl_access_result.setAlignment(QtCore.Qt.AlignCenter)
        self.lbl_access_result.setStyleSheet(
            "font-size:13px; font-weight:bold; padding:8px; border-radius:6px;"
        )

        layout.addWidget(self.inp_ac_sender)
        layout.addWidget(self.inp_ac_user)
        layout.addWidget(btn_grant)
        layout.addWidget(btn_revoke)
        layout.addWidget(btn_check)
        layout.addWidget(self.lbl_access_result)
        layout.addStretch()
        return gb


    def block_door(self):
        gb = self.make_group("🚪  Эмулятор замка")
        layout = QtWidgets.QVBoxLayout(gb)

        lbl_hint = QtWidgets.QLabel(
            "Пользователь подходит к двери и нажимает кнопку.\n"
            "Система проверяет доступ и записывает в блокчейн."
        )
        lbl_hint.setStyleSheet("color:#757575; font-size:11px;")
        lbl_hint.setWordWrap(True)

        self.inp_door_user = self.make_input("Адрес пользователя")

        btn_enter = QtWidgets.QPushButton("🚶  Войти в коворкинг")
        btn_enter.setFixedHeight(50)
        btn_enter.setStyleSheet("""
            QPushButton {
                background: #1a237e; color: white;
                font-weight: bold; font-size: 14px;
                border-radius: 8px; padding: 10px;
            }
            QPushButton:hover { background: #283593; }
        """)
        btn_enter.clicked.connect(self.try_entry)

        self.lbl_lock = QtWidgets.QLabel("🔒")
        self.lbl_lock.setAlignment(QtCore.Qt.AlignCenter)
        self.lbl_lock.setStyleSheet("font-size: 60px; padding: 10px;")

        self.lbl_lock_msg = QtWidgets.QLabel("Ожидание...")
        self.lbl_lock_msg.setAlignment(QtCore.Qt.AlignCenter)
        self.lbl_lock_msg.setStyleSheet(
            "font-size:13px; font-weight:bold; color:#757575;"
        )

        layout.addWidget(lbl_hint)
        layout.addWidget(self.inp_door_user)
        layout.addWidget(btn_enter)
        layout.addWidget(self.lbl_lock)
        layout.addWidget(self.lbl_lock_msg)
        layout.addStretch()
        return gb


    def block_log(self):
        gb = self.make_group("📋  Журнал посещений (ончейн)")
        layout = QtWidgets.QVBoxLayout(gb)

        btn_refresh = self.make_btn("🔄  Обновить журнал", "#607D8B")
        btn_refresh.clicked.connect(self.load_log)

        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels([
            "№", "Адрес пользователя", "Время", "Результат"
        ])
        self.table.horizontalHeader().setSectionResizeMode(
            1, QtWidgets.QHeaderView.Stretch
        )
        self.table.setColumnWidth(0, 50)
        self.table.setColumnWidth(2, 160)
        self.table.setColumnWidth(3, 130)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #E0E0E0;
                border-radius: 6px;
                gridline-color: #F5F5F5;
                font-size: 11px;
            }
            QHeaderView::section {
                background: #1a237e; color: white;
                font-weight: bold; padding: 6px; border: none;
            }
            QTableWidget::item:alternate { background: #F5F5F5; }
        """)
        self.table.setFixedHeight(200)

        layout.addWidget(btn_refresh)
        layout.addWidget(self.table)
        return gb


    def validate_address(self, adr, field_name):
        if not adr:
            self.warn(f"Поле '{field_name}' не может быть пустым!")
            return False
        if not is_valid_address(adr):
            self.warn(
                f"Неверный адрес в поле '{field_name}'!\n"
                f"Адрес должен начинаться с 0x и содержать 42 символа.\n"
                f"Пример: 0x2a780F82bb407c3D233f6180997CeBfb9716f546"
            )
            return False
        return True

    def validate_name(self, name):
        if not name:
            self.warn("Поле 'Имя' не может быть пустым!")
            return False
        if len(name) < 2:
            self.warn("Имя должно содержать минимум 2 символа!")
            return False
        return True


    def get_user_info(self):
        adr = self.inp_info_adr.text().strip()
        if not self.validate_address(adr, "Адрес пользователя"):
            return
        try:
            d = self.api.get_user(adr)
            # d = (name, role, hasAccess, isRegistered)
            role_name  = ROLES.get(d[1], str(d[1]))
            role_color = ROLE_COLORS.get(d[1], "#000")

            self.lbl_u_name.setText(f"Имя: {d[0]}")
            self.lbl_u_role.setText(f"Роль: {role_name}")
            self.lbl_u_role.setStyleSheet(
                f"font-size:12px; padding:2px; color:{role_color}; font-weight:bold;"
            )
            self.lbl_u_access.setText(
                "Доступ: ✅ Есть" if d[2] else "Доступ: ❌ Нет"
            )
            self.lbl_u_exist.setText(
                "Статус: Зарегистрирован" if d[3] else "Статус: Не зарегистрирован"
            )
        except Exception as e:
            self.err(e)

    def register_user(self):
        sender = self.inp_reg_sender.text().strip()
        adr    = self.inp_reg_adr.text().strip()
        name   = self.inp_reg_name.text().strip()

        # Валидация всех полей
        if not self.validate_address(sender, "Адрес Admin"):
            return
        if not self.validate_address(adr, "Адрес нового пользователя"):
            return
        if not self.validate_name(name):
            return
        if sender == adr:
            self.warn("Адрес Admin и адрес нового пользователя не могут совпадать!")
            return

        try:
            self.api.register_user(sender, adr, name, self.cmb_role.currentIndex())
            self.ok(f"Пользователь '{name}' успешно зарегистрирован!")
            self.refresh_header()
        except Exception as e:
            self.err(e)

    def grant_access(self):
        sender = self.inp_ac_sender.text().strip()
        adr    = self.inp_ac_user.text().strip()

        if not self.validate_address(sender, "Адрес Admin"):
            return
        if not self.validate_address(adr, "Адрес пользователя"):
            return

        try:
            self.api.grant_access(sender, adr)
            self.lbl_access_result.setText("✅ Доступ выдан!")
            self.lbl_access_result.setStyleSheet(
                "font-size:13px; font-weight:bold; padding:8px; "
                "border-radius:6px; background:#E8F5E9; color:#2E7D32;"
            )
        except Exception as e:
            self.err(e)

    def revoke_access(self):
        sender = self.inp_ac_sender.text().strip()
        adr    = self.inp_ac_user.text().strip()

        if not self.validate_address(sender, "Адрес Admin"):
            return
        if not self.validate_address(adr, "Адрес пользователя"):
            return

        try:
            self.api.revoke_access(sender, adr)
            self.lbl_access_result.setText("❌ Доступ отозван!")
            self.lbl_access_result.setStyleSheet(
                "font-size:13px; font-weight:bold; padding:8px; "
                "border-radius:6px; background:#FFEBEE; color:#C62828;"
            )
        except Exception as e:
            self.err(e)

    def check_access(self):
        adr = self.inp_ac_user.text().strip()
        if not self.validate_address(adr, "Адрес пользователя"):
            return
        try:
            has_access = self.api.check_access(adr)
            if has_access:
                self.lbl_access_result.setText("🔍 Доступ: ЕСТЬ ✅")
                self.lbl_access_result.setStyleSheet(
                    "font-size:13px; font-weight:bold; padding:8px; "
                    "border-radius:6px; background:#E8F5E9; color:#2E7D32;"
                )
            else:
                self.lbl_access_result.setText("🔍 Доступ: НЕТ ❌")
                self.lbl_access_result.setStyleSheet(
                    "font-size:13px; font-weight:bold; padding:8px; "
                    "border-radius:6px; background:#FFEBEE; color:#C62828;"
                )
        except Exception as e:
            self.err(e)

    def try_entry(self):
        adr = self.inp_door_user.text().strip()
        if not self.validate_address(adr, "Адрес пользователя"):
            return
        try:
            granted = self.api.try_entry(adr)

            if granted:
                self.lbl_lock.setText("🔓")
                self.lbl_lock_msg.setText("Добро пожаловать!")
                self.lbl_lock_msg.setStyleSheet(
                    "font-size:14px; font-weight:bold; color:#2E7D32;"
                )
                QtCore.QTimer.singleShot(3000, self.close_lock)
            else:
                self.lbl_lock.setText("🔒")
                self.lbl_lock_msg.setText("Доступ запрещён!")
                self.lbl_lock_msg.setStyleSheet(
                    "font-size:14px; font-weight:bold; color:#C62828;"
                )

            self.load_log()
            self.refresh_header()
        except Exception as e:
            self.err(e)

    def close_lock(self):
        self.lbl_lock.setText("🔒")
        self.lbl_lock_msg.setText("Замок закрыт")
        self.lbl_lock_msg.setStyleSheet(
            "font-size:13px; font-weight:bold; color:#757575;"
        )

    def load_log(self):
        try:
            log = self.api.get_full_log()
            self.table.setRowCount(0)

            for entry in reversed(log):
                row = self.table.rowCount()
                self.table.insertRow(row)

                self.table.setItem(row, 0,
                    QtWidgets.QTableWidgetItem(str(entry["id"])))
                self.table.setItem(row, 1,
                    QtWidgets.QTableWidgetItem(entry["user"]))

                dt = datetime.fromtimestamp(entry["timestamp"])
                self.table.setItem(row, 2,
                    QtWidgets.QTableWidgetItem(dt.strftime("%Y-%m-%d %H:%M:%S")))

                result = "✅ Разрешён" if entry["granted"] else "❌ Запрещён"
                result_item = QtWidgets.QTableWidgetItem(result)
                result_item.setForeground(
                    QtGui.QColor("#2E7D32") if entry["granted"] else QtGui.QColor("#C62828")
                )
                self.table.setItem(row, 3, result_item)
        except Exception as e:
            self.err(e)


    def ok(self, msg):
        QtWidgets.QMessageBox.information(self, "✅ Успех", msg)

    def warn(self, msg):
        QtWidgets.QMessageBox.warning(self, "⚠️ Внимание", msg)

    def err(self, e):
        QtWidgets.QMessageBox.critical(self, "❌ Ошибка", str(e))

    def make_group(self, title):
        gb = QtWidgets.QGroupBox(title)
        gb.setStyleSheet("""
            QGroupBox {
                font-weight: bold; font-size: 12px;
                border: 1px solid #CFD8DC; border-radius: 8px;
                margin-top: 10px; background: white; padding: 10px;
            }
            QGroupBox::title { subcontrol-origin: margin; left: 12px; color: #1a237e; }
        """)
        return gb

    def make_input(self, placeholder):
        inp = QtWidgets.QLineEdit()
        inp.setPlaceholderText(placeholder)
        inp.setStyleSheet("""
            QLineEdit {
                border: 1px solid #BDBDBD; border-radius: 4px;
                padding: 6px; font-size: 11px; background: white;
            }
            QLineEdit:focus { border: 1px solid #1a237e; }
        """)
        return inp

    def make_btn(self, text, color):
        btn = QtWidgets.QPushButton(text)
        btn.setStyleSheet(f"""
            QPushButton {{
                background: {color}; color: white;
                font-weight: bold; border-radius: 6px;
                padding: 7px; font-size: 12px;
            }}
            QPushButton:hover {{ opacity: 0.85; }}
        """)
        return btn


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())