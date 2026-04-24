import { useState, useEffect } from "react";
import { getContract } from "../contract";

export default function Log({ onCountChange }) {
  const [log,     setLog]     = useState([]);
  const [loading, setLoading] = useState(false);

  const load = async () => {
    setLoading(true);
    try {
      const contract = getContract();
      const count    = Number(await contract.getLogCount());
      onCountChange?.(count);
      const entries  = [];
      for (let i = count - 1; i >= 0; i--) {
        const e = await contract.getLogEntry(i);
        entries.push({
          id:        i,
          user:      e[0],
          timestamp: Number(e[1]),
          granted:   e[2],
        });
      }
      setLog(entries);
    } catch {}
    setLoading(false);
  };

  useEffect(() => { load(); }, []);

  const fmt = (ts) =>
    new Date(ts * 1000).toLocaleString("ru-RU", {
      year: "numeric", month: "2-digit", day: "2-digit",
      hour: "2-digit", minute: "2-digit", second: "2-digit",
    });

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-xl font-bold text-indigo-900">📋 Журнал посещений</h2>
          <p className="text-sm text-gray-400">Все записи хранятся в блокчейне навсегда</p>
        </div>
        <button
          onClick={load}
          disabled={loading}
          className="bg-gray-600 text-white px-4 py-2 rounded-xl text-sm font-semibold hover:bg-gray-700 transition disabled:opacity-50"
        >
          {loading ? "..." : "🔄 Обновить"}
        </button>
      </div>

      <div className="bg-white rounded-2xl shadow overflow-hidden">
        {/* Заголовок таблицы */}
        <div className="grid grid-cols-12 bg-indigo-900 text-white text-xs font-bold px-4 py-3">
          <div className="col-span-1">№</div>
          <div className="col-span-6">Адрес пользователя</div>
          <div className="col-span-3">Время</div>
          <div className="col-span-2 text-center">Результат</div>
        </div>

        {/* Строки */}
        {log.length === 0 ? (
          <div className="text-center py-12 text-gray-300">
            <div className="text-4xl mb-2">📋</div>
            <p className="text-sm">Журнал пуст</p>
          </div>
        ) : (
          log.map((entry, i) => (
            <div
              key={entry.id}
              className={`grid grid-cols-12 px-4 py-3 text-sm border-b border-gray-50 hover:bg-gray-50 transition ${
                i % 2 === 0 ? "bg-white" : "bg-gray-50/50"
              }`}
            >
              <div className="col-span-1 text-gray-400 font-mono">{entry.id}</div>
              <div className="col-span-6 text-gray-600 font-mono text-xs truncate">
                {entry.user}
              </div>
              <div className="col-span-3 text-gray-500 text-xs">
                {fmt(entry.timestamp)}
              </div>
              <div className="col-span-2 text-center">
                <span className={`px-2 py-1 rounded-full text-xs font-semibold ${
                  entry.granted
                    ? "bg-green-100 text-green-700"
                    : "bg-red-100 text-red-600"
                }`}>
                  {entry.granted ? "✅ Разрешён" : "❌ Запрещён"}
                </span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}