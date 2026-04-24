import { useState } from "react";
import { getSignedContract, getAccounts, resolveIdentity, getContract } from "../contract";

export default function Access({ accounts }) {
  const [sender,   setSender]   = useState(accounts[0] || "");
  const [identity, setIdentity] = useState("");
  const [loading,  setLoading]  = useState(false);
  const [result,   setResult]   = useState(null);

  const action = async (type) => {
    if (!sender || !identity) {
      setResult({ type: "warn", msg: "Заполните все поля!" });
      return;
    }
    setLoading(true);
    setResult(null);
    try {
      const accs = await getAccounts();
      const idx  = accs.findIndex((a) => a.toLowerCase() === sender.toLowerCase());
      const adr  = await resolveIdentity(identity);

      if (type === "check") {
        const has = await getContract().checkAccess(adr);
        setResult({
          type: has ? "success" : "error",
          msg:  has ? "🔍 Доступ: ЕСТЬ ✅" : "🔍 Доступ: НЕТ ❌",
        });
        setLoading(false);
        return;
      }

      const contract = await getSignedContract(idx >= 0 ? idx : 0);
      let tx;
      if (type === "grant")  tx = await contract.grantAccess(adr);
      if (type === "revoke") tx = await contract.revokeAccess(adr);
      await tx.wait();

      setResult({
        type: "success",
        msg: type === "grant"
          ? "✅ Доступ выдан! (списана комиссия 2%)"
          : "🚫 Доступ отозван!",
      });
    } catch (e) {
      setResult({ type: "error", msg: e.reason || e.message });
    }
    setLoading(false);
  };

  const resultStyles = {
    success: "bg-green-50 text-green-700 border border-green-200",
    error:   "bg-red-50 text-red-600 border border-red-200",
    warn:    "bg-yellow-50 text-yellow-700 border border-yellow-200",
  };

  return (
    <div className="max-w-lg">
      <div className="bg-white rounded-2xl shadow p-6">
        <h2 className="text-xl font-bold text-indigo-900 mb-1">🔑 Управление доступом</h2>
        <p className="text-sm text-gray-400 mb-5">Выдайте, отзовите или проверьте доступ</p>

        <div className="space-y-3 mb-5">
          <div>
            <label className="text-xs font-bold text-gray-500 mb-1 block">Admin (кто выдаёт)</label>
            <input
              value={sender}
              onChange={(e) => setSender(e.target.value)}
              placeholder="Адрес Admin (0x...)"
              className="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-indigo-500"
            />
          </div>
          <div>
            <label className="text-xs font-bold text-gray-500 mb-1 block">Пользователь</label>
            <input
              value={identity}
              onChange={(e) => setIdentity(e.target.value)}
              placeholder="Адрес / Имя / Телефон"
              className="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-indigo-500"
            />
          </div>
        </div>

        <div className="grid gap-2">
          <button
            onClick={() => action("grant")}
            disabled={loading}
            className="w-full bg-green-600 text-white font-semibold py-3 rounded-xl hover:bg-green-700 transition disabled:opacity-50"
          >
            {loading ? "..." : "✅ Выдать доступ"}
          </button>
          <button
            onClick={() => action("revoke")}
            disabled={loading}
            className="w-full bg-red-600 text-white font-semibold py-3 rounded-xl hover:bg-red-700 transition disabled:opacity-50"
          >
            {loading ? "..." : "🚫 Отозвать доступ"}
          </button>
          <button
            onClick={() => action("check")}
            disabled={loading}
            className="w-full bg-orange-500 text-white font-semibold py-3 rounded-xl hover:bg-orange-600 transition disabled:opacity-50"
          >
            {loading ? "..." : "🔍 Проверить доступ"}
          </button>
        </div>

        {result && (
          <div className={`mt-4 text-sm text-center p-3 rounded-xl font-semibold ${resultStyles[result.type]}`}>
            {result.msg}
          </div>
        )}
      </div>
    </div>
  );
}