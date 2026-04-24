import { ethers } from "ethers";
import abi from "./abi.json";

// Адрес контракта — вставить сюда актуальный адрес
const CONTRACT_ADDRESS = "0xC0F63545e6EFCE544eD970f143f15bd9e225f422";

// Подключение к Ganache
const provider = new ethers.JsonRpcProvider("http://172.20.10.3:8545");

// Получить контракт (только чтение)
export const getContract = () => {
  return new ethers.Contract(CONTRACT_ADDRESS, abi, provider);
};

// Получить контракт с подписью (для транзакций)
export const getSignedContract = async (signerIndex = 0) => {
  const signer = await provider.getSigner(signerIndex);
  return new ethers.Contract(CONTRACT_ADDRESS, abi, signer);
};

// Получить все аккаунты Ganache
export const getAccounts = async () => {
  const accounts = await provider.listAccounts();
  return accounts.map((a) => a.address);
};

// Универсальный поиск адреса по имени/телефону/адресу
export const resolveIdentity = async (value) => {
  const contract = getContract();
  value = value.trim();

  // Ethereum адрес
  if (value.startsWith("0x") && value.length === 42) {
    return ethers.getAddress(value);
  }

  // Телефон
  if (value.startsWith("+") || /^\d+$/.test(value)) {
    return await contract.getAddressByPhone(value);
  }

  // Имя
  return await contract.getAddressByName(value);
};

// Словарь ролей
export const ROLES = { 0: "User", 1: "Admin", 2: "SuperAdmin" };
export const ROLE_COLORS = {
  0: "bg-green-100 text-green-700",
  1: "bg-blue-100 text-blue-700",
  2: "bg-purple-100 text-purple-700",
};