"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { useTelegram } from "@/lib/telegram";
import { devLogin, telegramLogin, useAuth } from "@/lib/api";
import { Loader2, Sparkles } from "lucide-react";

export default function HomePage() {
  const router = useRouter();
  const { user, isReady, initDataRaw, showAlert, haptic } = useTelegram();
  const { setAuth, token } = useAuth();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!isReady) return;
    (async () => {
      try {
        let auth;
        if (initDataRaw) {
          const url = new URL(window.location.href);
          const ref = url.searchParams.get("ref") || undefined;
          auth = await telegramLogin(initDataRaw, ref);
        } else {
          // Dev mode
          const tgId = user?.id || 999999;
          auth = await devLogin(tgId, user?.username, user?.first_name);
        }
        setAuth(auth.access_token, auth.user);
        haptic("success");
        router.push("/lobby");
      } catch (e: any) {
        console.error("Auth error", e);
        setError(e?.response?.data?.detail || e?.message || "Auth failed");
        setLoading(false);
      }
    })();
  }, [isReady]);

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-6 relative overflow-hidden">
      <div className="absolute inset-0 bg-grid-pattern opacity-30" />

      <motion.div
        initial={{ scale: 0.5, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.5, ease: "easeOut" }}
        className="relative z-10 text-center"
      >
        <motion.div
          animate={{ rotate: [0, 5, -5, 0] }}
          transition={{ duration: 3, repeat: Infinity }}
          className="text-8xl mb-6"
        >
          🎮
        </motion.div>

        <h1 className="font-display text-5xl md:text-6xl font-black mb-3 text-gradient">
          FIRDAVS PLAY
        </h1>
        <p className="text-cyber-muted text-base md:text-lg mb-8 flex items-center justify-center gap-2">
          <Sparkles className="w-4 h-4 text-cyber-cyan" />
          Premium Telegram Gaming
        </p>

        {loading ? (
          <div className="flex flex-col items-center gap-3 text-cyber-cyan">
            <Loader2 className="w-10 h-10 animate-spin" />
            <p className="text-sm">Authenticating...</p>
          </div>
        ) : error ? (
          <div className="glass rounded-2xl p-6 max-w-sm">
            <p className="text-cyber-red mb-4">{error}</p>
            <button
              onClick={() => window.location.reload()}
              className="w-full py-3 bg-gradient-cyber rounded-xl font-semibold"
            >
              Retry
            </button>
          </div>
        ) : null}
      </motion.div>
    </div>
  );
}
