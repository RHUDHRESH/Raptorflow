import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { TopNav } from "@/components/nav/TopNav";
import { MobileSheet } from "@/components/nav/MobileSheet";
import { Footer } from "@/components/footer/Footer";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "RaptorFlow - Marketing that actually works",
  description: "Marketing that actually works for founders, small teams, and indie hackers.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <TopNav />
        <main className="min-h-screen">{children}</main>
        <Footer />
      </body>
    </html>
  );
}

