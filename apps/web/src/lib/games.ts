export interface GameMeta {
  id: string;
  name: string;
  emoji: string;
  description: string;
  category: "instant" | "crash" | "skill" | "lottery";
  rtp: number;
  minBet: number;
  maxBet: number;
  color: string;
  gradient: string;
  hot?: boolean;
  new?: boolean;
}

export const GAMES: GameMeta[] = [
  { id: "crash",     name: "Crash",        emoji: "🚀", description: "Cash out before the rocket explodes",  category: "crash",   rtp: 96, minBet: 10, maxBet: 100000, color: "#ef4444", gradient: "from-red-500 to-orange-500", hot: true },
  { id: "mines",     name: "Mines",        emoji: "💣", description: "Reveal safe tiles, avoid mines",        category: "skill",   rtp: 97, minBet: 10, maxBet: 50000,  color: "#f59e0b", gradient: "from-amber-500 to-yellow-500" },
  { id: "plinko",    name: "Plinko",       emoji: "🎯", description: "Drop a ball, win up to x1000",         category: "instant", rtp: 96, minBet: 10, maxBet: 10000,  color: "#3b82f6", gradient: "from-blue-500 to-cyan-500" },
  { id: "dice",      name: "Dice",         emoji: "🎲", description: "Roll over or under your target",       category: "instant", rtp: 98, minBet: 10, maxBet: 100000, color: "#22c55e", gradient: "from-green-500 to-emerald-500" },
  { id: "coinflip",  name: "Coin Flip",    emoji: "🪙", description: "Heads or tails, double or nothing",    category: "instant", rtp: 95, minBet: 10, maxBet: 50000,  color: "#eab308", gradient: "from-yellow-500 to-amber-500" },
  { id: "wheel",     name: "Lucky Wheel",  emoji: "🎡", description: "Spin to win up to x10",                category: "instant", rtp: 95, minBet: 10, maxBet: 25000,  color: "#a855f7", gradient: "from-purple-500 to-pink-500" },
  { id: "cardpick",  name: "Card Pick",    emoji: "🃏", description: "Pick the highest card, win x4",        category: "skill",   rtp: 96, minBet: 10, maxBet: 25000,  color: "#ec4899", gradient: "from-pink-500 to-rose-500" },
  { id: "keno",      name: "Keno",         emoji: "🔢", description: "Pick numbers, win up to x1000",        category: "lottery", rtp: 95, minBet: 10, maxBet: 10000,  color: "#06b6d4", gradient: "from-cyan-500 to-teal-500" },
  { id: "limbo",     name: "Limbo",        emoji: "📈", description: "Bet on a multiplier, win or lose",     category: "instant", rtp: 96, minBet: 10, maxBet: 100000, color: "#8b5cf6", gradient: "from-violet-500 to-purple-500", new: true },
  { id: "hilo",      name: "Hi-Lo",        emoji: "🎴", description: "Guess higher or lower",                category: "skill",   rtp: 95, minBet: 10, maxBet: 50000,  color: "#10b981", gradient: "from-emerald-500 to-green-500" },
  { id: "towers",    name: "Towers",       emoji: "🗼", description: "Climb up, avoid the bombs",            category: "skill",   rtp: 96, minBet: 10, maxBet: 25000,  color: "#f97316", gradient: "from-orange-500 to-red-500" },
  { id: "jackpot",   name: "Jackpot",      emoji: "💎", description: "Coming soon",                          category: "lottery", rtp: 0,  minBet: 0,  maxBet: 0,      color: "#fbbf24", gradient: "from-yellow-400 to-amber-600" },
  { id: "wheelduel", name: "Wheel Duel",   emoji: "⚔️", description: "Coming soon",                          category: "lottery", rtp: 0,  minBet: 0,  maxBet: 0,      color: "#dc2626", gradient: "from-red-600 to-pink-600" },
];

export function getGame(id: string): GameMeta | undefined {
  return GAMES.find((g) => g.id === id);
}
