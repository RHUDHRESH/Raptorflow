"use client";

import { useEffect, useRef } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { 
  Compass, 
  Target, 
  Zap, 
  BarChart3, 
  Users, 
  Sparkles 
} from "lucide-react";

const features = [
  {
    icon: Compass,
    title: "Strategic Foundation",
    description: "Build your marketing on rock-solid positioning. Know exactly who you serve and why they should care.",
    gradient: "from-purple-500 to-pink-500",
  },
  {
    icon: Target,
    title: "Precision Targeting",
    description: "Stop guessing. Our AI identifies your ideal customers and crafts messages that resonate deeply.",
    gradient: "from-blue-500 to-cyan-500",
  },
  {
    icon: Zap,
    title: "Automated Execution",
    description: "From strategy to scheduled content in minutes. Your marketing machine runs while you sleep.",
    gradient: "from-amber-500 to-orange-500",
  },
  {
    icon: BarChart3,
    title: "Real-time Analytics",
    description: "See what's working instantly. Data-driven insights guide every decision without the paralysis.",
    gradient: "from-emerald-500 to-teal-500",
  },
  {
    icon: Users,
    title: "Team Alignment",
    description: "Everyone on the same page. Your team executes with clarity, consistency, and confidence.",
    gradient: "from-rose-500 to-pink-500",
  },
  {
    icon: Sparkles,
    title: "AI-Powered Creativity",
    description: "Generate compelling content that sounds like you, not a robot. Authenticity at scale.",
    gradient: "from-violet-500 to-purple-500",
  },
];

export function Features() {
  const sectionRef = useRef<HTMLDivElement>(null);
  const cardsRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!sectionRef.current || !cardsRef.current) return;

    const ctx = gsap.context(() => {
      // Title animation
      gsap.fromTo(
        ".features-title",
        { y: 50, opacity: 0 },
        {
          y: 0,
          opacity: 1,
          duration: 0.8,
          ease: "power3.out",
          scrollTrigger: {
            trigger: ".features-title",
            start: "top 80%",
            toggleActions: "play none none reverse",
          },
        }
      );

      // Cards stagger animation
      const cards = cardsRef.current!.querySelectorAll(".feature-card");
      gsap.fromTo(
        cards,
        { y: 80, opacity: 0, scale: 0.9 },
        {
          y: 0,
          opacity: 1,
          scale: 1,
          duration: 0.6,
          stagger: 0.1,
          ease: "power3.out",
          scrollTrigger: {
            trigger: cardsRef.current,
            start: "top 75%",
            toggleActions: "play none none reverse",
          },
        }
      );
    }, sectionRef);

    return () => ctx.revert();
  }, []);

  return (
    <section
      ref={sectionRef}
      id="features"
      className="relative py-32 overflow-hidden"
    >
      <div className="relative z-10 max-w-7xl mx-auto px-6 lg:px-8">
        {/* Section Header */}
        <div className="features-title text-center mb-20">
          <span className="inline-block px-4 py-2 rounded-full bg-purple-500/10 border border-purple-500/20 text-purple-300 text-sm font-medium tracking-wide mb-6">
            Features
          </span>
          <h2 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-white mb-6">
            Everything You Need to{" "}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-blue-400">
              Win
            </span>
          </h2>
          <p className="text-lg text-white/60 max-w-2xl mx-auto">
            A complete marketing operating system. No more juggling tools, no more lost opportunities.
          </p>
        </div>

        {/* Features Grid */}
        <div
          ref={cardsRef}
          className="grid md:grid-cols-2 lg:grid-cols-3 gap-6"
        >
          {features.map((feature, index) => (
            <div
              key={index}
              className="feature-card group relative p-8 rounded-2xl bg-white/[0.03] border border-white/[0.08] backdrop-blur-sm hover:bg-white/[0.06] hover:border-white/[0.15] transition-all duration-500"
            >
              {/* Hover glow effect */}
              <div className="absolute inset-0 rounded-2xl bg-gradient-to-br from-purple-500/10 to-blue-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
              
              {/* Icon */}
              <div className={`relative inline-flex items-center justify-center w-14 h-14 rounded-xl bg-gradient-to-br ${feature.gradient} mb-6 shadow-lg`}>
                <feature.icon className="w-7 h-7 text-white" />
              </div>

              {/* Content */}
              <h3 className="relative text-xl font-semibold text-white mb-3 group-hover:text-transparent group-hover:bg-clip-text group-hover:bg-gradient-to-r group-hover:from-white group-hover:to-white/80 transition-all duration-300">
                {feature.title}
              </h3>
              <p className="relative text-white/50 leading-relaxed group-hover:text-white/70 transition-colors duration-300">
                {feature.description}
              </p>

              {/* Corner accent */}
              <div className="absolute top-0 right-0 w-20 h-20 overflow-hidden rounded-tr-2xl">
                <div className={`absolute -top-10 -right-10 w-20 h-20 bg-gradient-to-br ${feature.gradient} opacity-0 group-hover:opacity-20 transition-opacity duration-500 rotate-45`} />
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
