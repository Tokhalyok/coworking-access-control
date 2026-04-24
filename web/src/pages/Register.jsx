import { useState } from "react";
import { getSignedContract, getAccounts } from "../contract";

export default function Register({ accounts }) {
  const [form, setForm] = useState({
    sender: accounts[0] || "",
    address: "",
    name: "",
    phone: "",
    role: 0,
  });
  const [loading, setLoading] = useState(false);
  const [result, setResult]   = useState(null);

  const set = (k, v) => setForm((f) => ({ ...f, [k]: v }));

  const submit = async () => {
    if (!form.sender || !form.address || !form.name || !form.phone) {
      setResult({ ok: false, msg: "Заполните все поля!" });
      return;
    }
    setLoading(true);
    setResult(null);
    try {
      const accs = await getAccounts();
      const idx  = accs.findIndex(
        (a) => a.toLowerCase() === form.sender.toLowerCase()
      );
      const contract = await getSignedContract(idx >= 0 ? idx : 0);
      const tx = await contract.registerUser(
        form.address, form.name, form.phone, form.role
      );
      await tx.wait();
      setResult({ ok: true, msg: `✅ Пользователь '${form.name}' зарегистрирован!` });
      setForm((f) => ({ ...f, address: "", name: "", phone: "" }));
    } catch (e) {
      setResult({ ok: false, msg: e.reason || e.message });
    }
    setLoading(false);
  };

  return (
    <div className="max-w-lg">
      <div className="bg-white rounded-2xl shadow p-6">
        <h2 className="text-xl font-bold text-indigo-900 mb-1">➕ Регистрация</h2>
        <p className="text-sm text-gray-400 mb-5">Добавить нового пользователя в систему</p>

        <div className="space-y-3">
          <div>
            <label className="text-xs font-bold text-gray-500 mb-1 block">Адрес Admin/SuperAdmin</label>
            <input
              value={form.sender}
              onChange={(e) => set("sender", e.target.value)}
              placeholder="0x..."
              className="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-indigo-500"
            />
          </div>

          <div>
            <label className="text-xs font-bold text-gray-500 mb-1 block">Адрес нового пользователя</label>
            <input
              value={form.address}
              onChange={(e) => set("address", e.target.value)}
              placeholder="0x..."
              className="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-indigo-500"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-xs font-bold text-gray-500 mb-1 block">Уникальное имя</label>
              <input
                value={form.name}
                onChange={(e) => set("name", e.target.value)}
                placeholder="Алибек"
                className="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-indigo-500"
              />
            </div>
            <div>
              <label className="text-xs font-bold text-gray-500 mb-1 block">Телефон</label>
              <input
                value={form.phone}
                onChange={(e) => set("phone", e.target.value)}
                placeholder="+77001234567"
                className="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-indigo-500"
              />
            </div>
          </div>

          {/* Выбор роли */}
          <div>
            <label className="text-xs font-bold text-gray-500 mb-2 block">Роль</label>
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
                      : "bg-white text-gray-500 border-gray-200 hover:border-gray-300"
                  }`}
                >
                  {r.label}
                </button>
              ))}
            </div>
          </div>

          <button
            onClick={submit}
            disabled={loading}
            className="w-full bg-green-600 text-white font-semibold py-3 rounded-xl hover:bg-green-700 transition disabled:opacity-50 mt-2"
          >
            {loading ? "Регистрация..." : "➕ Зарегистрировать"}
          </button>

          {result && (
            <div className={`text-sm text-center p-3 rounded-xl ${
              result.ok ? "bg-green-50 text-green-700" : "bg-red-50 text-red-600"
            }`}>
              {result.msg}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}