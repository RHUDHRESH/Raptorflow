"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";
import { LandingNavbar } from "@/features/landing/components/LandingNavbar";
import { FooterSection } from "@/features/landing/components/FooterSection";
import { communicationsService } from "@/services/communications.service";

export default function ContactPage() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [subject, setSubject] = useState("General inquiry");
  const [message, setMessage] = useState("");
  const [isSending, setIsSending] = useState(false);
  const [result, setResult] = useState<string>("");

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    if (!name.trim() || !email.trim() || !message.trim()) {
      setResult("Please complete all required fields.");
      return;
    }

    setIsSending(true);
    setResult("");
    try {
      const response = await communicationsService.sendContact({
        name: name.trim(),
        email: email.trim(),
        subject: subject.trim() || "General inquiry",
        message: message.trim(),
        source: "contact-page",
      });
      if (response.accepted) {
        setResult("Message sent. We will respond soon.");
        setMessage("");
      } else {
        setResult("Message was received, but delivery is partial.");
      }
    } catch (error: any) {
      setResult(error?.message || "Failed to send message.");
    } finally {
      setIsSending(false);
    }
  }

  return (
    <main className="relative min-h-screen bg-[var(--bg-canvas)]">
      <LandingNavbar />
      <div className="pt-24">
        <div className="max-w-3xl mx-auto px-6 py-16 space-y-8">
          <header className="space-y-3">
            <h1 className="text-[40px] leading-[48px] font-bold tracking-[-0.02em] text-[var(--ink-1)]">
              Contact
            </h1>
            <p className="text-[var(--ink-2)]">
              Have a question or need support? Reach out and we&apos;ll get back
              to you.
            </p>
          </header>

          <section className="rounded-[var(--radius-lg)] border border-[var(--border-1)] bg-[var(--bg-surface)] p-6 space-y-4">
            <form onSubmit={onSubmit} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <input
                  className="rf-input"
                  placeholder="Your name"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  maxLength={120}
                  required
                />
                <input
                  className="rf-input"
                  placeholder="you@company.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  type="email"
                  required
                />
              </div>
              <input
                className="rf-input"
                placeholder="Subject"
                value={subject}
                onChange={(e) => setSubject(e.target.value)}
                maxLength={160}
                required
              />
              <textarea
                className="rf-textarea"
                placeholder="How can we help?"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                maxLength={5000}
                required
              />
              <div className="flex items-center gap-3">
                <button
                  type="submit"
                  disabled={isSending}
                  className="rf-btn rf-btn-primary"
                >
                  {isSending ? "Sending..." : "Send Message"}
                </button>
                {result ? (
                  <p className="text-sm text-[var(--ink-2)]">{result}</p>
                ) : null}
              </div>
            </form>

            <div className="space-y-1 pt-4 border-t border-[var(--border-1)]">
              <h2 className="text-xl font-semibold text-[var(--ink-1)]">
                Open The App
              </h2>
              <p className="text-sm text-[var(--ink-2)]">
                Go to{" "}
                <Link
                  className="text-[var(--ink-1)] underline hover:no-underline"
                  href="/dashboard"
                >
                  /dashboard
                </Link>
              </p>
            </div>
          </section>
        </div>

        <FooterSection />
      </div>
    </main>
  );
}
