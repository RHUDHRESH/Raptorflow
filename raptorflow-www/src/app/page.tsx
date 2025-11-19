// Root page - show marketing site
import { LiquidMetalBackground } from "@/components/liquid-metal-background/LiquidMetalBackground";
import { FloatingNavbar } from "@/components/floating-navbar/FloatingNavbar";
import { HeroHeader } from "@/components/hero/HeroHeader";
import { ValueTrio } from "@/components/trio/ValueTrio";
import { PersonaGrid } from "@/components/icp/PersonaGrid";
import { PlanLikeAPro } from "@/components/plan/PlanLikeAPro";
import { IdeaEngine } from "@/components/ideas/IdeaEngine";
import { AssetFactory } from "@/components/assets/AssetFactory";
import { HowItWorks } from "@/components/how-it-works/HowItWorks";
import { PricingTable } from "@/components/pricing/PricingTable";
import { Testimonial } from "@/components/testimonial/Testimonial";
import { BottomCTA } from "@/components/cta/BottomCTA";
import { Footer } from "@/components/footer/Footer";
import { cn } from "@/lib/utils";

export default function Home() {
  return (
    <main className="relative min-h-screen">
      <LiquidMetalBackground />
      
      {/* Dark opacity overlay */}
      <div className="fixed inset-0 z-[5] bg-black/50" />
      
      {/* Dots pattern overlay */}
      <div
        aria-hidden="true"
        className={cn(
          "fixed inset-0 z-[6] size-full pointer-events-none",
          "bg-[radial-gradient(rgba(255,255,255,0.1)_1px,transparent_1px)]",
          "bg-[size:12px_12px]",
          "opacity-30",
        )}
      />
      
      <FloatingNavbar />
      
      {/* Hero Section */}
      <div className="relative z-10">
        <HeroHeader />
      </div>
      
      {/* Rest of sections */}
      <div className="relative z-10">
        <ValueTrio />
        <PersonaGrid />
        <PlanLikeAPro />
        <IdeaEngine />
        <AssetFactory />
        <HowItWorks />
        <PricingTable />
        <Testimonial />
        <BottomCTA />
        <Footer />
      </div>
    </main>
  );
}
