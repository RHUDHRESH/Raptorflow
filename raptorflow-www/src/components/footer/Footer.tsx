import Link from "next/link";
import { COPY } from "@/lib/copy";
import { Twitter, Linkedin } from "lucide-react";

export function Footer() {
  return (
    <footer className="border-t border-rf-mineshaft/50 bg-rf-card/50">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
          {/* Left: Wordmark & Mission */}
          <div className="md:col-span-1">
            <h3 className="text-xl font-bold text-rf-ink mb-4">RaptorFlow</h3>
            <p className="text-sm text-rf-subtle leading-relaxed">
              {COPY.footer.mission}
            </p>
          </div>

          {/* Product Links */}
          <div>
            <h4 className="text-sm font-semibold text-rf-ink mb-4">
              {COPY.footer.product.title}
            </h4>
            <ul className="space-y-2 text-sm text-rf-subtle">
              {COPY.footer.product.links.map((link) => (
                <li key={link}>
                  <Link
                    href={`#${link.toLowerCase()}`}
                    className="hover:text-rf-ink transition-colors"
                  >
                    {link}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Company Links */}
          <div>
            <h4 className="text-sm font-semibold text-rf-ink mb-4">
              {COPY.footer.company.title}
            </h4>
            <ul className="space-y-2 text-sm text-rf-subtle">
              {COPY.footer.company.links.map((link) => (
                <li key={link}>
                  <Link
                    href={`/${link.toLowerCase()}`}
                    className="hover:text-rf-ink transition-colors"
                  >
                    {link}
                  </Link>
                </li>
              ))}
            </ul>
            <div className="mt-4 text-sm text-rf-subtle">
              <a
                href={`mailto:${COPY.footer.contact.email}`}
                className="hover:text-rf-ink transition-colors"
              >
                {COPY.footer.contact.email}
              </a>
            </div>
          </div>

          {/* Legal Links */}
          <div>
            <h4 className="text-sm font-semibold text-rf-ink mb-4">Legal</h4>
            <ul className="space-y-2 text-sm text-rf-subtle">
              {COPY.footer.legal.links.map((link) => (
                <li key={link}>
                  <Link
                    href={`/${link.toLowerCase().replace(/\s+/g, "-")}`}
                    className="hover:text-rf-ink transition-colors"
                  >
                    {link}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Bottom Row */}
        <div className="pt-8 border-t border-rf-mineshaft/50 flex flex-col sm:flex-row justify-between items-center gap-4">
          <p className="text-sm text-rf-subtle">
            &copy; {new Date().getFullYear()} RaptorFlow. All rights reserved.
          </p>
          <div className="flex items-center gap-4">
            <a
              href="https://twitter.com"
              target="_blank"
              rel="noopener noreferrer"
              className="text-rf-subtle hover:text-rf-ink transition-colors"
              aria-label="Twitter"
            >
              <Twitter className="w-5 h-5" />
            </a>
            <a
              href="https://linkedin.com"
              target="_blank"
              rel="noopener noreferrer"
              className="text-rf-subtle hover:text-rf-ink transition-colors"
              aria-label="LinkedIn"
            >
              <Linkedin className="w-5 h-5" />
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
}
