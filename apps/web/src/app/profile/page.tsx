"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { Coins, Trophy, Zap, Gift, Tag, Copy, Check } from "lucide-react";
import { fetchMe, claimDaily, claimWeekly, redeemPromo, useAuth, fetchHistory } from "@/lib/api";
import { useTelegram } from "@/lib/telegram";
import { TopBar } from "@/components/TopBar";
import { BottomNav } from "@/components/BottomNav";
import { toast } from "sonner";

const BOT_USERNAME = process.env.NEXT_PUBLIC_BOT_USERNAME || "FirdavsPlayBot";

export default function ProfilePage() {
  const { user, updateUser, logout } = useAuth();
  const { haptic, share } = useTelegram();
  const qc = useQueryClient();

  const [promoCode, setPromoCode] = useState("");
  const [redeeming, setRedeeming] = useState(false);
  const [copied, setCopied] = useState(false);

  const { data: me } = useQuery({ queryKey: ["me"], queryFn: fetchMe });
  const { data: history } = useQuery({ queryKey: ["history"], queryFn: () => fetchHistory(20) });

  const refLink = `https://t.me/${BOT_USERNAME}?start=ref_${user?.telegram_id || 0}`;

  const handleClaimDaily = async () => {
    try {
      const res = await claimDaily();
      updateUser({ coins: (me?.coins || 0) + res.coins_awarded });
      qc.invalidateQueries({ queryKey: ["me"] });
      toast.success(`+${res.coins_awarded} coins claimed!`);
      haptic("success");
    } catch (e: any) {
      toast.error(e?.response?.data?.detail || "Already claimed today");
      haptic("error");
    }
  };

  const handleClaimWeekly = async () => {
    try {
      const res = await claimWeekly();
      updateUser({ coins: (me?.coins || 0) + res.coins_awarded });
      qc.invalidateQueries({ queryKey: ["me"] });
      toast.success(`+${res.coins_awarded} weekly bonus!`);
      haptic("success");
    } catch (e: any) {
      toast.error(e?.response?.data?.detail || "Already claimed this week");
      haptic("error");
    }
  };

  const handleRedeem = async () => {
    if (!promoCode.trim()) return;
    setRedeeming(true);
    try {
      const res = await redeemPromo(promoCode.toUpperCase());
      updateUser({ coins: (me?.coins || 0) + res.coins_awarded });
      qc.invalidateQueries({ queryKey: ["me"] });
      toast.success(`+${res.coins_awarded} coins!`);
      setPromoCode("");
      haptic("success");
    } catch (e: any) {
      toast.error(e?.response?.data?.detail || "Invalid code");
      haptic("error");
    } finally {
      setRedeeming(false);
    }
  };

  const copyRef = () => {
    navigator.clipboard.writeText(refLink);
    setCopied(true);
    toast.success("Referral link copied!");
    haptic("light");
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="min-h-screen pb-24">
      <TopBar />
      <div className="px-4 py-6 max-w-2xl mx-auto space-y-4">
        {/* Profile Card */}
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="glass-strong rounded-3xl p-6 cyber-glow text-center">
          <div className="w-20 h-20 rounded-full bg-gradient-cyber mx-auto mb-3 flex items-center justify-center text-3xl font-display font-bold">
            {user?.photo_url ? <img src={user.photo_url} className="w-full h-full rounded-full object-cover" alt="" /> : (user?.first_name || "P")[0].toUpperCase()}
          </div>
          <h1 className="font-display font-bold text-2xl">{user?.first_name} {user?.last_name}</h1>
          {user?.username && <p className="text-cyber-muted text-sm">@{user.username}</p>}
          {user?.is_premium && <p className="text-cyber-gold text-xs mt-1">⭐ Premium</p>}

          <div className="grid grid-cols-3 gap-2 mt-4">
            <div className="bg-cyber-bg/60 rounded-xl p-3">
              <Coins className="w-5 h-5 text-cyber-gold mx-auto mb-1" />
              <p className="text-xs text-cyber-muted">Coins</p>
              <p className="font-display font-bold text-sm">{(me?.coins || 0).toLocaleString()}</p>
            </div>
            <div className="bg-cyber-bg/60 rounded-xl p-3">
              <Zap className="w-5 h-5 text-cyber-cyan mx-auto mb-1" />
              <p className="text-xs text-cyber-muted">Level</p>
              <p className="font-display font-bold text-sm">{me?.level || 1}</p>
            </div>
            <div className="bg-cyber-bg/60 rounded-xl p-3">
              <Trophy className="w-5 h-5 text-cyber-purple mx-auto mb-1" />
              <p className="text-xs text-cyber-muted">Games</p>
              <p className="font-display font-bold text-sm">{me?.games_played || 0}</p>
            </div>
          </div>
        </motion.div>

        {/* Bonuses */}
        <div className="grid grid-cols-2 gap-3">
          <button onClick={handleClaimDaily} className="glass rounded-2xl p-4 cyber-glow active:scale-95 transition-transform">
            <Gift className="w-6 h-6 text-cyber-cyan mb-2" />
            <p className="font-bold text-sm">Daily Bonus</p>
            <p className="text-xs text-cyber-muted">+100 coins</p>
          </button>
          <button onClick={handleClaimWeekly} className="glass rounded-2xl p-4 cyber-glow-purple active:scale-95 transition-transform">
            <Gift className="w-6 h-6 text-cyber-purple mb-2" />
            <p className="font-bold text-sm">Weekly Bonus</p>
            <p className="text-xs text-cyber-muted">+1000 coins</p>
          </button>
        </div>

        {/* Promo */}
        <div className="glass rounded-3xl p-4 space-y-2">
          <div className="flex items-center gap-2">
            <Tag className="w-4 h-4 text-cyber-cyan" />
            <span className="font-bold text-sm">Promo Code</span>
          </div>
          <div className="flex gap-2">
            <input
              value={promoCode}
              onChange={(e) => setPromoCode(e.target.value.toUpperCase())}
              placeholder="WELCOME100"
              maxLength={32}
              className="flex-1 bg-cyber-bg/60 border border-cyber-border rounded-xl px-3 py-2 font-mono text-sm focus:border-cyber-cyan outline-none"
            />
            <button onClick={handleRedeem} disabled={redeeming || !promoCode} className="px-4 py-2 bg-gradient-cyber rounded-xl text-sm font-bold disabled:opacity-50">
              {redeeming ? "..." : "Apply"}
            </button>
          </div>
        </div>

        {/* Referral */}
        <div className="glass rounded-3xl p-4 space-y-2">
          <p className="font-bold text-sm flex items-center gap-2">👥 Invite Friends <span className="text-cyber-gold">+500 each</span></p>
          <div className="flex items-center gap-2">
            <code className="flex-1 bg-cyber-bg/60 rounded-lg px-3 py-2 text-xs font-mono truncate">{refLink}</code>
            <button onClick={copyRef} className="p-2 rounded-lg bg-cyber-cyan/20 text-cyber-cyan">
              {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
            </button>
            <button onClick={() => share(refLink, "Join Firdavs Play!")} className="p-2 rounded-lg bg-cyber-purple/20 text-cyber-purple text-xs">Share</button>
          </div>
        </div>

        {/* Recent Games */}
        {history && history.length > 0 && (
          <div className="glass rounded-3xl p-4">
            <p className="font-bold text-sm mb-3">🎮 Recent Games</p>
            <div className="space-y-1.5 max-h-64 overflow-y-auto no-scrollbar">
              {history.map((h: any) => (
                <div key={h.id} className="flex items-center justify-between bg-cyber-bg/40 rounded-xl px-3 py-2 text-sm">
                  <span className="capitalize">{h.game}</span>
                  <span className={h.payout > 0 ? "text-cyber-green" : "text-cyber-red"}>
                    {h.payout > 0 ? "+" : ""}{h.payout - h.bet_amount}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        <button onClick={logout} className="w-full py-3 text-cyber-red text-sm font-semibold">Sign Out</button>
      </div>
      <BottomNav />
    </div>
  );
}
