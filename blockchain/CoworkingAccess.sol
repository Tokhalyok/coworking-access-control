// SPDX-License-Identifier: MIT
pragma solidity ^0.5.17;
pragma experimental ABIEncoderV2;

contract CoworkingAccess {

    // РОЛИ

    enum Role { User, Admin, SuperAdmin }

    // СТРУКТУРЫ

    struct User {
        string name;        // имя пользователя
        Role role;          // роль
        bool hasAccess;     // есть ли доступ
        bool isRegistered;  // зарегистрирован ли
    }

    struct LogEntry {
        address user;       // кто вошёл
        uint timestamp;     // когда вошёл
        bool accessGranted; // был ли доступ разрешён
    }

    // ХРАНИЛИЩЕ

    mapping(address => User) public users;
    LogEntry[] public accessLog;  // журнал всех попыток входа

    // СОБЫТИЯ (Events) — записываются в блокчейн

    event AccessGranted(address indexed user, uint timestamp);
    event AccessRevoked(address indexed user, uint timestamp);
    event EntryLogged(address indexed user, uint timestamp, bool granted);
    event UserRegistered(address indexed user, string name, uint timestamp);

    // МОДИФИКАТОРЫ

    modifier onlyAdmin() {
        require(users[msg.sender].isRegistered, "error: not registered");
        require(
            users[msg.sender].role == Role.Admin ||
            users[msg.sender].role == Role.SuperAdmin,
            "error: not admin"
        );
        _;
    }

    modifier onlySuperAdmin() {
        require(users[msg.sender].isRegistered, "error: not registered");
        require(users[msg.sender].role == Role.SuperAdmin, "error: not superadmin");
        _;
    }

    modifier onlyRegistered() {
        require(users[msg.sender].isRegistered, "error: not registered");
        _;
    }

    // КОНСТРУКТОР — первый деплоер = SuperAdmin

    constructor() public {
        users[msg.sender] = User({
            name: "SuperAdmin",
            role: Role.SuperAdmin,
            hasAccess: true,
            isRegistered: true
        });
    }

    // Регистрация нового пользователя (только Admin/SuperAdmin)
    function registerUser(address adr, string memory name, Role role) public onlyAdmin {
        require(adr != address(0), "error: wrong address");
        require(!users[adr].isRegistered, "error: already registered");
        require(role != Role.SuperAdmin, "error: cannot assign superadmin");

        users[adr] = User({
            name: name,
            role: role,
            hasAccess: false,
            isRegistered: true
        });

        emit UserRegistered(adr, name, block.timestamp);
    }

    // Выдать доступ пользователю (только Admin/SuperAdmin)
    function grantAccess(address adr) public onlyAdmin {
        require(users[adr].isRegistered, "error: user not registered");
        require(!users[adr].hasAccess, "error: already has access");

        users[adr].hasAccess = true;

        emit AccessGranted(adr, block.timestamp);
    }

    // Отозвать доступ пользователя (только Admin/SuperAdmin)
    function revokeAccess(address adr) public onlyAdmin {
        require(users[adr].isRegistered, "error: user not registered");
        require(users[adr].hasAccess, "error: no access to revoke");

        users[adr].hasAccess = false;

        emit AccessRevoked(adr, block.timestamp);
    }

    // Попытка входа — записывает в журнал
    // Вызывает сам пользователь когда подходит к двери
    function tryEntry() public onlyRegistered {
        bool granted = users[msg.sender].hasAccess;

        accessLog.push(LogEntry({
            user: msg.sender,
            timestamp: block.timestamp,
            accessGranted: granted
        }));

        emit EntryLogged(msg.sender, block.timestamp, granted);
    }

    // ЧТЕНИЕ → .call() бесплатно

    // Проверить есть ли доступ у пользователя
    function checkAccess(address adr) public view returns (bool) {
        return users[adr].hasAccess;
    }

    // Получить запись журнала по ID
    function getLogEntry(uint id) public view returns (
        address user,
        uint timestamp,
        bool accessGranted
    ) {
        require(id < accessLog.length, "error: no such log entry");
        LogEntry memory entry = accessLog[id];
        return (entry.user, entry.timestamp, entry.accessGranted);
    }

    // Получить общее количество записей в журнале
    function getLogCount() public view returns (uint) {
        return accessLog.length;
    }

    // Получить информацию о пользователе
    function getUser(address adr) public view returns (
        string memory name,
        uint role,
        bool hasAccess,
        bool isRegistered
    ) {
        User memory u = users[adr];
        return (u.name, uint(u.role), u.hasAccess, u.isRegistered);
    }
}
