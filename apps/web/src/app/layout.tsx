import type * as React from "react";
import type { Metadata } from "next";
import { ClerkProvider } from "@clerk/nextjs";
import { Plus_Jakarta_Sans, DM_Mono } from "next/font/google";
import { AppProviders } from "@/components/providers/app-providers";
import "./globals.css";

const bodyFont = Plus_Jakarta_Sans({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700", "800"],
  variable: "--font-body",
});

const monoFont = DM_Mono({
  subsets: ["latin"],
  weight: ["400", "500"],
  variable: "--font-mono",
});

export const metadata: Metadata = {
  title: "RaptorFlow — AI Marketing for B2B SaaS Founders",
  description:
    "A team of 21 AI marketing specialists working on your B2B SaaS every single day. Morning briefings. Weekly campaigns. Your product deserves to be found.",
  metadataBase: new URL("https://raptorflow.in"),
  openGraph: {
    title: "RaptorFlow — AI Marketing for B2B SaaS Founders",
    description: "Your product deserves to be found. RaptorFlow makes sure it is.",
    url: "https://raptorflow.in",
    siteName: "RaptorFlow",
    images: [{ url: "/og-image.png", width: 1200, height: 630 }],
    locale: "en_IN",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "RaptorFlow — AI Marketing for B2B SaaS Founders",
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
    <ClerkProvider
      dynamic
      signInUrl="/sign-in"
      signUpUrl="/sign-up"
      afterSignInUrl="/app"
      afterSignUpUrl="/create-workspace"
    >
      <html lang="en" className={`${bodyFont.variable} ${monoFont.variable}`}>
        <body className="font-[family-name:var(--font-body)] text-[#13141A] bg-[#F7F4EE] antialiased min-h-screen">
          <AppProviders>{children}</AppProviders>
        </body>
      </html>
    </ClerkProvider>
  );
}
