import { useState, useEffect } from "react";
import { getContract } from "../contract";

const cards = [
  { key: 0, label: "Процент комиссии", icon: "💹", color: "from-indigo-900 to-indigo-700", suffix: "%" },
  { key: 1, label: "Базовая стоимость", icon: "💵", color: "from-blue-700 to-blue-500",    suffix: " wei" },
  { key: 2, label: "Сумма комиссии",    icon: "💸", color: "from-green-700 to-green-500",   suffix: " wei" },
  { key: 3, label: "Всего собрано",     icon: "🏦", color: "from-orange-600 to-orange-400", suffix: " wei" },
];

export default function Stats() {
  const [data,    setData]    = useState(null);
  const [loading, setLoading] = useState(false);

  const load = async () => {
    setLoading(true);
    try {
      const contract = getContract();
      const info = await contract.getCommissionInfo();
      setData(info.map((v) => v.toString()));
    } catch {}
    setLoading(false);
  };

  useEffect(() => { load(); }, []);

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-xl font-bold text-indigo-900">📊 Статистика комиссий</h2>
          <p className="text-sm text-gray-400">Информация о комиссиях за выдачу доступа</p>
        </div>
        <button
          onClick={load}
          disabled={loading}
          className="bg-gray-600 text-white px-4 py-2 rounded-xl text-sm font-semibold hover:bg-gray-700 transition disabled:opacity-50"
        >
          {loading ? "..." : "🔄 Обновить"}
        </button>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {cards.map((card) => (
          <div
            key={card.key}
            className={`bg-gradient-to-br ${card.color} rounded-2xl p-6 text-white shadow-lg`}
          >
            <div className="text-3xl mb-3">{card.icon}</div>
            <div className="text-2xl font-bold mb-1">
              {data ? `${data[card.key]}${card.suffix}` : "—"}
            </div>
            <div className="text-xs opacity-80">{card.label}</div>
          </div>
        ))}
      </div>
    </div>
  );
}