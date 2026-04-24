import { useState, useEffect } from "react";
import { getAccounts } from "./contract";
import Search from "./pages/Search";
import Register from "./pages/Register";
import Update from "./pages/Update";
import Access from "./pages/Access";
import Door from "./pages/Door";
import Stats from "./pages/Stats";
import Log from "./pages/Log";

const tabs = [
  { id: "search",   label: "🔍 Поиск"         },
  { id: "register", label: "➕ Регистрация"    },
  { id: "update",   label: "✏️ Редактировать"  },
  { id: "access",   label: "🔑 Доступ"         },
  { id: "door",     label: "🚪 Вход"           },
  { id: "stats",    label: "📊 Статистика"     },
  { id: "log",      label: "📋 Журнал"         },
];

export default function App() {
  const [activeTab, setActiveTab] = useState("search");
  const [accounts, setAccounts]   = useState([]);
  const [connected, setConnected] = useState(false);
  const [logCount, setLogCount]   = useState(0);

  useEffect(() => {
    getAccounts()
      .then((accs) => {
        setAccounts(accs);
        setConnected(true);
      })
      .catch(() => setConnected(false));
  }, []);

  const shortAddr = accounts[0]
    ? `${accounts[0].slice(0, 10)}...${accounts[0].slice(-4)}`
    : "—";

  return (
    <div className="min-h-screen bg-gray-100">

      {/* ── Шапка ── */}
      <header className="bg-gradient-to-r from-indigo-900 to-indigo-700 text-white shadow-lg">
        <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between flex-wrap gap-2">

          {/* Логотип */}
          <div className="flex items-center gap-2">
            <span className="text-2xl">🏢</span>
            <span className="font-bold text-lg">Coworking Access Control</span>
          </div>

          {/* Статус */}
          <div className="flex items-center gap-3 flex-wrap text-sm">
            <span className={`flex items-center gap-1 px-3 py-1 rounded-full ${
              connected
                ? "bg-green-500/20 text-green-200"
                : "bg-red-500/20 text-red-200"
            }`}>
              {connected ? "🟢 Подключено" : "🔴 Нет подключения"}
            </span>
            <span className="bg-white/10 px-3 py-1 rounded-full">
              📍 {shortAddr}
            </span>
            <span className="bg-white/10 px-3 py-1 rounded-full">
              📝 Журнал: {logCount}
            </span>
          </div>
        </div>
      </header>

      {/* ── Вкладки ── */}
      <div className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-6xl mx-auto px-4">
          <div className="flex overflow-x-auto gap-1 py-2">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`whitespace-nowrap px-4 py-2 rounded-lg text-sm font-semibold transition-all ${
                  activeTab === tab.id
                    ? "bg-indigo-900 text-white shadow"
                    : "text-gray-500 hover:bg-gray-100"
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* ── Контент ── */}
      <main className="max-w-6xl mx-auto px-4 py-6">
        {activeTab === "search"   && <Search accounts={accounts} />}
        {activeTab === "register" && <Register accounts={accounts} />}
        {activeTab === "update"   && <Update accounts={accounts} />}
        {activeTab === "access"   && <Access accounts={accounts} />}
        {activeTab === "door"     && <Door accounts={accounts} />}
        {activeTab === "stats"    && <Stats />}
        {activeTab === "log"      && <Log onCountChange={setLogCount} />}
      </main>
    </div>
  );
}