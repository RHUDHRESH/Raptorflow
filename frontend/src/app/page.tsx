import { Metadata } from 'next';
import LandingPage from "@/components/landing/LandingPage";
import LandingPageV2 from "@/components/landing/v2/LandingPageV2";

export const metadata: Metadata = {
  title: "RaptorFlow | Founder Marketing Operating System",
  description: "Stop guessing. Start executing. The unified operating system for founder-led marketing.",
};

// Feature flag: Set USE_LANDING_V2=true in .env.local to enable new landing page
// Feature flags
const USE_V2 = process.env.NEXT_PUBLIC_USE_LANDING_V2 === 'true';
const USE_V3 = true; // Hardcoded for development iteration

import LandingPageV3 from "@/components/landing/v3/LandingPageV3";

export default function RootPage() {
  if (USE_V3) return <LandingPageV3 />;
  return USE_V2 ? <LandingPageV2 /> : <LandingPage />;
}

