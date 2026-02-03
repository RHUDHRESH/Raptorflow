"use client";

import { HugeiconsIcon } from "@hugeicons/react";
import {
  CoffeeBean01Icon,
  TwitterIcon,
  Linkedin01Icon,
  GithubIcon,
  InstagramIcon
} from "@hugeicons/core-free-icons";

const footerLinks = {
  product: [
    { label: "Features", href: "#features" },
    { label: "Pricing", href: "#pricing" },
    { label: "Integrations", href: "#" },
    { label: "Changelog", href: "#" },
    { label: "Roadmap", href: "#" },
  ],
  company: [
    { label: "About", href: "#" },
    { label: "Blog", href: "#" },
    { label: "Careers", href: "#" },
    { label: "Press Kit", href: "#" },
    { label: "Contact", href: "#" },
  ],
  resources: [
    { label: "Documentation", href: "#" },
    { label: "Help Center", href: "#" },
    { label: "Community", href: "#" },
    { label: "Templates", href: "#" },
    { label: "API Reference", href: "#" },
  ],
  legal: [
    { label: "Privacy Policy", href: "#" },
    { label: "Terms of Service", href: "#" },
    { label: "Cookie Policy", href: "#" },
    { label: "Security", href: "#" },
  ],
};

const socialLinks = [
  { icon: TwitterIcon, href: "#", label: "Twitter" },
  { icon: Linkedin01Icon, href: "#", label: "LinkedIn" },
  { icon: GithubIcon, href: "#", label: "GitHub" },
  { icon: InstagramIcon, href: "#", label: "Instagram" },
];

export function Footer() {
  return (
    <footer className="relative bg-shaft-500 pt-20 pb-8">
      <div className="max-w-7xl mx-auto px-6 lg:px-8">
        {/* Main Footer Content */}
        <div className="grid grid-cols-2 md:grid-cols-6 gap-8 lg:gap-12 pb-16 border-b border-barley/10">
          {/* Brand Column */}
          <div className="col-span-2">
            <a href="#" className="flex items-center gap-2 mb-6 group">
              <HugeiconsIcon
                icon={CoffeeBeansIcon}
                className="w-8 h-8 text-barley transition-transform duration-500 group-hover:rotate-12"
              />
              <span className="font-display text-2xl font-semibold text-rock tracking-tight">
                Raptor<span className="text-barley">Flow</span>
              </span>
            </a>
            <p className="text-akaroa-200/50 text-sm leading-relaxed mb-6 max-w-xs">
              Crafted with care for teams who appreciate the art of automation.
              Brew better workflows.
            </p>

            {/* Social Links */}
            <div className="flex gap-3">
              {socialLinks.map((social) => {
                const Icon = social.icon;
                return (
                  <a
                    key={social.label}
                    href={social.href}
                    className="w-10 h-10 rounded-full bg-shaft-400/30 flex items-center justify-center text-rock/60 hover:bg-barley/20 hover:text-barley transition-all duration-300"
                    aria-label={social.label}
                    data-cursor-hover
                  >
                    <HugeiconsIcon icon={Icon} className="w-5 h-5" />
                  </a>
                );
              })}
            </div>
          </div>

          {/* Link Columns */}
          <div>
            <h4 className="text-rock font-medium mb-4 text-sm tracking-wide uppercase">Product</h4>
            <ul className="space-y-3">
              {footerLinks.product.map((link) => (
                <li key={link.label}>
                  <a
                    href={link.href}
                    className="text-akaroa-200/50 text-sm hover:text-barley transition-colors duration-300"
                    data-cursor-hover
                  >
                    {link.label}
                  </a>
                </li>
              ))}
            </ul>
          </div>

          <div>
            <h4 className="text-rock font-medium mb-4 text-sm tracking-wide uppercase">Company</h4>
            <ul className="space-y-3">
              {footerLinks.company.map((link) => (
                <li key={link.label}>
                  <a
                    href={link.href}
                    className="text-akaroa-200/50 text-sm hover:text-barley transition-colors duration-300"
                    data-cursor-hover
                  >
                    {link.label}
                  </a>
                </li>
              ))}
            </ul>
          </div>

          <div>
            <h4 className="text-rock font-medium mb-4 text-sm tracking-wide uppercase">Resources</h4>
            <ul className="space-y-3">
              {footerLinks.resources.map((link) => (
                <li key={link.label}>
                  <a
                    href={link.href}
                    className="text-akaroa-200/50 text-sm hover:text-barley transition-colors duration-300"
                    data-cursor-hover
                  >
                    {link.label}
                  </a>
                </li>
              ))}
            </ul>
          </div>

          <div>
            <h4 className="text-rock font-medium mb-4 text-sm tracking-wide uppercase">Legal</h4>
            <ul className="space-y-3">
              {footerLinks.legal.map((link) => (
                <li key={link.label}>
                  <a
                    href={link.href}
                    className="text-akaroa-200/50 text-sm hover:text-barley transition-colors duration-300"
                    data-cursor-hover
                  >
                    {link.label}
                  </a>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="pt-8 flex flex-col md:flex-row items-center justify-between gap-4">
          <p className="text-akaroa-200/40 text-sm">
            © {new Date().getFullYear()} RaptorFlow. Crafted with precision.
          </p>
          <div className="flex items-center gap-6">
            <span className="text-akaroa-200/40 text-sm flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
              All systems operational
            </span>
          </div>
        </div>
      </div>
    </footer>
  );
}
