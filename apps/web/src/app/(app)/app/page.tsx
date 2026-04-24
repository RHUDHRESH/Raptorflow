"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import type { Route } from "next";

export default function AppHomePage() {
  const router = useRouter();
  useEffect(() => {
    router.replace("/app/dashboard" as Route);
  }, [router]);
  return null;
}
