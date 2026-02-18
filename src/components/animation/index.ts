// Animation Components
export { PageTransition } from "./PageTransition";
export { RevealOnScroll } from "./RevealOnScroll";
export { StaggerContainer } from "./StaggerContainer";

// Legacy animation components (kept for backward compatibility)
export { 
  AnimatedPage, 
  AnimatedCard, 
  AnimatedList, 
  FadeInView 
} from "./AnimatedPage";

// Re-export hooks from provider for convenience
export { useAnimation } from "@/components/providers/AnimationProvider";
