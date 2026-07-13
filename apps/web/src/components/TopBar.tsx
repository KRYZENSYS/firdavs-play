"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { useQuery } from "@tanstack/react-query";
import { Bell, Coins, Plus } from "lucide-react";
import { fetchMe, useAuth } from "@/lib/api";

export function TopBar() {
  const { user, updateUser } = useAuth();

  const { data } = useQuery({
    queryKey: ["me"],
    queryFn: fetchMe,
    refetchInterval: 30000,
    onSuccess: (data) => updateUser(data),
  });

  return (
    <div className="sticky top-0 z-40 glass-strong border-b border-cyber-border">
      <div className="max-w-2xl mx-auto px-4 py-3 flex items-center justify-between gap-3">
        <Link href="/lobby" className="flex items-center gap-2">
          <div className="w-9 h-9 rounded-xl bg-gradient-cyber flex items-center justify-center text-lg">
            🎮
          </div>
          <span className="font-display font-bold text-base hidden sm:block">FIRDAVS</span>
        </Link>

        <motion.div
          whileTap={{ scale: 0.95 }}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-cyber-bg/80 border border-cyber-cyan/30"
        >
          <Coins className="w-4 h-4 text-cyber-gold" />
          <span className="font-mono font-bold text-sm">{(user?.coins || 0).toLocaleString()}</span>
          <Link
            href="/profile?tab=bonus"
            className="ml-1 w-5 h-5 rounded-full bg-cyber-cyan/20 flex items-center justify-center"
          >
            <Plus className="w-3 h-3 text-cyber-cyan" />
          </Link>
        </motion.div>

        <div className="flex items-center gap-2">
          <Link
            href="/notifications"
            className="w-9 h-9 rounded-xl bg-cyber-bg/60 border border-cyber-border flex items-center justify-center"
          >
            <Bell className="w-4 h-4 text-cyber-cyan" />
          </Link>
          <Link
            href="/profile"
            className="w-9 h-9 rounded-full bg-gradient-cyber flex items-center justify-center font-bold text-sm"
          >
            {user?.photo_url ? (
              <img src={user.photo_url} alt="" className="w-full h-full rounded-full object-cover" />
            ) : (
              <span>{(user?.first_name || "P")[0].toUpperCase()}</span>
            )}
          </Link>
        </div>
      </div>
    </div>
  );
}
