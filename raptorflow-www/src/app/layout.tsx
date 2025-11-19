import type { Metadata } from "next";
import "./globals.css";
import { Footer } from "@/components/footer/Footer";

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
      <body className="font-sans">
        {children}
      </body>
    </html>
  );
}

