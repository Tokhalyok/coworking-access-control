# 📊 Диаграмма архитектуры IoT

## Mermaid диаграмма

```mermaid
graph TB
    IoT["🏗️ IoT<br/>(Главная папка)"]
    
    IoT --> Root1["📄 abi.json<br/>(ABI контракта)"]
    IoT --> Root2["🐍 API.py<br/>(API на Python)"]
    IoT --> Root3["🔧 build.bat<br/>(Скрипт сборки)"]
    IoT --> Root4["📋 CoworkingAccess.sol<br/>(Smart контракт)"]
    IoT --> Root5["📖 README.md<br/>(Документация)"]
    IoT --> Root6["▶️ Run.py<br/>(Запуск приложения)"]
    
    IoT --> Blockchain["🔗 blockchain/<br/>(Блокчейн)"]
    IoT --> Desktop["💻 desktop/<br/>(Десктоп приложение)"]
    IoT --> Web["🌐 web/<br/>(Веб приложение)"]
    
    Blockchain --> BC1["📄 abi.json"]
    Blockchain --> BC2["📋 CoworkingAccess.sol"]
    
    Desktop --> D1["🐍 API.py"]
    Desktop --> D2["🔧 build.bat"]
    Desktop --> D3["▶️ Run.py"]
    
    Web --> WebReact["⚛️ coworking-react/"]
    WebReact --> WR1["📦 package.json"]
    WebReact --> WR2["⚙️ Конфиги<br/>vite.config.js<br/>tailwind.config.js<br/>postcss.config.js"]
    WebReact --> WR3["🗂️ public/"]
    WebReact --> WR4["📁 src/<br/>(Исходный код React)"]
    
    style IoT fill:#3498db,stroke:#2980b9,color:#fff
    style Blockchain fill:#e74c3c,stroke:#c0392b,color:#fff
    style Desktop fill:#f39c12,stroke:#d68910,color:#fff
    style Web fill:#2ecc71,stroke:#27ae60,color:#fff
```

## Описание компонентов на диаграмме

### 🔵 IoT (Главная папка)
Центральный узел, содержащий весь проект управления доступом в коворкинг через блокчейн.

### 🔴 blockchain/ (Красный блок)
- **Назначение:** Хранение и управление смарт-контрактом
- **Содержимое:**
  - `abi.json` — интерфейс контракта
  - `CoworkingAccess.sol` — сам контракт

### 🟠 desktop/ (Оранжевый блок)
- **Назначение:** Десктоп приложение на Python
- **Содержимое:**
  - `API.py` — основной API
  - `build.bat` — сборка
  - `Run.py` — запуск

### 🟢 web/ (Зелёный блок)
- **Назначение:** Веб приложение
- **Содержимое:**
  - React приложение с конфигурацией Vite
  - Tailwind CSS для стилизации
  - PostCSS для обработки стилей

---

## Уровни архитектуры

```mermaid
graph LR
    A["User Interface<br/>React + Desktop"] --> B["API Layer<br/>Python API"]
    B --> C["Smart Contract<br/>Solidity"]
    C --> D["Blockchain<br/>Network"]
    
    style A fill:#2ecc71,stroke:#27ae60,color:#fff
    style B fill:#f39c12,stroke:#d68910,color:#fff
    style C fill:#e74c3c,stroke:#c0392b,color:#fff
    style D fill:#3498db,stroke:#2980b9,color:#fff
```

---

*Диаграмма создана: 24.04.2026*
