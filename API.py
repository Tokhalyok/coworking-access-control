from web3 import Web3
import json

class CoworkingAPI:
    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))

        contract_address = self.w3.to_checksum_address(
            "0x164f8353bf536D029b6aB84BC068Ab43C5b0bC9f"
        )

        with open("abi.json", "r") as f:
            abi = json.load(f)

        self.contract = self.w3.eth.contract(address=contract_address, abi=abi)

    def get_accounts(self):
        return self.w3.eth.accounts

    def get_eth_balance(self, address):
        return self.w3.from_wei(self.w3.eth.get_balance(address), "ether")

    def is_connected(self):
        return self.w3.is_connected()

    def get_user(self, address):
        # Возвращает (name, role, hasAccess, isRegistered)
        # role: 0=User, 1=Admin, 2=SuperAdmin
        return self.contract.functions.getUser(address).call()

    def check_access(self, address):
        # Возвращает True/False — есть ли доступ
        return self.contract.functions.checkAccess(address).call()

    def get_log_count(self):
        # Количество записей в журнале
        return self.contract.functions.getLogCount().call()

    def get_log_entry(self, log_id):
        # Возвращает (user_address, timestamp, accessGranted)
        return self.contract.functions.getLogEntry(log_id).call()

    def get_full_log(self):
        # Получить весь журнал — список всех записей
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

    def register_user(self, sender, address, name, role):
        # sender  — кто вызывает (должен быть admin)
        # address — адрес нового пользователя
        # name    — имя
        # role    — 0=User, 1=Admin, 2=SuperAdmin
        tx = self.contract.functions.registerUser(
            address, name, int(role)
        ).transact({"from": sender})
        self.w3.eth.wait_for_transaction_receipt(tx)

    def grant_access(self, sender, address):
        # Выдать доступ пользователю
        tx = self.contract.functions.grantAccess(
            address
        ).transact({"from": sender})
        self.w3.eth.wait_for_transaction_receipt(tx)

    def revoke_access(self, sender, address):
        # Отозвать доступ пользователя
        tx = self.contract.functions.revokeAccess(
            address
        ).transact({"from": sender})
        self.w3.eth.wait_for_transaction_receipt(tx)

    def try_entry(self, sender):
        # Попытка входа — вызывает сам пользователь
        # Контракт записывает в журнал да или нет
        tx = self.contract.functions.tryEntry().transact({"from": sender})
        receipt = self.w3.eth.wait_for_transaction_receipt(tx)

        # Читаем событие EntryLogged из receipt
        logs = self.contract.events.EntryLogged().process_receipt(receipt)
        if logs:
            return logs[0]["args"]["granted"]
        return False

    def emulate_lock(self, granted):
        # Имитация физического замка
        # В реальной системе здесь был бы сигнал на IoT устройство
        if granted:
            return "🔓 ЗАМОК ОТКРЫТ — Добро пожаловать!"
        else:
            return "🔒 ЗАМОК ЗАКРЫТ — Доступ запрещён!"