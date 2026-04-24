import type * as React from "react";
import type { Metadata } from "next";
import { ClerkProvider, Show, SignInButton, SignUpButton, UserButton } from "@clerk/nextjs";
import Link from "next/link";
import { DM_Sans, JetBrains_Mono, Instrument_Serif } from "next/font/google";
import { AppProviders } from "@/components/providers/app-providers";
import { RouteProgress } from "@/components/layout/RouteProgress";
import "./globals.css";

const bodyFont = DM_Sans({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  variable: "--font-body",
});

const monoFont = JetBrains_Mono({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  variable: "--font-mono",
});

const displayFont = Instrument_Serif({
  subsets: ["latin"],
  weight: ["400"],
  style: ["normal", "italic"],
  variable: "--font-display",
});

export const metadata: Metadata = {
  title: "RaptorFlow — Your marketing office. Staffed by 21 strategists.",
  description:
    "A team of 21 AI marketing specialists working on your B2B SaaS every single day. Morning briefings. Weekly campaigns. Your product deserves to be found.",
  metadataBase: new URL("https://raptorflow.in"),
  openGraph: {
    title: "RaptorFlow — Your marketing office. Staffed by 21 strategists.",
    description: "Your product deserves to be found. RaptorFlow makes sure it is.",
    url: "https://raptorflow.in",
    siteName: "RaptorFlow",
    images: [{ url: "/og-image.png", width: 1200, height: 630 }],
    locale: "en_IN",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "RaptorFlow — Your marketing office. Staffed by 21 strategists.",
    description: "Your product deserves to be found. RaptorFlow makes sure it is.",
    images: ["/og-image.png"],
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>): React.ReactElement {
  return (
    <html lang="en" className={`${bodyFont.variable} ${monoFont.variable} ${displayFont.variable}`}>
      <body className="font-[family-name:var(--font-body)] text-[var(--foreground)] bg-[var(--background)] antialiased min-h-screen paper-soft">
        <ClerkProvider dynamic signInUrl="/sign-in" signUpUrl="/sign-up">
          <header className="sticky top-0 z-30 border-b border-[var(--border)] bg-[var(--background)]/95 backdrop-blur-sm">
            <div className="mx-auto flex h-16 max-w-[1400px] items-center justify-between gap-4 px-5 md:px-8">
              <Link
                href="/"
                className="font-[family-name:var(--font-display)] text-lg font-bold tracking-[0.18em] text-[var(--ink-900)]"
              >
                RAPTORFLOW
              </Link>
              <div className="flex items-center gap-3">
                <Show when="signed-out">
                  <SignInButton>
                    <button className="btn-secondary text-xs font-mono uppercase tracking-[0.22em]">
                      Sign in
                    </button>
                  </SignInButton>
                  <SignUpButton>
                    <button className="btn-mono">Sign up</button>
                  </SignUpButton>
                </Show>
                <Show when="signed-in">
                  <UserButton />
                </Show>
              </div>
            </div>
          </header>
          <AppProviders>
            <RouteProgress />
            {children}
          </AppProviders>
        </ClerkProvider>
      </body>
    </html>
  );
}
