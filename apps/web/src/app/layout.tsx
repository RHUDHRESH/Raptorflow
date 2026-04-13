import type * as React from "react";
import type { Metadata } from "next";
import { ClerkProvider } from "@clerk/nextjs";
import { IBM_Plex_Sans, Space_Grotesk } from "next/font/google";
import { AppProviders } from "@/components/providers/app-providers";
import "./globals.css";

const bodyFont = IBM_Plex_Sans({
  subsets: ["latin"],
  variable: "--font-body",
});

const displayFont = Space_Grotesk({
  subsets: ["latin"],
  variable: "--font-display",
});
const clerkPublishableKey = process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY;
if (!clerkPublishableKey) {
  throw new Error(
    "NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY is not set. Copy apps/web/.env.example to apps/web/.env.local and fill in your Clerk publishable key.",
  );
}

export const metadata: Metadata = {
  title: "RaptorFlow",
  description: "Production scaffold for the living marketing office.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>): React.ReactElement {
  return (
    <ClerkProvider publishableKey={clerkPublishableKey}>
      <html lang="en">
        <body className={`${bodyFont.variable} ${displayFont.variable}`}>
          <AppProviders>{children}</AppProviders>
        </body>
      </html>
    </ClerkProvider>
  );
}
