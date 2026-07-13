"use client";

import { createContext, useContext, useEffect, useState, ReactNode } from "react";
import { init, retrieveLaunchParams } from "@telegram-apps/sdk";

interface TelegramUser {
  id: number;
  first_name: string;
  last_name?: string;
  username?: string;
  photo_url?: string;
  language_code?: string;
  is_premium?: boolean;
}

interface TelegramContextValue {
  user: TelegramUser | null;
  initData: string;
  initDataRaw: string;
  isReady: boolean;
  webApp: any;
  colorScheme: "light" | "dark";
  haptic: (type: "light" | "medium" | "heavy" | "success" | "warning" | "error") => void;
  showAlert: (msg: string) => void;
  showConfirm: (msg: string) => Promise<boolean>;
  close: () => void;
  expand: () => void;
  ready: () => void;
  share: (url: string, text?: string) => void;
}

const TelegramContext = createContext<TelegramContextValue | null>(null);

export function TelegramProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<TelegramUser | null>(null);
  const [isReady, setIsReady] = useState(false);
  const [webApp, setWebApp] = useState<any>(null);
  const [initDataRaw, setInitDataRaw] = useState("");

  useEffect(() => {
    if (typeof window === "undefined") return;

    try {
      const params = retrieveLaunchParams();
      if (params.tgWebAppData?.user) {
        setUser({
          id: params.tgWebAppData.user.id,
          first_name: params.tgWebAppData.user.first_name,
          last_name: params.tgWebAppData.user.last_name,
          username: params.tgWebAppData.user.username,
          photo_url: params.tgWebAppData.user.photo_url,
          language_code: params.tgWebAppData.user.language_code,
          is_premium: params.tgWebAppData.user.is_premium,
        });
        setInitDataRaw(params.tgWebAppData.rawData || "");
      }

      const wa = (window as any).Telegram?.WebApp;
      if (wa) {
        setWebApp(wa);
        wa.ready();
        wa.expand();
        setIsReady(true);
      } else {
        setIsReady(true);
      }
    } catch (e) {
      console.warn("Telegram init failed, falling back to dev mode", e);
      setIsReady(true);
    }
  }, []);

  const haptic = (type: TelegramContextValue["haptic"] extends (...args: any) => any ? Parameters<TelegramContextValue["haptic"]>[0] : never) => {
    if (webApp?.HapticFeedback?.impactOccurred) {
      const map: any = { light: "light", medium: "medium", heavy: "heavy", success: "light", warning: "medium", error: "heavy" };
      webApp.HapticFeedback.impactOccurred(map[type] || "light");
    }
  };

  const showAlert = (msg: string) => webApp?.showAlert?.(msg) ?? alert(msg);
  const showConfirm = async (msg: string) => {
    if (webApp?.showConfirm) return new Promise<boolean>((res) => webApp.showConfirm(msg, res));
    return confirm(msg);
  };
  const close = () => webApp?.close?.();
  const expand = () => webApp?.expand?.();
  const ready = () => webApp?.ready?.();
  const share = (url: string, text?: string) => {
    const fullText = `${text || ""} ${url}`.trim();
    if (navigator.share) {
      navigator.share({ url, text: fullText }).catch(() => {});
    } else {
      navigator.clipboard?.writeText(url);
    }
  };

  const colorScheme = (webApp?.colorScheme as "light" | "dark") || "dark";

  return (
    <TelegramContext.Provider
      value={{
        user, isReady, webApp, initData: initDataRaw, initDataRaw, colorScheme,
        haptic, showAlert, showConfirm, close, expand, ready, share,
      }}
    >
      {children}
    </TelegramContext.Provider>
  );
}

export function useTelegram() {
  const ctx = useContext(TelegramContext);
  if (!ctx) throw new Error("useTelegram must be inside TelegramProvider");
  return ctx;
}
