import { HeroHeader } from "@/components/hero/HeroHeader";
import { ValueTrio } from "@/components/trio/ValueTrio";
import { PersonaGrid } from "@/components/icp/PersonaGrid";
import { PlanLikeAPro } from "@/components/plan/PlanLikeAPro";
import { IdeaEngine } from "@/components/ideas/IdeaEngine";
import { AssetFactory } from "@/components/assets/AssetFactory";
import { PricingTable } from "@/components/pricing/PricingTable";
import { BottomCTA } from "@/components/cta/BottomCTA";

export default function Home() {
  return (
    <>
      <HeroHeader />
      <ValueTrio />
      <PersonaGrid />
      <PlanLikeAPro />
      <IdeaEngine />
      <AssetFactory />
      <PricingTable />
      <BottomCTA />
    </>
  );
}

