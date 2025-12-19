"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAtom } from "jotai";
import { userAtom } from "@/lib/store/atoms";
import { supabase } from "@/lib/api/supabase";
import { Sidebar } from "@/components/layout/Sidebar";
import { TopBar } from "@/components/layout/TopBar";
import { QueryProvider } from "@/components/providers/QueryProvider";
import { JotaiProvider } from "@/components/providers/JotaiProvider";

export default function AppLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const [, setUser] = useAtom(userAtom);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const {
          data: { user },
        } = await supabase.auth.getUser();

        if (!user) {
          router.push("/auth/login");
          return;
        }

        setUser({
          id: user.id,
          email: user.email || "",
          created_at: user.created_at || new Date().toISOString(),
        });
      } catch (error) {
        console.error("Auth check failed:", error);
        router.push("/auth/login");
      } finally {
        setLoading(false);
      }
    };

    checkAuth();
  }, [router, setUser]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-gray-50">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-gray-200 border-t-primary rounded-full animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <JotaiProvider>
      <QueryProvider>
        <div className="flex">
          <Sidebar />
          <TopBar />
          <main className="w-full pt-16 pl-64">
            {children}
          </main>
        </div>
      </QueryProvider>
    </JotaiProvider>
  );
}
