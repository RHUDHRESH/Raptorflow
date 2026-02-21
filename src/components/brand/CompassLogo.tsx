"use client";

import { useRef, useEffect, useState, forwardRef, useImperativeHandle } from "react";
import gsap from "gsap";

// ═══════════════════════════════════════════════════════════════════════════════
// RAPTORFLOW LOGO SYSTEM v2.0
// Pale, Refined, Universal
// ═══════════════════════════════════════════════════════════════════════════════

// SOFTER color palette - more pale/refined
const colors = {
  // Primary - softened charcoal
  charcoal: "#3D383C",      // Was #2A2529 - now lighter
  charcoalDark: "#2A2529",  // For contrast when needed
  charcoalLight: "#5C565B", // For secondary elements

  // Pale tones
  paleIvory: "#F7F5EF",     // Was #F3F0E7 - warmer
  paleCream: "#FAF9F6",     // Even lighter for highlights
  paleFog: "#EFEDE6",       // Background blend

  // Accents (muted, not harsh)
  muted: "#9B9599",         // Soft gray
  subtle: "#B8B2A7",        // Warm gray
};

// Size system
const sizeMap = {
  xs: 16,
  sm: 20,
  md: 28,
  lg: 40,
  xl: 56,
  "2xl": 80,
} as const;

type SizeKey = keyof typeof sizeMap;
type LogoState = "static" | "loading" | "hover" | "success" | "pulse";

// ═══════════════════════════════════════════════════════════════════════════════
// ANIMATION CONFIG - Locked Down
// ═══════════════════════════════════════════════════════════════════════════════

const animations = {
  // Entrance - subtle fade up
  entrance: {
    duration: 0.6,
    ease: "power2.out",
    y: 8,
    opacity: 0,
  },

  // Hover - gentle lift and rotate
  hover: {
    duration: 0.35,
    ease: "power2.out",
    rotation: 8,
    y: -3,
    scale: 1.05,
  },

  // Success - checkmark morph
  success: {
    duration: 0.5,
    ease: "back.out(1.7)",
    scale: 1.1,
  },

  // Pulse - breathing effect
  pulse: {
    duration: 2,
    ease: "sine.inOut",
    scale: 1.08,
  },

  // Loading - continuous gentle spin
  loading: {
    duration: 8,
    ease: "none",
    rotation: 360,
  },
};

// ═══════════════════════════════════════════════════════════════════════════════
// MAIN LOGO COMPONENT
// ═══════════════════════════════════════════════════════════════════════════════

export interface CompassLogoProps {
  size?: SizeKey | number;
  showText?: boolean;
  state?: LogoState;
  animate?: boolean;
  className?: string;
  onClick?: () => void;
  mode?: string;
  variant?: string;
  magnetic?: boolean;
}

export interface CompassLogoRef {
  setState: (state: LogoState) => void;
  pulse: () => void;
  success: () => void;
}

export const CompassLogo = forwardRef<CompassLogoRef, CompassLogoProps>(
  function CompassLogo(
    {
      size = "md",
      showText = false,
      state: controlledState,
      animate = true,
      className,
      onClick
    },
    ref
  ) {
    const containerRef = useRef<HTMLDivElement>(null);
    const svgRef = useRef<SVGSVGElement>(null);
    const outerRef = useRef<SVGPathElement>(null);
    const innerRef = useRef<SVGPathElement>(null);
    const centerRef = useRef<SVGCircleElement>(null);

    const [internalState, setInternalState] = useState<LogoState>("static");
    const state = controlledState ?? internalState;
    const pixelSize = typeof size === "number" ? size : sizeMap[size];

    // Expose imperative methods
    useImperativeHandle(ref, () => ({
      setState: setInternalState,
      pulse: () => {
        setInternalState("pulse");
        setTimeout(() => setInternalState("static"), 2000);
      },
      success: () => {
        setInternalState("success");
        setTimeout(() => setInternalState("static"), 1500);
      },
    }));

    // ═══════════════════════════════════════════════════════════════════════════
    // ANIMATION EFFECTS
    // ═══════════════════════════════════════════════════════════════════════════

    // Entrance animation
    useEffect(() => {
      if (!animate || !svgRef.current) return;

      const ctx = gsap.context(() => {
        gsap.fromTo(svgRef.current,
          {
            opacity: animations.entrance.opacity,
            y: animations.entrance.y
          },
          {
            opacity: 1,
            y: 0,
            duration: animations.entrance.duration,
            ease: animations.entrance.ease,
          }
        );
      });

      return () => ctx.revert();
    }, [animate]);

    // Hover animations
    useEffect(() => {
      if (!animate || !containerRef.current || !svgRef.current) return;

      const container = containerRef.current;
      const svg = svgRef.current;

      const handleEnter = () => {
        if (state === "loading") return;

        gsap.to(svg, {
          rotation: animations.hover.rotation,
          y: animations.hover.y,
          scale: animations.hover.scale,
          duration: animations.hover.duration,
          ease: animations.hover.ease,
          transformOrigin: "center center",
        });

        // Subtle color shift on inner
        if (innerRef.current) {
          gsap.to(innerRef.current, {
            fill: colors.paleCream,
            duration: 0.3,
          });
        }
      };

      const handleLeave = () => {
        if (state === "loading") return;

        gsap.to(svg, {
          rotation: 0,
          y: 0,
          scale: 1,
          duration: animations.hover.duration,
          ease: animations.hover.ease,
          transformOrigin: "center center",
        });

        if (innerRef.current) {
          gsap.to(innerRef.current, {
            fill: colors.paleIvory,
            duration: 0.3,
          });
        }
      };

      container.addEventListener("mouseenter", handleEnter);
      container.addEventListener("mouseleave", handleLeave);

      return () => {
        container.removeEventListener("mouseenter", handleEnter);
        container.removeEventListener("mouseleave", handleLeave);
      };
    }, [animate, state]);

    // Loading animation
    useEffect(() => {
      if (!svgRef.current) return;

      if (state === "loading") {
        gsap.to(svgRef.current, {
          rotation: animations.loading.rotation,
          duration: animations.loading.duration,
          ease: animations.loading.ease,
          repeat: -1,
          transformOrigin: "center center",
        });
      } else {
        gsap.killTweensOf(svgRef.current, "rotation");
        gsap.to(svgRef.current, {
          rotation: 0,
          duration: 0.5,
          ease: "power2.out",
        });
      }
    }, [state]);

    // Pulse animation
    useEffect(() => {
      if (!svgRef.current || state !== "pulse") return;

      const tl = gsap.timeline({
        onComplete: () => setInternalState("static"),
      });

      tl.to(svgRef.current, {
        scale: animations.pulse.scale,
        duration: animations.pulse.duration / 2,
        ease: animations.pulse.ease,
        yoyo: true,
        repeat: 1,
        transformOrigin: "center center",
      });

      return () => { tl.kill(); };
    }, [state]);

    // Success animation
    useEffect(() => {
      if (!svgRef.current || state !== "success") return;

      const tl = gsap.timeline({
        onComplete: () => setInternalState("static"),
      });

      tl.to(svgRef.current, {
        scale: animations.success.scale,
        duration: animations.success.duration / 2,
        ease: animations.success.ease,
        yoyo: true,
        repeat: 1,
        transformOrigin: "center center",
      });

      return () => { tl.kill(); };
    }, [state]);

    // ═══════════════════════════════════════════════════════════════════════════
    // RENDER
    // ═══════════════════════════════════════════════════════════════════════════

    const isInteractive = animate && !onClick;

    return (
      <div
        ref={containerRef}
        className={`inline-flex items-center select-none ${className || ""} ${onClick ? "cursor-pointer" : isInteractive ? "cursor-default" : ""
          }`}
        style={{
          gap: showText ? pixelSize * 0.4 : 0,
        }}
        onClick={onClick}
      >
        {/* SVG Logo */}
        <svg
          ref={svgRef}
          width={pixelSize}
          height={pixelSize}
          viewBox="0 0 24 24"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          className="block will-change-transform"
          style={{
            filter: state === "hover"
              ? "drop-shadow(0 2px 4px rgba(42, 37, 41, 0.08))"
              : "none",
            transition: "filter 0.3s ease",
          }}
        >
          {/* Top triangle — north / primary */}
          <path
            ref={outerRef}
            d="M12 2L18.5 13H5.5L12 2Z"
            fill={colors.charcoal}
            style={{ transition: "fill 0.3s ease" }}
          />

          {/* Bottom triangle — south / secondary */}
          <path
            ref={innerRef}
            d="M12 22L18.5 13H5.5L12 22Z"
            fill={colors.charcoalLight}
            opacity="0.5"
            style={{ transition: "fill 0.3s ease, opacity 0.3s ease" }}
          />

          {/* Center dot at intersection */}
          <circle
            ref={centerRef}
            cx="12"
            cy="13"
            r="1.8"
            fill={colors.paleIvory}
          />
        </svg>

        {/* Text wordmark */}
        {showText && (
          <span
            className="font-semibold tracking-tight whitespace-nowrap"
            style={{
              fontFamily: "'DM Sans', system-ui, sans-serif",
              fontSize: `${pixelSize * 0.7}px`,
              color: colors.charcoal,
              lineHeight: 1,
              letterSpacing: "-0.02em",
            }}
          >
            RaptorFlow
          </span>
        )}
      </div>
    );
  }
);

// ═══════════════════════════════════════════════════════════════════════════════
// LOTTIE LOGO COMPONENT - For animated logo states
// ═══════════════════════════════════════════════════════════════════════════════

interface LottieLogoProps {
  size?: SizeKey;
  showText?: boolean;
  autoplay?: boolean;
  loop?: boolean;
  className?: string;
}

export function LottieLogo({
  size = "md",
  showText = false,
  autoplay = true,
  loop = true,
  className,
}: LottieLogoProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [isLoaded, setIsLoaded] = useState(false);
  const [hasError, setHasError] = useState(false);
  const pixelSize = sizeMap[size];

  useEffect(() => {
    let animationInstance: any = null;

    const loadLottie = async () => {
      try {
        let lottie: any;
        try {
          // Optional dependency: avoid hard bundler resolution when not installed.
          const dynamicImport = new Function(
            "specifier",
            "return import(specifier)"
          ) as (specifier: string) => Promise<{ default?: any }>;
          const mod = await dynamicImport("lottie-web");
          lottie = mod.default;
        } catch {
          // lottie-web not installed, fallback to static
          setHasError(true);
          return;
        }

        if (containerRef.current && lottie) {
          animationInstance = lottie.loadAnimation({
            container: containerRef.current,
            renderer: "svg",
            loop,
            autoplay,
            path: "/lottie/compass-pointer.json",
          });

          animationInstance.addEventListener("DOMLoaded", () => {
            setIsLoaded(true);
            gsap.fromTo(containerRef.current,
              { opacity: 0, scale: 0.9 },
              { opacity: 1, scale: 1, duration: 0.5, ease: "power2.out" }
            );
          });

          animationInstance.addEventListener("error", () => {
            setHasError(true);
          });
        }
      } catch (error) {
        console.warn("Lottie animation failed to load:", error);
        setHasError(true);
      }
    };

    loadLottie();

    return () => {
      if (animationInstance) {
        animationInstance.destroy();
      }
    };
  }, [autoplay, loop]);

  // Fallback to static logo if Lottie fails
  if (hasError) {
    return <CompassLogo size={size} showText={showText} state="pulse" className={className} />;
  }

  return (
    <div
      className={`inline-flex items-center ${className || ""}`}
      style={{ gap: showText ? pixelSize * 0.4 : 0 }}
    >
      <div
        ref={containerRef}
        style={{
          width: pixelSize,
          height: pixelSize,
          opacity: isLoaded ? 1 : 0,
          transition: "opacity 0.3s ease",
        }}
      />

      {!isLoaded && !hasError && (
        <CompassIcon size={size} animate />
      )}

      {showText && (
        <span
          className="font-semibold tracking-tight whitespace-nowrap"
          style={{
            fontFamily: "'DM Sans', system-ui, sans-serif",
            fontSize: `${pixelSize * 0.7}px`,
            color: colors.charcoal,
            lineHeight: 1,
            letterSpacing: "-0.02em",
          }}
        >
          RaptorFlow
        </span>
      )}
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════════════════
// STANDALONE ICON - For small spaces
// ═══════════════════════════════════════════════════════════════════════════════

interface CompassIconProps {
  size?: SizeKey;
  className?: string;
  animate?: boolean;
}

export function CompassIcon({ size = "md", className, animate = false }: CompassIconProps) {
  const svgRef = useRef<SVGSVGElement>(null);
  const pixelSize = sizeMap[size];

  useEffect(() => {
    if (!animate || !svgRef.current) return;

    const ctx = gsap.context(() => {
      gsap.to(svgRef.current, {
        rotation: 360,
        duration: 20,
        ease: "none",
        repeat: -1,
        transformOrigin: "center center",
      });
    });

    return () => ctx.revert();
  }, [animate]);

  return (
    <svg
      ref={svgRef}
      width={pixelSize}
      height={pixelSize}
      viewBox="0 0 24 24"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={`block ${className || ""}`}
    >
      {/* Top triangle */}
      <path
        d="M12 2L18.5 13H5.5L12 2Z"
        fill={colors.charcoal}
      />
      {/* Bottom triangle */}
      <path
        d="M12 22L18.5 13H5.5L12 22Z"
        fill={colors.charcoalLight}
        opacity="0.5"
      />
      {/* Center dot */}
      <circle
        cx="12"
        cy="13"
        r="1.8"
        fill={colors.paleIvory}
      />
    </svg>
  );
}

// ═══════════════════════════════════════════════════════════════════════════════
// LOADING SPINNER - Logo as loading indicator
// ═══════════════════════════════════════════════════════════════════════════════

interface LogoSpinnerProps {
  size?: SizeKey;
  text?: string;
  className?: string;
}

export function LogoSpinner({ size = "lg", text, className }: LogoSpinnerProps) {
  return (
    <div className={`flex flex-col items-center justify-center ${className || ""}`}>
      <CompassIcon size={size} animate />
      {text && (
        <span
          className="mt-3 text-sm"
          style={{
            fontFamily: "'DM Sans', system-ui, sans-serif",
            color: colors.charcoalLight,
          }}
        >
          {text}
        </span>
      )}
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════════════════
// SEAL / LOCK ICON - For locked states
// ═══════════════════════════════════════════════════════════════════════════════

interface LockSealProps {
  size?: SizeKey;
  locked?: boolean;
  className?: string;
}

export function LockSeal({ size = "sm", locked = true, className }: LockSealProps) {
  const sealRef = useRef<HTMLDivElement>(null);
  const pixelSize = sizeMap[size];

  useEffect(() => {
    if (!sealRef.current) return;

    gsap.fromTo(sealRef.current,
      { scale: 0, rotation: -180 },
      {
        scale: 1,
        rotation: 0,
        duration: 0.5,
        ease: "back.out(1.7)",
      }
    );
  }, [locked]);

  return (
    <div
      ref={sealRef}
      className={`inline-flex items-center justify-center rounded-full ${className || ""}`}
      style={{
        width: pixelSize,
        height: pixelSize,
        backgroundColor: locked ? colors.charcoal : "transparent",
        border: `1.5px solid ${locked ? colors.charcoal : colors.muted}`,
      }}
    >
      <svg
        width={pixelSize * 0.5}
        height={pixelSize * 0.5}
        viewBox="0 0 24 24"
        fill="none"
        stroke={locked ? colors.paleIvory : colors.muted}
        strokeWidth="2.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      >
        {locked ? (
          <>
            <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
            <path d="M7 11V7a5 5 0 0 1 10 0v4" />
          </>
        ) : (
          <>
            <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
            <path d="M7 11V7a5 5 0 0 1 9.9-1" />
          </>
        )}
      </svg>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════════════════
// EXPORTS
// ═══════════════════════════════════════════════════════════════════════════════

export { colors as logoColors, sizeMap as logoSizes };
export type { LogoState, SizeKey };
export default CompassLogo;
