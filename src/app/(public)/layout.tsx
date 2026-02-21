// ═══════════════════════════════════════════════════════════════════════════════
// PUBLIC LAYOUT — No workspace required
// For landing, docs, support, legal pages
// ═══════════════════════════════════════════════════════════════════════════════

import { ReactNode } from "react";
import Link from "next/link";
import { Logo, Wordmark } from "@/components/brand";
import {
  ArrowRight,
  HelpCircle,
  BookOpen,
  MessageCircle,
  FileText,
  Shield,
  Scale,
  Cookie,
} from "lucide-react";

export default function PublicLayout({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen bg-[#F3F0E7]">
      {/* Public Navigation */}
      <header className="fixed top-0 left-0 right-0 z-50 bg-[#F3F0E7]/90 backdrop-blur-xl border-b border-[#E3DED3]">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            {/* Logo with Wordmark */}
            <Link href="/" className="flex items-center gap-3 group">
              <Logo
                size={36}
                className="transition-transform duration-300 group-hover:scale-105"
              />
              <span className="font-semibold text-xl text-[#2A2529] tracking-tight">
                RaptorFlow
              </span>
            </Link>

            {/* Center Navigation */}
            <nav className="hidden md:flex items-center gap-6">
              <Link href="/docs" className="rf-body-sm text-[#5C565B] hover:text-[#2A2529] transition-colors flex items-center gap-2">
                <BookOpen size={16} />
                Docs
              </Link>
              <Link href="/support" className="rf-body-sm text-[#5C565B] hover:text-[#2A2529] transition-colors flex items-center gap-2">
                <HelpCircle size={16} />
                Support
              </Link>
              <Link href="/changelog" className="rf-body-sm text-[#5C565B] hover:text-[#2A2529] transition-colors flex items-center gap-2">
                <FileText size={16} />
                Changelog
              </Link>
            </nav>

            {/* Right Actions */}
            <div className="flex items-center gap-3">
              <Link
                href="/login"
                className="hidden sm:block rf-body-sm text-[#5C565B] hover:text-[#2A2529] px-4 py-2 transition-colors"
              >
                Sign In
              </Link>
              <Link
                href="/dashboard"
                className="rf-btn rf-btn-primary h-10 px-5 text-sm flex items-center gap-2 bg-[#2A2529] text-[#F3F0E7] rounded-lg hover:bg-[#3A3539] transition-colors"
              >
                Start Building
                <ArrowRight size={14} />
              </Link>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="pt-20">
        {children}
      </main>

      {/* Public Footer */}
      <footer className="py-16 px-6 border-t border-[#E3DED3] bg-[#F7F5EF]">
        <div className="max-w-6xl mx-auto">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 mb-12">
            {/* Brand */}
            <div className="col-span-2 md:col-span-1">
              <Link href="/" className="flex items-center gap-2 mb-4 group">
                <Logo size={28} className="transition-transform group-hover:scale-105" />
                <span className="font-semibold text-[#2A2529]">RaptorFlow</span>
              </Link>
              <p className="rf-body-sm text-[#5C565B] mb-4">
                The marketing OS for operators.
              </p>
            </div>

            {/* Product */}
            <div>
              <h4 className="rf-label mb-4 text-[#2A2529]">Product</h4>
              <ul className="space-y-2">
                <li><Link href="/docs" className="rf-body-sm text-[#5C565B] hover:text-[#2A2529]">Documentation</Link></li>
                <li><Link href="/support" className="rf-body-sm text-[#5C565B] hover:text-[#2A2529]">Support</Link></li>
                <li><Link href="/changelog" className="rf-body-sm text-[#5C565B] hover:text-[#2A2529]">Changelog</Link></li>
                <li><Link href="/pricing" className="rf-body-sm text-[#5C565B] hover:text-[#2A2529]">Pricing</Link></li>
              </ul>
            </div>

            {/* Legal */}
            <div>
              <h4 className="rf-label mb-4 text-[#2A2529]">Legal</h4>
              <ul className="space-y-2">
                <li><Link href="/legal/privacy" className="rf-body-sm text-[#5C565B] hover:text-[#2A2529] flex items-center gap-2"><Shield size={14} /> Privacy</Link></li>
                <li><Link href="/legal/terms" className="rf-body-sm text-[#5C565B] hover:text-[#2A2529] flex items-center gap-2"><Scale size={14} /> Terms</Link></li>
                <li><Link href="/legal/cookies" className="rf-body-sm text-[#5C565B] hover:text-[#2A2529] flex items-center gap-2"><Cookie size={14} /> Cookies</Link></li>
              </ul>
            </div>

            {/* Contact */}
            <div>
              <h4 className="rf-label mb-4 text-[#2A2529]">Contact</h4>
              <ul className="space-y-2">
                <li><a href="mailto:hello@raptorflow.ai" className="rf-body-sm text-[#5C565B] hover:text-[#2A2529] flex items-center gap-2"><MessageCircle size={14} /> hello@raptorflow.ai</a></li>
                <li><a href="mailto:support@raptorflow.ai" className="rf-body-sm text-[#5C565B] hover:text-[#2A2529] flex items-center gap-2"><HelpCircle size={14} /> Support</a></li>
              </ul>
            </div>
          </div>

          <div className="pt-8 border-t border-[#E3DED3] flex flex-col md:flex-row items-center justify-between gap-4">
            <p className="rf-mono-xs text-[#847C82]">
              © 2026 RaptorFlow. All rights reserved.
            </p>
            <div className="flex items-center gap-6">
              <Link href="/legal/privacy" className="rf-mono-xs text-[#847C82] hover:text-[#2A2529]">Privacy</Link>
              <Link href="/legal/terms" className="rf-mono-xs text-[#847C82] hover:text-[#2A2529]">Terms</Link>
              <Link href="/legal/cookies" className="rf-mono-xs text-[#847C82] hover:text-[#2A2529]">Cookies</Link>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
