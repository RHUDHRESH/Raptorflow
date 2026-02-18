"use client";

const sizeMap = {
  xs: 12,
  sm: 14,
  md: 18,
  lg: 24,
  xl: 32,
};

export function Wordmark({ size = "md", className }: { size?: keyof typeof sizeMap; className?: string }) {
  const fontSize = sizeMap[size];
  
  return (
    <span
      className={`font-semibold tracking-tight whitespace-nowrap ${className || ""}`}
      style={{
        fontFamily: "'DM Sans', system-ui, sans-serif",
        fontSize: `${fontSize}px`,
        color: "#3D383C",
        lineHeight: 1,
        letterSpacing: "-0.02em",
      }}
    >
      RaptorFlow
    </span>
  );
}
