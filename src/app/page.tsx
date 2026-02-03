import { Navbar } from "@/components/landing/Navbar";
import { EnhancedHero } from "@/components/landing/EnhancedHero";
import { EnhancedFeatures } from "@/components/landing/EnhancedFeatures";
import { HowItWorks } from "@/components/landing/HowItWorks";
import { Pricing } from "@/components/landing/Pricing";
import { FinalCTA } from "@/components/landing/FinalCTA";
import { Footer } from "@/components/landing/Footer";

export default function LandingPage() {
  return (
    <main className="relative">
      <Navbar />
      <EnhancedHero />
      <EnhancedFeatures />
      <HowItWorks />
      <Pricing />
      <FinalCTA />
      <Footer />
    </main>
  );
}
