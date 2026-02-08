import type { Metadata } from "next";
import "./globals.css";
import { CustomCursor } from "@/components/effects/CustomCursor";
import { GrainEffect } from "@/components/effects/GrainEffect";
import { SmoothScrollProvider } from "@/components/effects/SmoothScroll";
import { Toaster } from "@/components/ui/sonner";

export const metadata: Metadata = {
  title: "RaptorFlow - Navigate Your Marketing",
  description: "The artisanal marketing operating system for founders who demand precision. AI-powered strategy, content, and campaign execution.",
  keywords: ["marketing", "AI", "founders", "SaaS", "strategy", "content generation"],
  authors: [{ name: "RaptorFlow" }],
  openGraph: {
    title: "RaptorFlow - Navigate Your Marketing",
    description: "The artisanal marketing operating system for founders who demand precision.",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <link rel="icon" type="image/svg+xml" href="/compass/compass-favicon.svg" />
      </head>
      <body className="min-h-screen">
        <SmoothScrollProvider>
          {/* Custom cursor for desktop */}
          <CustomCursor />

          {/* Animated grain overlay */}
          <GrainEffect />

          {/* Static grain overlay fallback */}
          <div className="grain-overlay" aria-hidden="true" />

          {children}
        </SmoothScrollProvider>
        <Toaster />
      </body>
    </html>
  );
}
