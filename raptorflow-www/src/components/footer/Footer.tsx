import Link from "next/link";
import { cn } from "@/lib/utils";

export function Footer() {
  return (
    <footer className="border-t border-rf-mineshaft/50 bg-rf-card/50">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div>
            <h3 className="text-lg font-semibold text-rf-ink mb-4">RaptorFlow</h3>
            <p className="text-sm text-rf-subtle">
              Marketing that actually works for founders, small teams, and indie hackers.
            </p>
          </div>
          <div>
            <h4 className="text-sm font-semibold text-rf-ink mb-4">Product</h4>
            <ul className="space-y-2 text-sm text-rf-subtle">
              <li>
                <Link href="#features" className="hover:text-rf-ink transition-colors">
                  Features
                </Link>
              </li>
              <li>
                <Link href="#pricing" className="hover:text-rf-ink transition-colors">
                  Pricing
                </Link>
              </li>
            </ul>
          </div>
          <div>
            <h4 className="text-sm font-semibold text-rf-ink mb-4">Company</h4>
            <ul className="space-y-2 text-sm text-rf-subtle">
              <li>
                <Link href="/about" className="hover:text-rf-ink transition-colors">
                  About
                </Link>
              </li>
              <li>
                <Link href="/blog" className="hover:text-rf-ink transition-colors">
                  Blog
                </Link>
              </li>
            </ul>
          </div>
          <div>
            <h4 className="text-sm font-semibold text-rf-ink mb-4">Legal</h4>
            <ul className="space-y-2 text-sm text-rf-subtle">
              <li>
                <Link href="/privacy" className="hover:text-rf-ink transition-colors">
                  Privacy
                </Link>
              </li>
              <li>
                <Link href="/terms" className="hover:text-rf-ink transition-colors">
                  Terms
                </Link>
              </li>
            </ul>
          </div>
        </div>
        <div className="mt-8 pt-8 border-t border-rf-mineshaft/50 text-center text-sm text-rf-subtle">
          <p>&copy; {new Date().getFullYear()} RaptorFlow. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
}

