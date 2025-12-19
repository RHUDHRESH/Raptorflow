"use client";

import { useAtom } from "jotai";
import { userAtom, museQuotaPercentAtom } from "@/lib/store/atoms";
import { Button } from "@/components/ui/button";
import { User, LogOut } from "lucide-react";
import { signOut } from "@/lib/api/supabase";

export function TopBar() {
  const [user] = useAtom(userAtom);
  const [museQuotaPercent] = useAtom(museQuotaPercentAtom);

  const handleSignOut = async () => {
    await signOut();
    window.location.href = "/auth/login";
  };

  return (
    <header className="fixed top-0 right-0 left-64 h-16 bg-white border-b border-gray-200 px-6 flex items-center justify-between z-30">
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2">
          <div className="text-xs">
            <p className="text-gray-600">Muse Quota</p>
            <div className="flex items-center gap-1 mt-1">
              <div className="w-32 h-2 bg-gray-200 rounded-full overflow-hidden">
                <div
                  className="h-full bg-primary transition-all"
                  style={{ width: `${Math.min(museQuotaPercent, 100)}%` }}
                />
              </div>
              <span className="font-semibold text-gray-900">
                {museQuotaPercent}%
              </span>
            </div>
          </div>
        </div>
      </div>

      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2">
          <User size={16} className="text-gray-600" />
          <span className="text-sm text-gray-700">{user?.email}</span>
        </div>
        <Button
          size="sm"
          variant="ghost"
          onClick={handleSignOut}
          className="text-gray-600 hover:text-gray-900"
        >
          <LogOut size={16} />
        </Button>
      </div>
    </header>
  );
}
