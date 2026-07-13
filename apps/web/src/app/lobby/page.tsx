"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { GAMES } from "@/lib/games";
import { useAuth } from "@/lib/api";
import { TopBar } from "@/components/TopBar";
import { GameCard } from "@/components/GameCard";
import { BottomNav } from "@/components/BottomNav";
import { Flame, Sparkles, Crown, Zap, TrendingUp } from "lucide-react";

export default function LobbyPage() {
  const { user } = useAuth();
  const hotGames = GAMES.filter((g) => g.hot);
  const newGames = GAMES.filter((g) => g.new);
  const allGames = GAMES.filter((g) => g.id !== "jackpot" && g.id !== "wheelduel");

  return (
    <div className="min-h-screen pb-24">
      <TopBar />

      <div className="px-4 py-6 max-w-2xl mx-auto">
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="mb-6">
          <p className="text-cyber-muted text-sm">Welcome back,</p>
          <h1 className="font-display text-3xl font-bold">
            {user?.first_name || "Player"} <span className="inline-block animate-float">👋</span>
          </h1>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="relative overflow-hidden rounded-3xl glass-strong p-6 mb-6 cyber-glow"
        >
          <div className="absolute inset-0 bg-gradient-cyber opacity-10" />
          <div className="relative z-10">
            <div className="flex items-center gap-2 mb-2">
              <Sparkles className="w-4 h-4 text-cyber-cyan" />
              <span className="text-xs font-semibold text-cyber-cyan uppercase tracking-wider">Daily Reward</span>
            </div>
            <h2 className="font-display text-2xl font-bold mb-1">Claim 100 coins</h2>
            <p className="text-cyber-muted text-sm mb-4">Come back every day to grow your streak</p>
            <Link
              href="/profile?tab=bonus"
              className="inline-flex items-center gap-2 px-4 py-2 bg-gradient-cyber rounded-full text-sm font-semibold"
            >
              <Crown className="w-4 h-4" />
              Claim Now
            </Link>
          </div>
        </motion.div>

        <div className="grid grid-cols-3 gap-3 mb-6">
          <Link href="/profile" className="glass rounded-2xl p-4 cyber-glow">
            <Zap className="w-5 h-5 text-cyber-cyan mb-1" />
            <p className="text-xs text-cyber-muted">Level</p>
            <p className="font-display text-xl font-bold">{user?.level || 1}</p>
          </Link>
          <Link href="/profile" className="glass rounded-2xl p-4 cyber-glow-purple">
            <Crown className="w-5 h-5 text-cyber-purple mb-1" />
            <p className="text-xs text-cyber-muted">XP</p>
            <p className="font-display text-xl font-bold">{(user?.xp || 0).toLocaleString()}</p>
          </Link>
          <Link href="/profile" className="glass rounded-2xl p-4">
            <TrendingUp className="w-5 h-5 text-cyber-green mb-1" />
            <p className="text-xs text-cyber-muted">Games</p>
            <p className="font-display text-xl font-bold">{user?.games_played || 0}</p>
          </Link>
        </div>

        {hotGames.length > 0 && (
          <section className="mb-6">
            <div className="flex items-center gap-2 mb-3">
              <Flame className="w-5 h-5 text-cyber-red" />
              <h2 className="font-display text-lg font-bold">Hot Games</h2>
            </div>
            <div className="grid grid-cols-1 gap-3">
              {hotGames.map((g) => <GameCard key={g.id} game={g} large />)}
            </div>
          </section>
        )}

        {newGames.length > 0 && (
          <section className="mb-6">
            <div className="flex items-center gap-2 mb-3">
              <Sparkles className="w-5 h-5 text-cyber-purple" />
              <h2 className="font-display text-lg font-bold">New</h2>
            </div>
            <div className="grid grid-cols-2 gap-3">
              {newGames.map((g) => <GameCard key={g.id} game={g} />)}
            </div>
          </section>
        )}

        <section className="mb-6">
          <h2 className="font-display text-lg font-bold mb-3">All Games</h2>
          <div className="grid grid-cols-2 gap-3">
            {allGames.map((g) => <GameCard key={g.id} game={g} />)}
          </div>
        </section>
      </div>

      <BottomNav />
    </div>
  );
}
