"use client";

// ═══════════════════════════════════════════════════════════════════════════════
// FAVICON SYSTEM — Universal favicon propagation
// All sizes and formats for maximum compatibility
// ═══════════════════════════════════════════════════════════════════════════════

import { useEffect } from "react";

/**
 * SVG Logo for favicon generation
 * Clean, minimal version that works at 16x16
 */
export const FaviconSVG = `
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
  <path d="M12 2L18.5 13H5.5L12 2Z" fill="#2A2529"/>
  <path d="M12 22L18.5 13H5.5L12 22Z" fill="#5C565B" opacity="0.5"/>
  <circle cx="12" cy="13" r="1.8" fill="#F3F0E7"/>
</svg>
`;

/**
 * Dark mode favicon
 */
export const FaviconSVGDark = `
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
  <path d="M12 2L18.5 13H5.5L12 2Z" fill="#F3F0E7"/>
  <path d="M12 22L18.5 13H5.5L12 22Z" fill="#F3F0E7" opacity="0.45"/>
  <circle cx="12" cy="13" r="1.8" fill="#2A2529"/>
</svg>
`;

/**
 * Minimal favicon for smallest sizes
 */
export const FaviconSVGMinimal = `
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
  <path d="M12 2L18.5 13H5.5L12 2Z" fill="#2A2529"/>
  <path d="M12 22L18.5 13H5.5L12 22Z" fill="#2A2529" opacity="0.4"/>
</svg>
`;

/**
 * Generate data URL from SVG
 */
function svgToDataUrl(svg: string): string {
  const encoded = encodeURIComponent(svg);
  return `data:image/svg+xml,${encoded}`;
}

/**
 * Favicon component - injects all favicon variants into document head
 */
export function Favicons() {
  useEffect(() => {
    // Generate data URLs
    const favicon16 = svgToDataUrl(FaviconSVGMinimal);
    const favicon32 = svgToDataUrl(FaviconSVG);
    const faviconDark = svgToDataUrl(FaviconSVGDark);

    // Create or update favicon links
    const updateFavicon = (rel: string, size: string, href: string, media?: string) => {
      let link = document.querySelector(`link[rel="${rel}"][sizes="${size}"]`) as HTMLLinkElement;
      if (!link) {
        link = document.createElement("link");
        link.rel = rel;
        link.setAttribute("sizes", size);
        if (media) link.media = media;
        document.head.appendChild(link);
      }
      link.href = href;
    };

    // Standard favicons
    updateFavicon("icon", "16x16", favicon16);
    updateFavicon("icon", "32x32", favicon32);
    updateFavicon("shortcut icon", "32x32", favicon32);

    // Apple Touch Icon (with padding for iOS)
    const appleIcon = `
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 180 180">
        <rect width="180" height="180" fill="#F3F0E7" rx="40"/>
        <g transform="translate(45, 30) scale(3.75)">
          <path d="M12 2L18.5 13H5.5L12 2Z" fill="#2A2529"/>
          <path d="M12 22L18.5 13H5.5L12 22Z" fill="#5C565B" opacity="0.5"/>
          <circle cx="12" cy="13" r="1.8" fill="#F3F0E7"/>
        </g>
      </svg>
    `;
    updateFavicon("apple-touch-icon", "180x180", svgToDataUrl(appleIcon));

    // Safari Pinned Tab (monochrome)
    const safariIcon = `
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
        <path d="M12 2L18.5 13H5.5L12 2Z" fill="#2A2529"/>
        <path d="M12 22L18.5 13H5.5L12 22Z" fill="#2A2529" opacity="0.4"/>
      </svg>
    `;
    let maskIcon = document.querySelector('link[rel="mask-icon"]') as HTMLLinkElement;
    if (!maskIcon) {
      maskIcon = document.createElement("link");
      maskIcon.rel = "mask-icon";
      maskIcon.setAttribute("color", "#2A2529");
      document.head.appendChild(maskIcon);
    }
    maskIcon.href = svgToDataUrl(safariIcon);

    // MS Tile (for Windows)
    let msTile = document.querySelector('meta[name="msapplication-TileImage"]') as HTMLMetaElement;
    if (!msTile) {
      msTile = document.createElement("meta");
      msTile.name = "msapplication-TileImage";
      document.head.appendChild(msTile);
    }
    msTile.content = svgToDataUrl(appleIcon);

    let msColor = document.querySelector('meta[name="msapplication-TileColor"]') as HTMLMetaElement;
    if (!msColor) {
      msColor = document.createElement("meta");
      msColor.name = "msapplication-TileColor";
      document.head.appendChild(msColor);
    }
    msColor.content = "#F3F0E7";

    // Theme color for mobile browsers
    let themeColor = document.querySelector('meta[name="theme-color"]') as HTMLMetaElement;
    if (!themeColor) {
      themeColor = document.createElement("meta");
      themeColor.name = "theme-color";
      document.head.appendChild(themeColor);
    }
    themeColor.content = "#F3F0E7";

    // Dark mode theme color
    let themeColorDark = document.querySelector('meta[name="theme-color"][media="(prefers-color-scheme: dark)"]') as HTMLMetaElement;
    if (!themeColorDark) {
      themeColorDark = document.createElement("meta");
      themeColorDark.name = "theme-color";
      themeColorDark.media = "(prefers-color-scheme: dark)";
      document.head.appendChild(themeColorDark);
    }
    themeColorDark.content = "#2A2529";

    // Cleanup
    return () => {
      // Favicons persist across navigation, don't remove
    };
  }, []);

  return null; // This component doesn't render anything
}

/**
 * Generate PNG favicon at specific size
 * Returns a canvas data URL
 */
export function generateFaviconPNG(size: number, dark = false): string {
  const canvas = document.createElement("canvas");
  canvas.width = size;
  canvas.height = size;
  const ctx = canvas.getContext("2d");

  if (!ctx) return "";

  // Background
  ctx.fillStyle = dark ? "#2A2529" : "#F3F0E7";
  ctx.fillRect(0, 0, size, size);

  // Scale factor
  const s = size / 24;

  // Top triangle
  ctx.fillStyle = dark ? "#F3F0E7" : "#2A2529";
  ctx.beginPath();
  ctx.moveTo(12 * s, 2 * s);
  ctx.lineTo(18.5 * s, 13 * s);
  ctx.lineTo(5.5 * s, 13 * s);
  ctx.closePath();
  ctx.fill();

  // Bottom triangle (lighter)
  ctx.globalAlpha = 0.5;
  ctx.fillStyle = dark ? "#F3F0E7" : "#5C565B";
  ctx.beginPath();
  ctx.moveTo(12 * s, 22 * s);
  ctx.lineTo(18.5 * s, 13 * s);
  ctx.lineTo(5.5 * s, 13 * s);
  ctx.closePath();
  ctx.fill();
  ctx.globalAlpha = 1;

  // Center dot
  ctx.fillStyle = dark ? "#2A2529" : "#F3F0E7";
  ctx.beginPath();
  ctx.arc(12 * s, 13 * s, 1.8 * s, 0, Math.PI * 2);
  ctx.fill();

  return canvas.toDataURL("image/png");
}

export default Favicons;
