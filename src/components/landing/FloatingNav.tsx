"use client";

import { useEffect, useState, useRef } from "react";
import gsap from "gsap";
import Link from "next/link";
import { Logo } from "@/components/brand";
import { 
  ArrowRight, 
  Menu, 
  X, 
  ChevronDown,
  Sparkles,
  Zap,
  BookOpen,
  HelpCircle,
  FileText,
  Mail,
  Shield,
  Scale,
  Cookie,
  Rocket
} from "lucide-react";

// ═══════════════════════════════════════════════════════════════════════════════
// FLOATING NAVIGATION — Comprehensive Header with All Links
// Uses the intricate Logo component
// ═══════════════════════════════════════════════════════════════════════════════

const NAV_PRODUCT = [
  { id: "features", label: "Features", href: "#features", icon: Sparkles },
  { id: "demo", label: "Demo", href: "#demo", icon: Zap },
  { id: "foundation", label: "Foundation", href: "/foundation", icon: Shield },
  { id: "moves", label: "Moves", href: "/moves", icon: Rocket },
  { id: "pricing", label: "Pricing", href: "/pricing", icon: null },
];

const NAV_RESOURCES = [
  { id: "docs", label: "Documentation", href: "/docs", icon: BookOpen },
  { id: "support", label: "Support Center", href: "/support", icon: HelpCircle },
  { id: "changelog", label: "Changelog", href: "/changelog", icon: FileText },
  { id: "api", label: "API Reference", href: "/api", icon: FileText },
];

const NAV_COMPANY = [
  { id: "about", label: "About", href: "/about", icon: null },
  { id: "contact", label: "Contact", href: "/contact", icon: Mail },
  { id: "privacy", label: "Privacy Policy", href: "/legal/privacy", icon: Shield },
  { id: "terms", label: "Terms of Service", href: "/legal/terms", icon: Scale },
  { id: "cookies", label: "Cookie Policy", href: "/legal/cookies", icon: Cookie },
];

export function FloatingNav() {
  const [isVisible, setIsVisible] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [activeSection, setActiveSection] = useState("");
  const [activeDropdown, setActiveDropdown] = useState<string | null>(null);
  const navRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleScroll = () => {
      setIsVisible(window.scrollY > window.innerHeight * 0.5);

      const sections = ["features", "demo", "philosophy", "built-for"];
      for (const section of sections) {
        const element = document.getElementById(section);
        if (element) {
          const rect = element.getBoundingClientRect();
          if (rect.top <= 150 && rect.bottom >= 150) {
            setActiveSection(section);
            break;
          }
        }
      }
    };

    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  useEffect(() => {
    if (isVisible) {
      gsap.fromTo(
        ".floating-nav",
        { y: -100, opacity: 0 },
        { y: 0, opacity: 1, duration: 0.5, ease: "power3.out" }
      );
    }
  }, [isVisible]);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (navRef.current && !navRef.current.contains(event.target as Node)) {
        setActiveDropdown(null);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const scrollToSection = (id: string) => {
    if (id.startsWith("#")) {
      const element = document.getElementById(id.slice(1));
      if (element) {
        element.scrollIntoView({ behavior: "smooth" });
      }
    }
    setIsMobileMenuOpen(false);
    setActiveDropdown(null);
  };

  const toggleDropdown = (dropdown: string) => {
    setActiveDropdown(activeDropdown === dropdown ? null : dropdown);
  };

  if (!isVisible) return null;

  return (
    <>
      <div 
        ref={navRef}
        className="floating-nav fixed top-4 left-0 right-0 z-50 px-4"
      >
        <div className="max-w-6xl mx-auto bg-[#F3F0E7]/95 backdrop-blur-xl border border-[#E3DED3] rounded-2xl px-4 py-2 shadow-lg">
          <div className="flex items-center justify-between gap-4">
            {/* Logo with magnetic effect */}
            <Link href="/" className="flex items-center gap-2 flex-shrink-0 group">
              <Logo 
                size={32} 
                mode="light" 
                magnetic={true}
                className="transition-transform duration-300" 
              />
              <span className="font-semibold text-[#2A2529] hidden sm:block">RaptorFlow</span>
            </Link>

            {/* Desktop Nav */}
            <div className="hidden lg:flex items-center gap-1">
              {/* Product Dropdown */}
              <div className="relative">
                <button
                  onClick={() => toggleDropdown("product")}
                  className={`flex items-center gap-1 px-3 py-2 rounded-lg text-sm transition-colors ${
                    activeDropdown === "product" 
                      ? "bg-[#F7F5EF] text-[#2A2529]" 
                      : "text-[#5C565B] hover:text-[#2A2529] hover:bg-[#F7F5EF]/50"
                  }`}
                >
                  Product
                  <ChevronDown size={14} className={`transition-transform ${activeDropdown === "product" ? "rotate-180" : ""}`} />
                </button>
                
                {activeDropdown === "product" && (
                  <div className="absolute top-full left-0 mt-2 w-56 bg-[#F3F0E7] border border-[#E3DED3] rounded-xl shadow-lg overflow-hidden animate-in fade-in slide-in-from-top-2">
                    {NAV_PRODUCT.map((item) => (
                      <Link
                        key={item.id}
                        href={item.href}
                        onClick={() => scrollToSection(item.href)}
                        className={`flex items-center gap-3 px-4 py-3 hover:bg-[#F7F5EF] transition-colors ${
                          activeSection === item.id ? "text-[#2A2529] bg-[#F7F5EF]" : "text-[#5C565B]"
                        }`}
                      >
                        {item.icon && <item.icon size={16} />}
                        <span className="rf-body-sm">{item.label}</span>
                      </Link>
                    ))}
                  </div>
                )}
              </div>

              {/* Resources Dropdown */}
              <div className="relative">
                <button
                  onClick={() => toggleDropdown("resources")}
                  className={`flex items-center gap-1 px-3 py-2 rounded-lg text-sm transition-colors ${
                    activeDropdown === "resources" 
                      ? "bg-[#F7F5EF] text-[#2A2529]" 
                      : "text-[#5C565B] hover:text-[#2A2529] hover:bg-[#F7F5EF]/50"
                  }`}
                >
                  Resources
                  <ChevronDown size={14} className={`transition-transform ${activeDropdown === "resources" ? "rotate-180" : ""}`} />
                </button>
                
                {activeDropdown === "resources" && (
                  <div className="absolute top-full left-0 mt-2 w-56 bg-[#F3F0E7] border border-[#E3DED3] rounded-xl shadow-lg overflow-hidden animate-in fade-in slide-in-from-top-2">
                    {NAV_RESOURCES.map((item) => (
                      <Link
                        key={item.id}
                        href={item.href}
                        onClick={() => setActiveDropdown(null)}
                        className="flex items-center gap-3 px-4 py-3 text-[#5C565B] hover:text-[#2A2529] hover:bg-[#F7F5EF] transition-colors"
                      >
                        <item.icon size={16} />
                        <span className="rf-body-sm">{item.label}</span>
                      </Link>
                    ))}
                  </div>
                )}
              </div>

              {/* Company Dropdown */}
              <div className="relative">
                <button
                  onClick={() => toggleDropdown("company")}
                  className={`flex items-center gap-1 px-3 py-2 rounded-lg text-sm transition-colors ${
                    activeDropdown === "company" 
                      ? "bg-[#F7F5EF] text-[#2A2529]" 
                      : "text-[#5C565B] hover:text-[#2A2529] hover:bg-[#F7F5EF]/50"
                  }`}
                >
                  Company
                  <ChevronDown size={14} className={`transition-transform ${activeDropdown === "company" ? "rotate-180" : ""}`} />
                </button>
                
                {activeDropdown === "company" && (
                  <div className="absolute top-full left-0 mt-2 w-56 bg-[#F3F0E7] border border-[#E3DED3] rounded-xl shadow-lg overflow-hidden animate-in fade-in slide-in-from-top-2">
                    {NAV_COMPANY.map((item) => (
                      <Link
                        key={item.id}
                        href={item.href}
                        onClick={() => setActiveDropdown(null)}
                        className="flex items-center gap-3 px-4 py-3 text-[#5C565B] hover:text-[#2A2529] hover:bg-[#F7F5EF] transition-colors"
                      >
                        {item.icon && <item.icon size={16} />}
                        <span className="rf-body-sm">{item.label}</span>
                      </Link>
                    ))}
                  </div>
                )}
              </div>
            </div>

            {/* Right side actions */}
            <div className="flex items-center gap-2">
              <Link
                href="/support"
                className="hidden sm:flex items-center gap-2 px-3 py-2 text-sm text-[#5C565B] hover:text-[#2A2529] transition-colors"
              >
                <HelpCircle size={16} />
                <span className="hidden md:inline">Help</span>
              </Link>

              <Link
                href="/dashboard"
                className="rf-btn rf-btn-primary h-9 px-4 text-sm hidden sm:flex items-center gap-2 bg-[#2A2529] text-[#F3F0E7] rounded-lg hover:bg-[#3A3539] transition-colors"
              >
                Start Building
                <ArrowRight size={14} />
              </Link>

              {/* Mobile menu button */}
              <button
                onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
                className="lg:hidden w-9 h-9 flex items-center justify-center rounded-lg bg-[#F7F5EF] hover:bg-[#E3DED3] transition-colors"
              >
                {isMobileMenuOpen ? <X size={18} /> : <Menu size={18} />}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Mobile Menu */}
      {isMobileMenuOpen && (
        <div className="fixed inset-0 z-40 bg-[#F3F0E7]/98 backdrop-blur-xl pt-24 px-6 lg:hidden overflow-y-auto">
          <div className="space-y-6 pb-24">
            {/* Product Section */}
            <div>
              <h3 className="rf-label text-[#847C82] mb-3 uppercase tracking-wider">Product</h3>
              <div className="space-y-1">
                {NAV_PRODUCT.map((item) => (
                  <Link
                    key={item.id}
                    href={item.href}
                    onClick={() => scrollToSection(item.href)}
                    className="flex items-center gap-3 w-full p-3 rounded-lg hover:bg-[#F7F5EF] transition-colors"
                  >
                    {item.icon && <item.icon size={18} className="text-[#5C565B]" />}
                    <span className="rf-body text-[#2A2529]">{item.label}</span>
                  </Link>
                ))}
              </div>
            </div>

            {/* Resources Section */}
            <div>
              <h3 className="rf-label text-[#847C82] mb-3 uppercase tracking-wider">Resources</h3>
              <div className="space-y-1">
                {NAV_RESOURCES.map((item) => (
                  <Link
                    key={item.id}
                    href={item.href}
                    onClick={() => setIsMobileMenuOpen(false)}
                    className="flex items-center gap-3 w-full p-3 rounded-lg hover:bg-[#F7F5EF] transition-colors"
                  >
                    <item.icon size={18} className="text-[#5C565B]" />
                    <span className="rf-body text-[#2A2529]">{item.label}</span>
                  </Link>
                ))}
              </div>
            </div>

            {/* Company Section */}
            <div>
              <h3 className="rf-label text-[#847C82] mb-3 uppercase tracking-wider">Company & Legal</h3>
              <div className="space-y-1">
                {NAV_COMPANY.map((item) => (
                  <Link
                    key={item.id}
                    href={item.href}
                    onClick={() => setIsMobileMenuOpen(false)}
                    className="flex items-center gap-3 w-full p-3 rounded-lg hover:bg-[#F7F5EF] transition-colors"
                  >
                    {item.icon && <item.icon size={18} className="text-[#5C565B]" />}
                    <span className="rf-body text-[#2A2529]">{item.label}</span>
                  </Link>
                ))}
              </div>
            </div>

            {/* CTA */}
            <div className="pt-6 border-t border-[#E3DED3]">
              <Link
                href="/dashboard"
                className="rf-btn rf-btn-primary w-full justify-center h-14 text-lg bg-[#2A2529] text-[#F3F0E7] rounded-lg hover:bg-[#3A3539] transition-colors flex items-center gap-2"
                onClick={() => setIsMobileMenuOpen(false)}
              >
                Start Building Free
                <ArrowRight size={18} />
              </Link>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
