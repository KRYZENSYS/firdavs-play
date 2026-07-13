"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { GameMeta } from "@/lib/games";
import { Flame, Sparkles } from "lucide-react";

interface Props {
  game: GameMeta;
  large?: boolean;
}

export function GameCard({ game, large }: Props) {
  const isDisabled = game.id === "jackpot" || game.id === "wheelduel";

  return (
    <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }} transition={{ type: "spring", stiffness: 400, damping: 17 }}>
      <Link
        href={isDisabled ? "#" : `/games/${game.id}`}
        className={`block relative overflow-hidden rounded-2xl bg-gradient-to-br ${game.gradient} p-${large ? "6" : "4"} ${isDisabled ? "opacity-50" : ""}`}
        onClick={(e) => isDisabled && e.preventDefault()}
      >
        <div className="absolute inset-0 bg-black/30" />
        <div className="absolute -top-6 -right-6 w-24 h-24 rounded-full bg-white/10 blur-2xl" />

        <div className="relative z-10 flex items-center justify-between">
          <div>
            <div className="flex items-center gap-1.5 mb-1">
              {game.hot && <Flame className="w-3.5 h-3.5 text-yellow-300" />}
              {game.new && <Sparkles className="w-3.5 h-3.5 text-cyan-300" />}
              {isDisabled && <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-white/20 text-white">SOON</span>}
            </div>
            <h3 className={`font-display font-bold ${large ? "text-2xl" : "text-lg"} text-white`}>
              {game.emoji} {game.name}
            </h3>
            <p className="text-white/80 text-xs mt-0.5">{game.description}</p>
            {!isDisabled && game.rtp > 0 && (
              <p className="text-white/60 text-[10px] mt-1 font-mono">RTP {game.rtp}% · Bet {game.minBet}–{game.maxBet.toLocaleString()}</p>
            )}
          </div>
          {large && <div className="text-6xl opacity-50">{game.emoji}</div>}
        </div>
      </Link>
    </motion.div>
  );
}
