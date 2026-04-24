import { useState } from "react";
import { getContract, getSignedContract, getAccounts, resolveIdentity } from "../contract";

export default function Update({ accounts }) {
  const [query,   setQuery]   = useState("");
  const [address, setAddress] = useState("");
  const [form,    setForm]    = useState({ sender: accounts[0] || "", name: "", phone: "", role: 0 });
  const [loading, setLoading] = useState(false);
  const [result,  setResult]  = useState(null);
  const [loaded,  setLoaded]  = useState(false);

  const set = (k, v) => setForm((f) => ({ ...f, [k]: v }));

  const loadUser = async () => {
    if (!query.trim()) return;
    setLoading(true);
    setResult(null);
    try {
      const adr  = await resolveIdentity(query);
      const data = await getContract().getUser(adr);
      setAddress(adr);
      setForm((f) => ({
        ...f,
        name:  data[0],
        phone: data[1],
        role:  Number(data[2]),
      }));
      setLoaded(true);
      setResult({ ok: true, msg: `Загружены данные: ${data[0]}` });
    } catch (e) {
      setResult({ ok: false, msg: "Пользователь не найден" });
    }
    setLoading(false);
  };

  const save = async () => {
    if (!address || !form.name || !form.phone) {
      setResult({ ok: false, msg: "Сначала загрузите пользователя!" });
      return;
    }
    setLoading(true);
    setResult(null);
    try {
      const accs = await getAccounts();
      const idx  = accs.findIndex((a) => a.toLowerCase() === form.sender.toLowerCase());
      const contract = await getSignedContract(idx >= 0 ? idx : 0);
      const tx = await contract.updateUser(address, form.name, form.phone, form.role);
      await tx.wait();
      setResult({ ok: true, msg: `✅ Данные обновлены!` });
    } catch (e) {
      setResult({ ok: false, msg: e.reason || e.message });
    }
    setLoading(false);
  };

  return (
    <div className="grid md:grid-cols-2 gap-6">

      {/* Поиск */}
      <div className="bg-white rounded-2xl shadow p-6">
        <h2 className="text-xl font-bold text-indigo-900 mb-1">✏️ Редактирование</h2>
        <p className="text-sm text-gray-400 mb-4">Шаг 1: найдите пользователя</p>

        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Адрес / Имя / Телефон"
          className="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-indigo-500 mb-3"
        />
        <button
          onClick={loadUser}
          disabled={loading}
          className="w-full bg-gray-600 text-white font-semibold py-3 rounded-xl hover:bg-gray-700 transition disabled:opacity-50"
        >
          {loading ? "Загрузка..." : "📂 Загрузить данные"}
        </button>

        {result && (
          <div className={`mt-3 text-sm text-center p-3 rounded-xl ${
            result.ok ? "bg-green-50 text-green-700" : "bg-red-50 text-red-600"
          }`}>
            {result.msg}
          </div>
        )}
      </div>

      {/* Форма редактирования */}
      <div className="bg-white rounded-2xl shadow p-6">
        <h2 className="text-lg font-bold text-gray-700 mb-4">
          Шаг 2: измените данные
        </h2>

        <div className="space-y-3">
          <div>
            <label className="text-xs font-bold text-gray-500 mb-1 block">Адрес SuperAdmin</label>
            <input
              value={form.sender}
              onChange={(e) => set("sender", e.target.value)}
              placeholder="0x..."
              className="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-indigo-500"
            />
          </div>

          <div>
            <label className="text-xs font-bold text-gray-500 mb-1 block">Новое имя</label>
            <input
              value={form.name}
              onChange={(e) => set("name", e.target.value)}
              placeholder="Имя"
              className="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-indigo-500"
            />
          </div>

          <div>
            <label className="text-xs font-bold text-gray-500 mb-1 block">Новый телефон</label>
            <input
              value={form.phone}
              onChange={(e) => set("phone", e.target.value)}
              placeholder="+77001234567"
              className="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-indigo-500"
            />
          </div>

          <div>
            <label className="text-xs font-bold text-gray-500 mb-2 block">Новая роль</label>
            <div className="grid grid-cols-2 gap-2">
              {[
                { id: 0, label: "👤 User",  color: "green" },
                { id: 1, label: "🛡 Admin", color: "blue"  },
              ].map((r) => (
                <button
                  key={r.id}
                  onClick={() => set("role", r.id)}
                  className={`py-2 rounded-xl text-sm font-semibold border-2 transition ${
                    form.role === r.id
                      ? r.color === "green"
                        ? "bg-green-500 text-white border-green-500"
                        : "bg-blue-500 text-white border-blue-500"
                      : "bg-white text-gray-500 border-gray-200"
                  }`}
                >
                  {r.label}
                </button>
              ))}
            </div>
          </div>

          <button
            onClick={save}
            disabled={loading || !loaded}
            className="w-full bg-purple-600 text-white font-semibold py-3 rounded-xl hover:bg-purple-700 transition disabled:opacity-50"
          >
            {loading ? "Сохранение..." : "💾 Сохранить изменения"}
          </button>
        </div>
      </div>
    </div>
  );
}