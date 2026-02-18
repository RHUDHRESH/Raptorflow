import type { Metadata } from "next";
import "./globals.css";
import { ScrollProgress } from "@/components/raptor";
import { Toaster } from "@/components/ui/sonner";

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
  themeColor: "#F3F0E7",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
      </head>
      <body className="min-h-screen bg-[#F3F0E7] text-[#2A2529]">
        {/* Subtle scroll progress */}
        <ScrollProgress />
        
        {children}
        
        <Toaster />
      </body>
    </html>
  );
}
