"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Minus, Plus, Coins, Loader2 } from "lucide-react";
import { cn } from "@/lib/cn";
import { useAuth } from "@/lib/api";
import { useTelegram } from "@/lib/telegram";

interface Props {
  game: string;
  minBet?: number;
  maxBet?: number;
  onBet: (amount: number) => Promise<void>;
  disabled?: boolean;
}

const QUICK_AMOUNTS = [10, 50, 100, 500, 1000, 5000];

export function BetPanel({ game, minBet = 10, maxBet = 100000, onBet, disabled }: Props) {
  const { user, updateUser } = useAuth();
  const { haptic } = useTelegram();
  const [amount, setAmount] = useState(100);
  const [busy, setBusy] = useState(false);
  const [lastResult, setLastResult] = useState<{ won: boolean; amount: number } | null>(null);

  const balance = user?.coins || 0;
  const canBet = amount >= minBet && amount <= maxBet && amount <= balance;

  const adjust = (delta: number) => {
    const next = Math.max(minBet, Math.min(maxBet, Math.min(balance, amount + delta)));
    setAmount(next);
    haptic("light");
  };

  const setRatio = (ratio: number) => {
    setAmount(Math.max(minBet, Math.floor(balance * ratio)));
    haptic("light");
  };

  const handleBet = async () => {
    if (!canBet || busy) return;
    setBusy(true);
    setLastResult(null);
    try {
      await onBet(amount);
      setLastResult({ won: true, amount: 0 });
      haptic("success");
    } catch (e: any) {
      haptic("error");
      setLastResult({ won: false, amount: 0 });
    } finally {
      setBusy(false);
      setTimeout(() => setLastResult(null), 2000);
    }
  };

  return (
    <div className="glass rounded-3xl p-4 space-y-3">
      <div className="flex items-center justify-between">
        <span className="text-xs text-cyber-muted uppercase tracking-wider">Bet Amount</span>
        <div className="flex items-center gap-1 text-sm">
          <Coins className="w-4 h-4 text-cyber-gold" />
          <span className="font-mono font-bold">{balance.toLocaleString()}</span>
        </div>
      </div>

      <div className="flex items-center gap-2">
        <button
          onClick={() => adjust(-Math.max(10, Math.floor(amount * 0.1)))}
          className="w-10 h-10 rounded-xl bg-cyber-bg/60 border border-cyber-border flex items-center justify-center active:scale-95"
          disabled={disabled}
        >
          <Minus className="w-4 h-4" />
        </button>
        <div className="flex-1 relative">
          <input
            type="number"
            value={amount}
            onChange={(e) => setAmount(Math.max(0, Math.min(maxBet, parseInt(e.target.value) || 0)))}
            className="w-full bg-cyber-bg/60 border border-cyber-cyan/30 rounded-xl px-4 py-2.5 text-center font-mono font-bold text-lg focus:border-cyber-cyan outline-none"
            disabled={disabled}
          />
        </div>
        <button
          onClick={() => adjust(Math.max(10, Math.floor(amount * 0.1)))}
          className="w-10 h-10 rounded-xl bg-cyber-bg/60 border border-cyber-border flex items-center justify-center active:scale-95"
          disabled={disabled}
        >
          <Plus className="w-4 h-4" />
        </button>
      </div>

      <div className="grid grid-cols-6 gap-1.5">
        {QUICK_AMOUNTS.map((a) => (
          <button
            key={a}
            onClick={() => { setAmount(Math.min(a, balance)); haptic("light"); }}
            className={cn(
              "py-1.5 rounded-lg text-xs font-mono font-semibold transition-all",
              amount === a ? "bg-cyber-cyan text-cyber-bg" : "bg-cyber-bg/40 text-cyber-muted hover:bg-cyber-bg/70"
            )}
            disabled={disabled}
          >
            {a >= 1000 ? `${a / 1000}K` : a}
          </button>
        ))}
      </div>

      <div className="grid grid-cols-4 gap-1.5">
        {[0.25, 0.5, 0.75, 1].map((r) => (
          <button
            key={r}
            onClick={() => setRatio(r)}
            className="py-1 rounded-lg bg-cyber-bg/40 text-cyber-muted text-[10px] font-mono hover:bg-cyber-bg/70"
            disabled={disabled}
          >
            {r === 1 ? "MAX" : `${r * 100}%`}
          </button>
        ))}
      </div>

      <AnimatePresence>
        {lastResult && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className={cn(
              "rounded-xl p-2 text-center text-sm font-bold",
              lastResult.won ? "bg-cyber-green/20 text-cyber-green" : "bg-cyber-red/20 text-cyber-red"
            )}
          >
            {lastResult.won ? "✓ Bet placed" : "✗ Bet failed"}
          </motion.div>
        )}
      </AnimatePresence>

      <button
        onClick={handleBet}
        disabled={!canBet || busy || disabled}
        className={cn(
          "w-full py-4 rounded-2xl font-display font-bold text-lg transition-all",
          "bg-gradient-cyber text-cyber-bg",
          "disabled:opacity-40 disabled:cursor-not-allowed",
          "active:scale-[0.98] cyber-glow"
        )}
      >
        {busy ? (
          <Loader2 className="w-5 h-5 animate-spin mx-auto" />
        ) : (
          <>🎲 {canBet ? "Place Bet" : (balance < minBet ? "Insufficient Balance" : "Invalid Bet")}</>
        )}
      </button>
    </div>
  );
}
