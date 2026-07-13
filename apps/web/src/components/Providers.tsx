"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useState } from "react";
import { TelegramProvider } from "@/lib/telegram";
import { Toaster } from "sonner";

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 30_000,
            refetchOnWindowFocus: false,
            retry: 1,
          },
        },
      })
  );

  return (
    <QueryClientProvider client={queryClient}>
      <TelegramProvider>
        {children}
        <Toaster
          position="top-center"
          theme="dark"
          toastOptions={{
            style: {
              background: "rgba(15, 22, 41, 0.95)",
              border: "1px solid rgba(0, 217, 255, 0.2)",
              color: "#e2e8f0",
              backdropFilter: "blur(20px)",
            },
          }}
        />
      </TelegramProvider>
    </QueryClientProvider>
  );
}
