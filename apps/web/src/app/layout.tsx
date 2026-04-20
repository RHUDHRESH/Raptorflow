import type * as React from "react";
import type { Metadata } from "next";
import { ClerkProvider } from "@clerk/nextjs";
import { DM_Sans, Instrument_Serif, JetBrains_Mono } from "next/font/google";
import { AppProviders } from "@/components/providers/app-providers";
import "./globals.css";

const bodyFont = DM_Sans({
  subsets: ["latin"],
  variable: "--font-body",
});

const displayFont = Instrument_Serif({
  subsets: ["latin"],
  weight: ["400"],
  variable: "--font-display",
});

const monoFont = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-mono",
});

export const metadata: Metadata = {
  title: "RaptorFlow — A Marketing Firm of Record",
  description: "Stop managing a tool. Start managing a team. 21 AI Strategists.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>): React.ReactElement {
  return (
    <ClerkProvider
      dynamic
      signInUrl="/sign-in"
      signUpUrl="/sign-up"
      afterSignInUrl="/app"
      afterSignUpUrl="/create-workspace"
    >
      <html
        lang="en"
        className={`${bodyFont.variable} ${displayFont.variable} ${monoFont.variable}`}
      >
        <body className="font-body text-[var(--foreground)] bg-[var(--background)] antialiased min-h-screen">
          <AppProviders>{children}</AppProviders>
        </body>
      </html>
    </ClerkProvider>
  );
}
