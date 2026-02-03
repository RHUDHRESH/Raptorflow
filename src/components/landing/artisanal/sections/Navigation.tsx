"use client";

import { useEffect, useState, useRef } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { HugeiconsIcon } from "@hugeicons/react";
import { 
  CoffeeBean01Icon, 
  Menu01Icon, 
  Cancel01Icon,
  ArrowRight01Icon 
} from "@hugeicons/core-free-icons";

const navLinks = [
  { label: "Features", href: "#features" },
  { label: "How it Works", href: "#how-it-works" },
  { label: "Pricing", href: "#pricing" },
  { label: "FAQ", href: "#faq" },
];

export function Navigation() {
  const [isScrolled, setIsScrolled] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const navRef = useRef<HTMLElement>(null);

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 100);
    };

    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  useEffect(() => {
    if (!navRef.current) return;

    const ctx = gsap.context(() => {
      gsap.fromTo(
        navRef.current,
        { y: -100, opacity: 0 },
        { y: 0, opacity: 1, duration: 0.8, delay: 0.2, ease: "power3.out" }
      );
    });

    return () => ctx.revert();
  }, []);

  const scrollToSection = (href: string) => {
    const element = document.querySelector(href);
    if (element) {
      element.scrollIntoView({ behavior: "smooth" });
    }
    setIsMobileMenuOpen(false);
  };

  return (
    <>
      <nav
        ref={navRef}
        className={`fixed top-0 left-0 right-0 z-50 transition-all duration-500
          ${isScrolled 
            ? "bg-shaft-500/95 backdrop-blur-md py-4 shadow-lg shadow-black/10" 
            : "bg-transparent py-6"
          }
        `}
      >
        <div className="max-w-7xl mx-auto px-6 lg:px-8 flex items-center justify-between">
          {/* Logo */}
          <a 
            href="#" 
            className="flex items-center gap-2 group"
            data-cursor-hover
          >
            <div className="relative">
              <HugeiconsIcon 
                icon={CoffeeBeansIcon}
                className="w-8 h-8 text-barley transition-transform duration-500 group-hover:rotate-12" 
              />
              <div className="absolute inset-0 bg-barley/20 blur-xl rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
            </div>
            <span className="font-display text-2xl font-semibold text-rock tracking-tight">
              Raptor<span className="text-barley">Flow</span>
            </span>
          </a>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center gap-8">
            {navLinks.map((link) => (
              <button
                key={link.label}
                onClick={() => scrollToSection(link.href)}
                className="relative text-rock/80 hover:text-rock transition-colors duration-300 text-sm font-medium tracking-wide group"
                data-cursor-hover
              >
                {link.label}
                <span className="absolute -bottom-1 left-0 w-0 h-px bg-barley transition-all duration-300 group-hover:w-full" />
              </button>
            ))}
          </div>

          {/* CTA Button */}
          <div className="hidden md:flex items-center gap-4">
            <button 
              className="group relative px-6 py-2.5 bg-barley text-shaft-500 font-medium text-sm rounded-full overflow-hidden transition-all duration-300 hover:shadow-lg hover:shadow-barley/25"
              data-cursor-hover
            >
              <span className="relative z-10 flex items-center gap-2">
                Get Started
                <HugeiconsIcon icon={ArrowRight01Icon} className="w-4 h-4 transition-transform duration-300 group-hover:translate-x-1" />
              </span>
              <div className="absolute inset-0 bg-akaroa-300 transform scale-x-0 origin-left transition-transform duration-300 group-hover:scale-x-100" />
            </button>
          </div>

          {/* Mobile Menu Button */}
          <button
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            className="md:hidden p-2 text-rock"
            data-cursor-hover
          >
            {isMobileMenuOpen ? (
              <HugeiconsIcon icon={Cancel01Icon} className="w-6 h-6" />
            ) : (
              <HugeiconsIcon icon={Menu01Icon} className="w-6 h-6" />
            )}
          </button>
        </div>
      </nav>

      {/* Mobile Menu */}
      <div
        className={`fixed inset-0 z-40 bg-shaft-500 transition-all duration-500 md:hidden
          ${isMobileMenuOpen ? "opacity-100 visible" : "opacity-0 invisible"}
        `}
      >
        <div className="flex flex-col items-center justify-center h-full gap-8">
          {navLinks.map((link, index) => (
            <button
              key={link.label}
              onClick={() => scrollToSection(link.href)}
              className="text-rock text-3xl font-display hover:text-barley transition-colors duration-300"
              style={{ 
                transitionDelay: isMobileMenuOpen ? `${index * 100}ms` : "0ms",
                opacity: isMobileMenuOpen ? 1 : 0,
                transform: isMobileMenuOpen ? "translateY(0)" : "translateY(20px)"
              }}
            >
              {link.label}
            </button>
          ))}
          <button 
            className="mt-8 px-8 py-3 bg-barley text-shaft-500 font-medium rounded-full"
            onClick={() => setIsMobileMenuOpen(false)}
          >
            Get Started
          </button>
        </div>
      </div>
    </>
  );
}
