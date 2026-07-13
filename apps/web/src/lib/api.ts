import axios from "axios";
import { create } from "zustand";
import { persist } from "zustand/middleware";

// Empty = same origin (Replit). Set NEXT_PUBLIC_API_URL to override.
const API_URL = process.env.NEXT_PUBLIC_API_URL || "";

export const api = axios.create({
  baseURL: `${API_URL}/api/v1`,
  headers: { "Content-Type": "application/json" },
});

let getToken: () => string | null = () => null;
export function setTokenGetter(fn: () => string | null) { getToken = fn; }

api.interceptors.request.use((config) => {
  const token = getToken();
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (r) => r,
  (err) => {
    if (err.response?.status === 401) {
      useAuth.getState().logout();
    }
    return Promise.reject(err);
  }
);

export interface User {
  id: number;
  telegram_id: number;
  username: string | null;
  first_name: string | null;
  last_name: string | null;
  photo_url: string | null;
  coins: number;
  xp: number;
  level: number;
  games_played: number;
  is_premium: boolean;
  is_admin?: boolean;
  created_at: string;
}

export interface AuthState {
  token: string | null;
  user: User | null;
  setAuth: (token: string, user: User) => void;
  updateUser: (user: Partial<User>) => void;
  logout: () => void;
}

export const useAuth = create<AuthState>()(
  persist(
    (set) => ({
      token: null, user: null,
      setAuth: (token, user) => set({ token, user }),
      updateUser: (user) => set((s) => ({ user: s.user ? { ...s.user, ...user } : null })),
      logout: () => set({ token: null, user: null }),
    }),
    { name: "firdavs-auth" }
  )
);

setTokenGetter(() => useAuth.getState().token);

// ===== API helpers =====
export async function telegramLogin(initData: string, referral?: string) {
  const { data } = await api.post("/auth/telegram", { init_data: initData, referral_code: referral });
  return data;
}

export async function devLogin(telegram_id: number, username?: string, first_name?: string) {
  const { data } = await api.post("/auth/dev", { telegram_id, username, first_name });
  return data;
}

export async function fetchMe() {
  const { data } = await api.get("/users/me");
  return data;
}

export async function claimDaily() {
  const { data } = await api.post("/users/daily-bonus");
  return data;
}

export async function claimWeekly() {
  const { data } = await api.post("/users/weekly-bonus");
  return data;
}

export async function placeBet(game: string, bet_amount: number, client_seed?: string, payload?: any) {
  const { data } = await api.post("/games/bet", { game, bet_amount, client_seed, payload });
  return data;
}

export async function crashCashout(round_id: number, multiplier: number) {
  const { data } = await api.post("/games/cashout", { round_id, multiplier });
  return data;
}

export async function listMissions() {
  const { data } = await api.get("/missions");
  return data;
}

export async function claimMission(id: number) {
  const { data } = await api.post(`/missions/${id}/claim`);
  return data;
}

export async function listAchievements() {
  const { data } = await api.get("/missions/achievements");
  return data;
}

export async function listInventory() {
  const { data } = await api.get("/inventory");
  return data;
}

export async function listNotifications(unreadOnly = false) {
  const { data } = await api.get("/notifications", { params: { unread_only: unreadOnly } });
  return data;
}

export async function markAllNotificationsRead() {
  const { data } = await api.post("/notifications/read-all");
  return data;
}

export async function redeemPromo(code: string) {
  const { data } = await api.post("/promo/redeem", { code });
  return data;
}

export async function leaderboard(by: "coins" | "xp" | "wagered" = "coins", limit = 50) {
  const { data } = await api.get(`/leaderboard/${by}`, { params: { limit } });
  return data;
}

export async function fetchHistory(limit = 50) {
  const { data } = await api.get("/users/history", { params: { limit } });
  return data;
}

// Admin
export async function adminStats() {
  const { data } = await api.get("/admin/stats");
  return data;
}
export async function adminListUsers(limit = 50, offset = 0) {
  const { data } = await api.get("/admin/users", { params: { limit, offset } });
  return data;
}
export async function adminAdjustCoins(user_id: number, delta: number, reason: string) {
  const { data } = await api.post("/admin/coins", { user_id, delta, reason });
  return data;
}
export async function adminBanUser(user_id: number, ban: boolean, reason?: string) {
  const { data } = await api.post("/admin/ban", { user_id, ban, reason });
  return data;
}
export async function adminCreatePromo(code: string, reward_coins: number, max_uses = 1) {
  const { data } = await api.post("/admin/promo", { code, reward_coins, max_uses });
  return data;
}
export async function adminListLogs(limit = 100, action?: string) {
  const { data } = await api.get("/admin/logs", { params: { limit, action } });
  return data;
}
export async function adminBroadcast(title: string, body: string, type = "announcement") {
  const { data } = await api.post("/admin/broadcast", { title, body, type });
  return data;
}
