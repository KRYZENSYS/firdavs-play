"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Home, Gamepad2, Trophy, User } from "lucide-react";
import { cn } from "@/lib/cn";

const ITEMS = [
  { href: "/lobby",         icon: Home,     label: "Home" },
  { href: "/games/crash",   icon: Gamepad2, label: "Games" },
  { href: "/leaderboard",   icon: Trophy,   label: "Ranks" },
  { href: "/profile",       icon: User,     label: "Profile" },
];

export function BottomNav() {
  const path = usePathname();
  return (
    <nav className="fixed bottom-0 left-0 right-0 z-50 glass-strong border-t border-cyber-border">
      <div className="max-w-2xl mx-auto grid grid-cols-4">
        {ITEMS.map((it) => {
          const active = path === it.href || (it.href !== "/lobby" && path?.startsWith(it.href));
          return (
            <Link
              key={it.href}
              href={it.href}
              className={cn(
                "flex flex-col items-center gap-1 py-2.5 transition-colors",
                active ? "text-cyber-cyan" : "text-cyber-muted"
              )}
            >
              <it.icon className={cn("w-5 h-5", active && "drop-shadow-[0_0_8px_rgba(0,217,255,0.6)]")} />
              <span className="text-[10px] font-medium">{it.label}</span>
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
