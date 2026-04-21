import type { Metadata } from "next";
import { LandingPage } from "@/components/landing/landing-page";

export const metadata: Metadata = {
  title: "RaptorFlow — AI Marketing for B2B SaaS Founders",
  description:
    "A team of 21 AI marketing specialists working on your B2B SaaS every single day. Morning briefings. Weekly campaigns. Your product deserves to be found.",
  openGraph: {
    title: "RaptorFlow — AI Marketing for B2B SaaS Founders",
    description: "Your product deserves to be found. RaptorFlow makes sure it is.",
    images: [{ url: "/og-image.png", width: 1200, height: 630 }],
  },
  twitter: {
    card: "summary_large_image",
    title: "RaptorFlow — AI Marketing for B2B SaaS Founders",
    description: "Your product deserves to be found. RaptorFlow makes sure it is.",
    images: ["/og-image.png"],
  },
};

export default function MarketingHome() {
  return <LandingPage />;
}
