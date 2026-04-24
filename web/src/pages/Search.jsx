import { useState } from "react";
import { getContract, resolveIdentity, ROLES, ROLE_COLORS } from "../contract";

export default function Search() {
  const [query, setQuery]   = useState("");
  const [user, setUser]     = useState(null);
  const [address, setAddress] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError]   = useState("");

  const search = async () => {
    if (!query.trim()) return;
    setLoading(true);
    setError("");
    setUser(null);
    try {
      const adr  = await resolveIdentity(query);
      const contract = getContract();
      const data = await contract.getUser(adr);
      setAddress(adr);
      setUser({
        name: data[0],
        phone: data[1],
        role: Number(data[2]),
        hasAccess: data[3],
        isRegistered: data[4],
        balance: data[5].toString(),
      });
    } catch (e) {
      setError("Пользователь не найден");
    }
    setLoading(false);
  };

  return (
    <div className="grid md:grid-cols-2 gap-6">

      {/* Форма поиска */}
      <div className="bg-white rounded-2xl shadow p-6">
        <h2 className="text-xl font-bold text-indigo-900 mb-1">🔍 Найти пользователя</h2>
        <p className="text-sm text-gray-400 mb-4">
          Введите адрес кошелька, имя или номер телефона
        </p>

        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && search()}
          placeholder="0x...  или  Алибек  или  +77001234567"
          className="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-indigo-500 mb-3"
        />

        <button
          onClick={search}
          disabled={loading}
          className="w-full bg-indigo-900 text-white font-semibold py-3 rounded-xl hover:bg-indigo-800 transition disabled:opacity-50"
        >
          {loading ? "Поиск..." : "🔍 Найти"}
        </button>

        {error && (
          <p className="mt-3 text-red-500 text-sm text-center">{error}</p>
        )}
      </div>

      {/* Карточка пользователя */}
      <div className="bg-white rounded-2xl shadow p-6">
        <h2 className="text-xl font-bold text-indigo-900 mb-4">
          Информация о пользователе
        </h2>

        {user ? (
          <div>
            {/* Аватар */}
            <div className="flex justify-center mb-4">
              <div className={`w-20 h-20 rounded-full flex items-center justify-center text-3xl font-bold ${
                ROLE_COLORS[user.role]
              }`}>
                {user.name[0]?.toUpperCase() || "?"}
              </div>
            </div>

            {/* Данные */}
            <div className="space-y-2">
              {[
                ["👤", "Имя",      user.name],
                ["📱", "Телефон",  user.phone],
                ["🎭", "Роль",     ROLES[user.role]],
                ["🔑", "Доступ",   user.hasAccess ? "✅ Есть" : "❌ Нет"],
                ["💰", "Баланс",   `${user.balance} wei`],
                ["✅", "Статус",   user.isRegistered ? "Зарегистрирован" : "Нет"],
              ].map(([icon, label, value]) => (
                <div key={label} className="flex items-center gap-3 bg-gray-50 rounded-xl px-4 py-2">
                  <span className="text-lg">{icon}</span>
                  <span className="text-xs text-gray-400 w-16">{label}:</span>
                  <span className="text-sm font-semibold text-gray-700">{value}</span>
                </div>
              ))}
            </div>

            <p className="mt-3 text-xs text-gray-300 break-all">{address}</p>
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center h-48 text-gray-300">
            <span className="text-5xl">👤</span>
            <p className="mt-2 text-sm">Введите запрос для поиска</p>
          </div>
        )}
      </div>
    </div>
  );
}