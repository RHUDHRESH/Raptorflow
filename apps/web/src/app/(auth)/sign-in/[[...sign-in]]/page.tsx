import type * as React from "react";
import { SignIn } from "@clerk/nextjs";

export default function SignInPage(): React.ReactElement {
  return (
    <SignIn 
      appearance={{
        elements: {
          rootBox: "w-full",
          card: "bg-[var(--card)] shadow-none border border-[var(--border)] rounded-none p-4",
          headerTitle: "font-[family-name:var(--font-display)] text-2xl text-[var(--foreground)]",
          headerSubtitle: "font-body text-[var(--muted-foreground)]",
          formButtonPrimary: "bg-[var(--primary)] text-[var(--primary-foreground)] hover:opacity-90 rounded-none h-12 uppercase tracking-wider text-xs font-mono border border-[var(--primary)]",
          formFieldInput: "bg-[var(--background)] border border-[var(--border)] rounded-none h-12 px-4 focus:ring-1 focus:ring-[var(--primary)]",
          formFieldLabel: "font-mono uppercase tracking-widest text-[10px] text-[var(--muted-foreground)] mb-1",
          footerActionLink: "text-[var(--primary)] hover:text-[var(--primary)]/80 font-bold",
          socialButtonsBlockButton: "border border-[var(--border)] rounded-none h-12 hover:bg-[var(--accent)]",
          dividerLine: "bg-[var(--border)]",
          dividerText: "text-[var(--muted-foreground)] font-mono uppercase text-[10px]",
        }
      }}
    />
  );
}
