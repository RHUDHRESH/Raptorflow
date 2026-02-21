import type { Metadata } from "next";
import { DM_Sans, JetBrains_Mono } from "next/font/google";
import "./globals.css";
import { ScrollProgress } from "@/components/raptor";
import { Toaster } from "@/components/ui/sonner";

const dmSans = DM_Sans({ subsets: ["latin"], display: "swap" });
const jetBrainsMono = JetBrains_Mono({ subsets: ["latin"], display: "swap", variable: "--font-mono" });

export const metadata: Metadata = {
  title: "RaptorFlow — Navigate Your Marketing",
  description: "The marketing operating system for founders who demand precision. Build truth. Lock strategy. Execute with clarity.",
  keywords: ["marketing", "strategy", "founders", "SaaS", "OS", "navigation"],
  authors: [{ name: "RaptorFlow" }],
  icons: {
    icon: [
      { url: "/favicon-16x16.png", sizes: "16x16", type: "image/png" },
      { url: "/favicon-32x32.png", sizes: "32x32", type: "image/png" },
    ],
    apple: { url: "/apple-touch-icon.png", sizes: "180x180" },
  },
  manifest: "/site.webmanifest",
  themeColor: "#EFEDE6",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning className={`${dmSans.className} ${jetBrainsMono.variable}`}>
      <head>
      </head>
      <body className="min-h-screen bg-[var(--bg-canvas)] text-[var(--ink-1)]">
        {/* Subtle scroll progress */}
        <ScrollProgress />

        {children}

        <Toaster />
      </body>
    </html>
  );
}
