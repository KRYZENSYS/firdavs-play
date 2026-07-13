"use client";

import { useEffect, useRef, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { io, Socket } from "socket.io-client";
import { useQueryClient } from "@tanstack/react-query";
import { ArrowLeft, Rocket } from "lucide-react";
import Link from "next/link";
import { placeBet, crashCashout, useAuth } from "@/lib/api";
import { useTelegram } from "@/lib/telegram";
import { BetPanel } from "@/components/BetPanel";
import { TopBar } from "@/components/TopBar";
import { BottomNav } from "@/components/BottomNav";

const API_URL = (process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000").replace(/\/api\/v1\/?$/, "");

export default function CrashPage() {
  const { token, updateUser } = useAuth();
  const { haptic } = useTelegram();
  const qc = useQueryClient();

  const [multiplier, setMultiplier] = useState(1.0);
  const [crashed, setCrashed] = useState(false);
  const [crashPoint, setCrashPoint] = useState<number | null>(null);
  const [status, setStatus] = useState<"waiting" | "flying" | "crashed">("waiting");
  const [activeRoundId, setActiveRoundId] = useState<number | null>(null);
  const [cashedOut, setCashedOut] = useState(false);
  const socketRef = useRef<Socket | null>(null);

  useEffect(() => {
    if (!token) return;
    const s = io(`${API_URL}/ws/crash`, {
      query: { token },
      transports: ["websocket"],
    });
    socketRef.current = s;

    s.on("connect", () => console.log("crash ws connected"));
    s.on("disconnect", () => console.log("crash ws disconnected"));

    s.on("crash_round", (data: any) => {
      setStatus("flying");
      setCrashed(false);
      setCashedOut(false);
      setActiveRoundId(null);
      setCrashPoint(data.crash_point);
      setMultiplier(1.0);

      // Animate multiplier using requestAnimationFrame
      const start = Date.now();
      const dur = 8000; // round duration ~8s
      const target = data.crash_point;

      const tick = () => {
        const elapsed = (Date.now() - start) / 1000;
        const newMult = Math.min(target, 1 + elapsed * (target - 1) / dur);
        setMultiplier(newMult);
        if (newMult >= target) {
          setCrashed(true);
          setStatus("crashed");
          setMultiplier(target);
          return;
        }
        requestAnimationFrame(tick);
      };
      requestAnimationFrame(tick);
    });

    return () => {
      s.disconnect();
    };
  }, [token]);

  const handleBet = async (amount: number) => {
    const res = await placeBet("crash", amount);
    updateUser({ coins: res.new_balance });
    setActiveRoundId(res.round_id);
    haptic("success");
  };

  const handleCashout = async () => {
    if (!activeRoundId || cashedOut || crashed) return;
    const res = await crashCashout(activeRoundId, multiplier);
    updateUser({ coins: res.new_balance });
    setCashedOut(true);
    haptic("success");
    qc.invalidateQueries({ queryKey: ["me"] });
  };

  const multColor = crashed ? "text-cyber-red" : status === "flying" ? "text-cyber-cyan" : "text-cyber-text";

  return (
    <div className="min-h-screen pb-24">
      <TopBar />
      <div className="px-4 py-4 max-w-2xl mx-auto">
        <Link href="/lobby" className="inline-flex items-center gap-1 text-cyber-muted text-sm mb-3">
          <ArrowLeft className="w-4 h-4" /> Back
        </Link>

        <div className="glass-strong rounded-3xl p-6 mb-4 relative overflow-hidden">
          <div className="absolute inset-0 bg-grid-pattern opacity-20" />
          <AnimatePresence mode="wait">
            {status === "waiting" && (
              <motion.div key="waiting" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="text-center py-12">
                <Rocket className="w-16 h-16 mx-auto text-cyber-cyan animate-float" />
                <p className="text-cyber-muted mt-3">Waiting for next round...</p>
              </motion.div>
            )}

            {status === "flying" && (
              <motion.div key="flying" initial={{ scale: 0.8, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} className="text-center py-8">
                <motion.div animate={{ y: [-10, 10, -10] }} transition={{ duration: 1, repeat: Infinity }} className="text-6xl mb-3">🚀</motion.div>
                <p className={`font-display font-black text-7xl ${multColor} cyber-glow`}>
                  {multiplier.toFixed(2)}x
                </p>
              </motion.div>
            )}

            {status === "crashed" && (
              <motion.div key="crashed" initial={{ scale: 0.5, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} className="text-center py-8">
                <p className="text-6xl mb-3">💥</p>
                <p className="font-display font-black text-5xl text-cyber-red mb-1">
                  {crashPoint?.toFixed(2)}x
                </p>
                <p className="text-cyber-muted">Crashed!</p>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {status === "flying" && activeRoundId && !cashedOut && !crashed && (
          <motion.button
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            onClick={handleCashout}
            className="w-full py-5 mb-3 rounded-2xl bg-gradient-to-r from-cyber-green to-emerald-500 text-cyber-bg font-display font-black text-xl cyber-glow active:scale-95"
          >
            💰 CASHOUT @ {multiplier.toFixed(2)}x
          </motion.button>
        )}

        {cashedOut && (
          <div className="text-center py-3 mb-3 rounded-2xl bg-cyber-green/20 text-cyber-green font-bold">
            ✓ Cashed out @ {multiplier.toFixed(2)}x
          </div>
        )}

        <BetPanel game="crash" onBet={handleBet} disabled={status !== "waiting" || !!activeRoundId} />
      </div>
      <BottomNav />
    </div>
  );
}
