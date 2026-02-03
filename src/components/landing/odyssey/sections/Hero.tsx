"use client";

import { useEffect, useRef } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import Link from "next/link";
import { ArrowRight, Sparkles } from "lucide-react";
import { AnimatedCompass } from "../shared/AnimatedCompass";

export function Hero() {
  const heroRef = useRef<HTMLDivElement>(null);
  const titleRef = useRef<HTMLHeadingElement>(null);
  const subtitleRef = useRef<HTMLParagraphElement>(null);
  const ctaRef = useRef<HTMLDivElement>(null);
  const compassContainerRef = useRef<HTMLDivElement>(null);
  const badgeRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!heroRef.current) return;

    const ctx = gsap.context(() => {
      // Master timeline for entrance
      const tl = gsap.timeline({
        defaults: { ease: "power3.out" },
        delay: 0.3,
      });

      // Badge entrance
      tl.fromTo(
        badgeRef.current,
        { y: 30, opacity: 0, scale: 0.9 },
        { y: 0, opacity: 1, scale: 1, duration: 0.8 }
      )
        // Title with split animation
        .fromTo(
          titleRef.current,
          { y: 100, opacity: 0, clipPath: "inset(100% 0 0 0)" },
          { y: 0, opacity: 1, clipPath: "inset(0% 0 0 0)", duration: 1.2 },
          "-=0.4"
        )
        // Subtitle
        .fromTo(
          subtitleRef.current,
          { y: 40, opacity: 0 },
          { y: 0, opacity: 1, duration: 0.8 },
          "-=0.6"
        )
        // CTA buttons
        .fromTo(
          ctaRef.current,
          { y: 30, opacity: 0 },
          { y: 0, opacity: 1, duration: 0.6 },
          "-=0.4"
        )
        // Compass entrance
        .fromTo(
          compassContainerRef.current,
          { scale: 0.5, opacity: 0, rotate: -30 },
          { scale: 1, opacity: 1, rotate: 0, duration: 1.5, ease: "elastic.out(1, 0.5)" },
          "-=1"
        );

      // Parallax scroll effect for compass
      gsap.to(compassContainerRef.current, {
        yPercent: 30,
        rotate: 15,
        ease: "none",
        scrollTrigger: {
          trigger: heroRef.current,
          start: "top top",
          end: "bottom top",
          scrub: 1,
        },
      });

      // Fade out on scroll
      gsap.to([titleRef.current, subtitleRef.current, ctaRef.current], {
        opacity: 0,
        y: -50,
        ease: "none",
        scrollTrigger: {
          trigger: heroRef.current,
          start: "center top",
          end: "bottom top",
          scrub: 1,
        },
      });
    }, heroRef);

    return () => ctx.revert();
  }, []);

  return (
    <section
      ref={heroRef}
      className="relative min-h-screen flex items-center justify-center pt-20 pb-32 overflow-hidden"
    >
      {/* Background Parallax Layers */}
      <div className="absolute inset-0 overflow-hidden">
        {/* Far mountains - slowest */}
        <div className="absolute bottom-0 left-0 right-0 h-[40vh]">
          <svg
            viewBox="0 0 1440 320"
            className="absolute bottom-0 w-full h-full opacity-20"
            preserveAspectRatio="none"
          >
            <path
              fill="url(#mountain-gradient-1)"
              d="M0,192L48,197.3C96,203,192,213,288,229.3C384,245,480,267,576,250.7C672,235,768,181,864,181.3C960,181,1056,235,1152,234.7C1248,235,1344,181,1392,154.7L1440,128L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z"
            />
            <defs>
              <linearGradient id="mountain-gradient-1" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" stopColor="#4c1d95" stopOpacity="0.5" />
                <stop offset="100%" stopColor="#1e1b4b" stopOpacity="0" />
              </linearGradient>
            </defs>
          </svg>
        </div>

        {/* Mid mountains */}
        <div className="absolute bottom-0 left-0 right-0 h-[30vh]">
          <svg
            viewBox="0 0 1440 320"
            className="absolute bottom-0 w-full h-full opacity-30"
            preserveAspectRatio="none"
          >
            <path
              fill="url(#mountain-gradient-2)"
              d="M0,256L48,261.3C96,267,192,277,288,266.7C384,256,480,224,576,213.3C672,203,768,213,864,224C960,235,1056,245,1152,234.7C1248,224,1344,192,1392,176L1440,160L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z"
            />
            <defs>
              <linearGradient id="mountain-gradient-2" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" stopColor="#7c3aed" stopOpacity="0.6" />
                <stop offset="100%" stopColor="#0a0a1a" stopOpacity="0" />
              </linearGradient>
            </defs>
          </svg>
        </div>

        {/* Foreground hills - fastest */}
        <div className="absolute bottom-0 left-0 right-0 h-[20vh]">
          <svg
            viewBox="0 0 1440 200"
            className="absolute bottom-0 w-full h-full opacity-40"
            preserveAspectRatio="none"
          >
            <path
              fill="url(#mountain-gradient-3)"
              d="M0,128L48,138.7C96,149,192,171,288,165.3C384,160,480,128,576,128C672,128,768,160,864,165.3C960,171,1056,149,1152,138.7C1248,128,1344,128,1392,128L1440,128L1440,200L1392,200C1344,200,1248,200,1152,200C1056,200,960,200,864,200C768,200,672,200,576,200C480,200,384,200,288,200C192,200,96,200,48,200L0,200Z"
            />
            <defs>
              <linearGradient id="mountain-gradient-3" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" stopColor="#9333ea" stopOpacity="0.8" />
                <stop offset="100%" stopColor="#0a0a1a" stopOpacity="0.5" />
              </linearGradient>
            </defs>
          </svg>
        </div>
      </div>

      {/* Content */}
      <div className="relative z-10 max-w-7xl mx-auto px-6 lg:px-8 w-full">
        <div className="grid lg:grid-cols-2 gap-12 lg:gap-16 items-center">
          {/* Left Content */}
          <div className="text-center lg:text-left">
            {/* Badge */}
            <div
              ref={badgeRef}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-purple-500/10 border border-purple-500/20 mb-8 backdrop-blur-sm"
            >
              <Sparkles className="w-4 h-4 text-purple-400" />
              <span className="text-purple-300 text-sm font-medium tracking-wide">
                The Marketing OS for Founders
              </span>
            </div>

            {/* Title */}
            <h1
              ref={titleRef}
              className="text-5xl sm:text-6xl lg:text-7xl xl:text-8xl font-bold leading-[0.95] tracking-tight mb-6"
            >
              <span className="text-white">Navigate</span>
              <br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 via-pink-400 to-blue-400 italic">
                Your Growth
              </span>
            </h1>

            {/* Subtitle */}
            <p
              ref={subtitleRef}
              className="text-lg sm:text-xl text-white/60 max-w-xl mx-auto lg:mx-0 mb-10 leading-relaxed"
            >
              Stop drowning in tool chaos. RaptorFlow is your strategic compass—guiding
              every marketing decision from first impression to loyal customer.
            </p>

            {/* CTAs */}
            <div ref={ctaRef} className="flex flex-col sm:flex-row gap-4 justify-center lg:justify-start">
              <Link
                href="/signup"
                className="group relative px-8 py-4 bg-gradient-to-r from-purple-600 to-blue-600 rounded-full font-semibold text-white overflow-hidden transition-all duration-300 hover:shadow-xl hover:shadow-purple-500/30"
              >
                <span className="relative z-10 flex items-center justify-center gap-2">
                  Start Your Journey
                  <ArrowRight className="w-5 h-5 transition-transform duration-300 group-hover:translate-x-1" />
                </span>
                <div className="absolute inset-0 bg-gradient-to-r from-purple-500 to-blue-500 translate-y-full group-hover:translate-y-0 transition-transform duration-300" />
              </Link>

              <Link
                href="#how-it-works"
                className="group px-8 py-4 border border-white/20 rounded-full font-medium text-white/80 transition-all duration-300 hover:bg-white/5 hover:border-white/40 flex items-center justify-center gap-2"
              >
                See How It Works
              </Link>
            </div>

            {/* Trust Indicators */}
            <div className="mt-12 pt-8 border-t border-white/10">
              <p className="text-white/40 text-sm mb-4 tracking-wide uppercase">
                Trusted by visionary founders
              </p>
              <div className="flex items-center justify-center lg:justify-start gap-8">
                {["YC", "Techstars", "500 Global", "Sequoia"].map((brand) => (
                  <span
                    key={brand}
                    className="text-white/30 font-semibold text-lg hover:text-white/60 transition-colors duration-300"
                  >
                    {brand}
                  </span>
                ))}
              </div>
            </div>
          </div>

          {/* Right Content - Animated Compass */}
          <div
            ref={compassContainerRef}
            className="relative flex items-center justify-center lg:justify-end"
          >
            <AnimatedCompass />
          </div>
        </div>
      </div>

      {/* Scroll Indicator */}
      <div className="absolute bottom-8 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2">
        <span className="text-white/30 text-xs tracking-widest uppercase">Scroll</span>
        <div className="w-6 h-10 border-2 border-white/20 rounded-full flex justify-center pt-2">
          <div className="w-1.5 h-3 bg-white/40 rounded-full animate-bounce" />
        </div>
      </div>
    </section>
  );
}
