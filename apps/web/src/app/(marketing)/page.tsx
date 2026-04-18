import type { Metadata } from "next";
import { LandingPage } from "@/components/landing/landing-page";

export const metadata: Metadata = {
  title: "RaptorFlow - AI-native marketing execution for Indian SMBs",
  description:
    "RaptorFlow turns business context into campaigns, competitor intelligence, daily action, and compounding marketing memory.",
};

export default function MarketingHome() {
  return <LandingPage />;
}
