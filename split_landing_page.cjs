const fs = require('fs');
const path = require('path');

const pagePath = path.join(__dirname, 'src/app/page.tsx');
let content = fs.readFileSync(pagePath, 'utf8');

// Ensure directories exist
const landingHooksDir = path.join(__dirname, 'src/features/landing/hooks');
const landingComponentsDir = path.join(__dirname, 'src/features/landing/components');
if (!fs.existsSync(landingHooksDir)) fs.mkdirSync(landingHooksDir, { recursive: true });
if (!fs.existsSync(landingComponentsDir)) fs.mkdirSync(landingComponentsDir, { recursive: true });

// 1. Extract the GSAP useEffect into useLandingAnimations.ts
const useEffectRegex = /useEffect\(\(\) => \{\n\s*if \(\!containerRef\.current[\s\S]*?return \(\) => ctx\.revert\(\);\n\s*\}, \[isLoaded\]\);/;
const match = content.match(useEffectRegex);
if (match) {
    const hookContent = `import { useEffect } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { MotionPathPlugin } from "gsap/MotionPathPlugin";

if (typeof window !== "undefined") {
  gsap.registerPlugin(ScrollTrigger, MotionPathPlugin);
}

export function useLandingAnimations(containerRef: React.RefObject<HTMLDivElement | null>, isLoaded: boolean) {
  ${match[0]}
}
`;
    fs.writeFileSync(path.join(landingHooksDir, 'useLandingAnimations.ts'), hookContent);
}

// 2. Extract specific sections into components
function extractSection(name, startComment, endComment) {
    const regex = new RegExp(`{/\\* ═══════════════════════════════════════════════════════════════════════\\n\\s*${startComment}[\\s\\S]*?(?={/\\* ════════════════════════|</section>|</div>\\s*</Layout>|$)`, 'i');
    const m = content.match(regex);
    if (m) {
        let sectionCode = m[0];
        // Clean up if it grabbed too much
        if (sectionCode.includes('</section>')) {
            sectionCode = sectionCode.substring(0, sectionCode.indexOf('</section>') + 10);
        }

        // We'll just leave the imports intact in page.tsx for now and replace the body
        return sectionCode;
    }
    return null;
}

const heroSection = extractSection('HeroSection', 'HERO SECTION');
const problemSection = extractSection('ProblemSection', 'PROBLEM SECTION');
const cockpitSection = extractSection('CockpitSection', 'SOLUTION SECTION');
const featuresSection = extractSection('FeaturesSection', 'FEATURES GRID');
// For simplicity, we'll extract the Top Nav and the rest can stay in a wrapper.

// Let's take a simpler approach: Just create LandingClientWrapper and move everything inside the return to it,
// EXCEPT we'll put the page.tsx as a Server Component.
// Wait, to properly fulfill task 2.3, we need separate files.

const sections = [
    { name: 'HeroSection', comment: 'HERO SECTION' },
    { name: 'ProblemSection', comment: 'PROBLEM SECTION' },
    { name: 'CockpitSection', comment: 'SOLUTION SECTION' },
    { name: 'FeaturesSection', comment: 'FEATURES GRID' }
];

let remainingContent = content;

const importsList = `import Link from "next/link";
import {
  ArrowRight, Lock, Zap, Target, Sparkles, BarChart3, Check, ChevronDown, Play, Pause, RotateCcw, Eye, Layers, TrendingUp, Users, Compass, Shield, Clock, GitBranch, MousePointer2
} from "lucide-react";`;

for (const sec of sections) {
    const sectionCode = extractSection(sec.name, sec.comment);
    if (sectionCode) {
        const componentContent = `import React from "react";
${importsList}

export function ${sec.name}() {
  return (
    <>
      ${sectionCode}
    </>
  );
}
`;
        fs.writeFileSync(path.join(landingComponentsDir, `${sec.name}.tsx`), componentContent);
        remainingContent = remainingContent.replace(sectionCode, `<${sec.name} />`);
    }
}

// Also extract the Navigation
const navRegex = /{\/\* ═══════════════════════════════════════════════════════════════════════\n\s*TOP NAVIGATION[\s\S]*?<\/header>/;
const navMatch = remainingContent.match(navRegex);
if (navMatch) {
    const navComponent = `import React from "react";
        import Link from "next/link";
        import { ArrowRight } from "lucide-react";
        import { Logo } from "@/components/brand";

        export function TopNavigation() {
            return (
                ${navMatch[0]}
  );
        }
        `;
    fs.writeFileSync(path.join(landingComponentsDir, 'TopNavigation.tsx'), navComponent);
    remainingContent = remainingContent.replace(navMatch[0], '<TopNavigation />');
}

// 3. Rewrite page.tsx
// Extract the rest of the body into LandingClient
let bodyMatch = remainingContent.match(/return \([\s\S]*?\n\}/);
if (bodyMatch) {
    let bodyStr = bodyMatch[0];

    // Create LandingClient.tsx
    const clientContent = `"use client";
        import React, { useState, useRef, useEffect } from "react";
        import { PageLoader } from "@/components/landing/PageLoader";
        import { FloatingNav } from "@/components/landing/FloatingNav";
        import { useLandingAnimations } from "@/features/landing/hooks/useLandingAnimations";
        import { TopNavigation } from "@/features/landing/components/TopNavigation";
        import { HeroSection } from "@/features/landing/components/HeroSection";
        import { ProblemSection } from "@/features/landing/components/ProblemSection";
        import { CockpitSection } from "@/features/landing/components/CockpitSection";
        import { FeaturesSection } from "@/features/landing/components/FeaturesSection";
${importsList}

        export function LandingClient() {
            const containerRef = useRef < HTMLDivElement > (null);
            const [isLoaded, setIsLoaded] = useState(false);
            const [activeDemo, setActiveDemo] = useState(0);
            const [isPlaying, setIsPlaying] = useState(true);

            useLandingAnimations(containerRef as any, isLoaded);

            useEffect(() => {
                if (!isPlaying) return;
                const interval = setInterval(() => {
                    setActiveDemo((prev) => (prev + 1) % 4);
                }, 4000);
                return () => clearInterval(interval);
            }, [isPlaying]);

  ${bodyStr}
            `;
    fs.writeFileSync(path.join(landingComponentsDir, 'LandingClient.tsx'), clientContent);
}

// Clean up page.tsx to render the client
const newPageTsx = `import { LandingClient } from "@/features/landing/components/LandingClient";

            export default function Page() {
                return <LandingClient />;
            }
            `;
fs.writeFileSync(pagePath, newPageTsx);

console.log("Successfully decomposed page.tsx");
