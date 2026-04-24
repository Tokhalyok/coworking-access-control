import { useState } from "react";
import { getSignedContract, getAccounts, resolveIdentity } from "../contract";

export default function Door() {
  const [identity, setIdentity] = useState("");
  const [loading,  setLoading]  = useState(false);
  const [status,   setStatus]   = useState(null); // null | "open" | "closed"

  const enter = async () => {
    if (!identity.trim()) return;
    setLoading(true);
    setStatus(null);
    try {
      const accs    = await getAccounts();
      const address = await resolveIdentity(identity);
      const idx     = accs.findIndex((a) => a.toLowerCase() === address.toLowerCase());
      const contract = await getSignedContract(idx >= 0 ? idx : 0);
      const tx      = await contract.tryEntry();
      const receipt = await tx.wait();

      // Читаем событие EntryLogged
      const iface  = contract.interface;
      let granted  = false;
      for (const log of receipt.logs) {
        try {
          const parsed = iface.parseLog(log);
          if (parsed.name === "EntryLogged") {
            granted = parsed.args.granted;
            break;
          }
        } catch {}
      }

      setStatus(granted ? "open" : "closed");

      // Закрываем замок через 3 секунды
      if (granted) {
        setTimeout(() => setStatus("closed"), 3000);
      }
    } catch (e) {
      setStatus("error");
    }
    setLoading(false);
  };

  return (
    <div className="flex justify-center">
      <div className="bg-white rounded-2xl shadow p-8 w-full max-w-md text-center">
        <h2 className="text-xl font-bold text-indigo-900 mb-1">🚪 Эмулятор замка</h2>
        <p className="text-sm text-gray-400 mb-6">
          Введите адрес, имя или телефон и войдите в коворкинг
        </p>

        <input
          value={identity}
          onChange={(e) => setIdentity(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && enter()}
          placeholder="Адрес / Имя / Телефон"
          className="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-indigo-500 mb-4"
        />

        {/* Большой замок */}
        <div className="my-6">
          {status === "open" ? (
            <div className="text-8xl animate-bounce">🔓</div>
          ) : status === "closed" ? (
            <div className="text-8xl">🔒</div>
          ) : status === "error" ? (
            <div className="text-8xl">❌</div>
          ) : (
            <div className="text-8xl text-gray-200">🔒</div>
          )}
        </div>

        {/* Сообщение */}
        <div className={`mb-6 text-base font-bold ${
          status === "open"   ? "text-green-600" :
          status === "closed" ? "text-red-600"   :
          status === "error"  ? "text-red-500"   :
          "text-gray-300"
        }`}>
          {status === "open"   && "Добро пожаловать! 🎉"}
          {status === "closed" && "Доступ запрещён!"}
          {status === "error"  && "Произошла ошибка"}
          {status === null     && "Ожидание..."}
        </div>

        <button
          onClick={enter}
          disabled={loading}
          className="w-full bg-indigo-900 text-white font-bold py-4 rounded-xl text-lg hover:bg-indigo-800 transition disabled:opacity-50"
        >
          {loading ? "Проверка..." : "🚶 Войти в коворкинг"}
        </button>
      </div>
    </div>
  );
}