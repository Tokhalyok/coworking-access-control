from web3 import Web3
import json

class CoworkingAPI:
    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))

        # СЮДА ВСТАВЬ НОВЫЙ АДРЕС ПОСЛЕ ДЕПЛОЯ
        contract_address = self.w3.to_checksum_address(
            "0xc0575C27b015Dad7ddF77D44c0832Bea7f92a4d5"
        )

        with open("abi.json", "r") as f:
            abi = json.load(f)

        self.contract = self.w3.eth.contract(address=contract_address, abi=abi)

    # ─────────────────────────────────────────
    # ВСПОМОГАТЕЛЬНЫЕ
    # ─────────────────────────────────────────

    def get_accounts(self):
        return self.w3.eth.accounts

    def get_eth_balance(self, address):
        return self.w3.from_wei(self.w3.eth.get_balance(address), "ether")

    def is_connected(self):
        return self.w3.is_connected()

    def resolve_identity(self, value):
        """
        Универсальный метод — принимает адрес, имя или телефон
        и возвращает адрес пользователя.

        Логика определения:
        0x + 42 символа  → это Ethereum адрес
        начинается с +   → это телефон
        только цифры     → это телефон
        всё остальное    → это имя
        """
        value = value.strip()

        # Адрес Ethereum
        if value.startswith("0x") and len(value) == 42:
            return self.w3.to_checksum_address(value)

        # Телефон — начинается с + или только цифры
        if value.startswith("+") or value.isdigit():
            return self.contract.functions.getAddressByPhone(value).call()

        # Имя — всё остальное
        return self.contract.functions.getAddressByName(value).call()

    # ─────────────────────────────────────────
    # ЧТЕНИЕ → .call() бесплатно
    # ─────────────────────────────────────────

    def get_user(self, address):
        # Возвращает (name, phone, role, hasAccess, isRegistered, balance)
        return self.contract.functions.getUser(address).call()

    def get_user_by_identity(self, value):
        # Получить инфо о пользователе по адресу/имени/телефону
        address = self.resolve_identity(value)
        return self.get_user(address), address

    def check_access(self, address):
        return self.contract.functions.checkAccess(address).call()

    def get_log_count(self):
        return self.contract.functions.getLogCount().call()

    def get_log_entry(self, log_id):
        return self.contract.functions.getLogEntry(log_id).call()

    def get_full_log(self):
        count = self.get_log_count()
        log = []
        for i in range(count):
            entry = self.get_log_entry(i)
            log.append({
                "id": i,
                "user": entry[0],
                "timestamp": entry[1],
                "granted": entry[2]
            })
        return log

    def get_commission_info(self):
        # Возвращает (percent, fee, commissionAmt, totalCollected)
        return self.contract.functions.getCommissionInfo().call()

    def get_owner(self):
        return self.contract.functions.owner().call()

    # ─────────────────────────────────────────
    # ЗАПИСЬ → .transact() меняет блокчейн
    # ─────────────────────────────────────────

    def register_user(self, sender, address, name, phone, role):
        tx = self.contract.functions.registerUser(
            address, name, phone, int(role)
        ).transact({"from": sender})
        self.w3.eth.wait_for_transaction_receipt(tx)

    def grant_access(self, sender, identity):
        # Принимает адрес, имя или телефон
        address = self.resolve_identity(identity)
        tx = self.contract.functions.grantAccess(
            address
        ).transact({"from": sender})
        self.w3.eth.wait_for_transaction_receipt(tx)

    def revoke_access(self, sender, identity):
        # Принимает адрес, имя или телефон
        address = self.resolve_identity(identity)
        tx = self.contract.functions.revokeAccess(
            address
        ).transact({"from": sender})
        self.w3.eth.wait_for_transaction_receipt(tx)

    def try_entry(self, identity):
        # Принимает адрес, имя или телефон
        address = self.resolve_identity(identity)
        tx = self.contract.functions.tryEntry().transact({"from": address})
        receipt = self.w3.eth.wait_for_transaction_receipt(tx)
        logs = self.contract.events.EntryLogged().process_receipt(receipt)
        if logs:
            return logs[0]["args"]["granted"]
        return False

    # ─────────────────────────────────────────
    # ЭМУЛЯТОР ЗАМКА
    # ─────────────────────────────────────────

    def emulate_lock(self, granted):
        if granted:
            return "🔓 ЗАМОК ОТКРЫТ — Добро пожаловать!"
        else:
            return "🔒 ЗАМОК ЗАКРЫТ — Доступ запрещён!"