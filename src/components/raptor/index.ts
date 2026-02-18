// ═══════════════════════════════════════════════════════════════════════════════
// RAPTORFLOW UI SYSTEM v1.0
// Charcoal / Ivory Design System
// Minimal, Light, Bold, Subtle
// ═══════════════════════════════════════════════════════════════════════════════

// Shell Components
export { Layout } from "./shell/Layout";
export { Sidebar } from "./shell/Sidebar";
export { TopBar } from "./shell/TopBar";
export { RightDrawer } from "./shell/RightDrawer";

// UI Components
export { Button } from "./ui/Button";
export { Card, CardHeader, CardFooter } from "./ui/Card";
export { Input } from "./ui/Input";
export { Badge } from "./ui/Badge";
export { Tag } from "./ui/Tag";
export { Modal, ConfirmDialog } from "./ui/Modal";
export { Tabs } from "./ui/Tabs";
export { Progress } from "./ui/Progress";
export { ScrollProgress } from "./ui/ScrollProgress";
export { Table } from "./ui/Table";

// Animation Components
export { LottieOrigami, LoadingOrigami, EmptyStateOrigami } from "./animations/LottieOrigami";

// Brand / Logo
export { 
  CompassLogo,
  LottieLogo,
  CompassIcon,
  LogoSpinner,
  LockSeal,
  logoColors,
  logoSizes
} from "@/components/brand";

export type { CompassLogoRef, LogoState, SizeKey } from "@/components/brand";

// GSAP Utilities - Sophisticated but subtle
export {
  // Text reveals
  revealTextByLines,
  revealTextByWords,
  revealTextByChars,
  blurReveal,
  
  // Scroll reveals
  fadeUpOnScroll,
  staggerChildren,
  slideIn,
  
  // Parallax & depth
  subtleParallax,
  scaleOnScroll,
  
  // SVG
  drawPath,
  revealSVG,
  
  // Micro-interactions
  magneticButton,
  underlineDraw,
  animateCounter,
  
  // Page transitions
  pageEntrance,
  smoothScrollTo,
  
  // Cleanup
  killAllAnimations,
  cleanupScrollTriggers,
} from "@/lib/gsap/animations";
