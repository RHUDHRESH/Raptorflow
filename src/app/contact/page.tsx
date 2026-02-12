"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";
import { Navbar } from "@/components/landing/Navbar";
import { Footer } from "@/components/landing/Footer";
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
    <main className="relative">
      <Navbar />
      <div className="pt-24 bg-[var(--bg-primary)]">
        <div className="max-w-3xl mx-auto px-6 py-16 space-y-8">
          <header className="space-y-3">
            <h1 className="font-display text-4xl md:text-5xl font-semibold text-[var(--text-primary)]">
              Contact
            </h1>
            <p className="text-[var(--text-secondary)]">
              Reconstruction mode is active: billing and auth are disabled. If you need sales or
              support, use the links below.
            </p>
          </header>

          <section className="rounded-2xl border border-[var(--border)] bg-[var(--bg-secondary)] p-6 space-y-4">
            <form onSubmit={onSubmit} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <input
                  className="px-3 py-2 rounded-lg border border-[var(--border)] bg-[var(--bg-primary)] text-[var(--text-primary)]"
                  placeholder="Your name"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  maxLength={120}
                  required
                />
                <input
                  className="px-3 py-2 rounded-lg border border-[var(--border)] bg-[var(--bg-primary)] text-[var(--text-primary)]"
                  placeholder="you@company.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  type="email"
                  required
                />
              </div>
              <input
                className="w-full px-3 py-2 rounded-lg border border-[var(--border)] bg-[var(--bg-primary)] text-[var(--text-primary)]"
                placeholder="Subject"
                value={subject}
                onChange={(e) => setSubject(e.target.value)}
                maxLength={160}
                required
              />
              <textarea
                className="w-full min-h-[140px] px-3 py-2 rounded-lg border border-[var(--border)] bg-[var(--bg-primary)] text-[var(--text-primary)]"
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
                  className="px-4 py-2 rounded-lg bg-[var(--accent)] text-white text-sm font-medium disabled:opacity-50"
                >
                  {isSending ? "Sending..." : "Send Message"}
                </button>
                {result ? <p className="text-sm text-[var(--text-secondary)]">{result}</p> : null}
              </div>
            </form>

            <div className="space-y-1">
              <h2 className="font-display text-xl font-semibold text-[var(--text-primary)]">
                Open The App
              </h2>
              <p className="text-sm text-[var(--text-secondary)]">
                Go to{" "}
                <Link className="text-[var(--accent)] hover:underline" href="/dashboard">
                  /dashboard
                </Link>{" "}
                (no login required).
              </p>
            </div>

            <div className="text-xs text-[var(--text-muted)] font-mono">
              Tenant boundary: <span className="text-[var(--text-primary)]">x-workspace-id</span>
            </div>
          </section>
        </div>

        <Footer />
      </div>
    </main>
  );
}
