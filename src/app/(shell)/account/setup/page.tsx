"use client";

import { FormEvent, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { createClient } from "@/lib/supabase/client";
import { useAuthStore } from "@/stores/authStore";
import { getAccountProfileState } from "@/lib/auth/account";

export default function AccountSetupPage() {
  const router = useRouter();
  const { session, setSession } = useAuthStore();

  const metadata = session?.user?.user_metadata ?? {};
  const [fullName, setFullName] = useState((metadata.full_name as string) ?? "");
  const [jobTitle, setJobTitle] = useState((metadata.job_title as string) ?? "");
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const profileState = useMemo(() => getAccountProfileState(session?.user), [session?.user]);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);

    if (!fullName.trim()) {
      setError("Please enter your full name.");
      return;
    }

    setIsSaving(true);
    try {
      const supabase = createClient();
      const { error: updateError } = await supabase.auth.updateUser({
        data: {
          full_name: fullName.trim(),
          job_title: jobTitle.trim() || null,
        },
      });

      if (updateError) {
        setError(updateError.message);
        return;
      }

      const {
        data: { session: refreshedSession },
      } = await supabase.auth.getSession();
      setSession(refreshedSession);
      router.replace("/onboarding");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to save account profile.");
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-6">
      <div className="w-full max-w-lg bg-white rounded-xl shadow-sm border border-gray-200 p-8">
        <p className="text-xs uppercase tracking-widest text-gray-500 mb-2">Account Setup</p>
        <h1 className="text-2xl font-semibold text-gray-900">Complete your profile</h1>
        <p className="text-sm text-gray-600 mt-2 mb-6">
          Add your account details before we move into workspace onboarding.
        </p>

        {profileState.missingRequiredFields.length > 0 && (
          <div className="mb-4 rounded-md border border-amber-200 bg-amber-50 p-3 text-sm text-amber-900">
            Missing required fields: {profileState.missingRequiredFields.join(", ")}
          </div>
        )}

        {error && (
          <div className="mb-4 rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-700">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <label className="block">
            <span className="text-sm font-medium text-gray-700">Full name *</span>
            <input
              type="text"
              value={fullName}
              onChange={(event) => setFullName(event.target.value)}
              className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
              placeholder="Jane Doe"
              required
            />
          </label>

          <label className="block">
            <span className="text-sm font-medium text-gray-700">Job title</span>
            <input
              type="text"
              value={jobTitle}
              onChange={(event) => setJobTitle(event.target.value)}
              className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
              placeholder="Head of Growth"
            />
          </label>

          <button
            type="submit"
            disabled={isSaving}
            className="w-full rounded-md bg-gray-900 text-white py-2 text-sm font-medium disabled:opacity-60"
          >
            {isSaving ? "Saving..." : "Continue to onboarding"}
          </button>
        </form>
      </div>
    </div>
  );
}
