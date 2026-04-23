from web3 import Web3
import json

class CoworkingAPI:
    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))

        contract_address = self.w3.to_checksum_address(
            "0x34644BAef876a746F13e270131Da1339B6e86169"
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

    # ─────────────────────────────────────────
    # ЧТЕНИЕ → .call() бесплатно
    # ─────────────────────────────────────────

    def get_user(self, address):
        # Возвращает (name, role, hasAccess, isRegistered, balance)
        return self.contract.functions.getUser(address).call()

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
        # percent      = 2 (процент)
        # fee          = 100 (базовая стоимость)
        # commissionAmt = 2 (сумма комиссии = fee * percent / 100)
        # totalCollected = всего собрано комиссий
        return self.contract.functions.getCommissionInfo().call()

    def get_owner(self):
        return self.contract.functions.owner().call()

    # ─────────────────────────────────────────
    # ЗАПИСЬ → .transact() меняет блокчейн
    # ─────────────────────────────────────────

    def register_user(self, sender, address, name, role):
        tx = self.contract.functions.registerUser(
            address, name, int(role)
        ).transact({"from": sender})
        self.w3.eth.wait_for_transaction_receipt(tx)

    def grant_access(self, sender, address):
        # Списывает 2% комиссию с sender (Admin)
        tx = self.contract.functions.grantAccess(
            address
        ).transact({"from": sender})
        self.w3.eth.wait_for_transaction_receipt(tx)

    def revoke_access(self, sender, address):
        tx = self.contract.functions.revokeAccess(
            address
        ).transact({"from": sender})
        self.w3.eth.wait_for_transaction_receipt(tx)

    def try_entry(self, sender):
        tx = self.contract.functions.tryEntry().transact({"from": sender})
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