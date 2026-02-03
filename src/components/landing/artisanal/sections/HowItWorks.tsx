"use client";

import { useEffect, useRef } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { HugeiconsIcon } from "@hugeicons/react";
import { 
  Coffee01Icon,
  Settings02Icon,
  Rocket01Icon,
  ArrowRight01Icon
} from "@hugeicons/core-free-icons";

const steps = [
  {
    number: "01",
    icon: Coffee01Icon,
    title: "Brew Your Blueprint",
    description: "Start with a template or craft your workflow from scratch. Our visual canvas makes it as intuitive as sketching on paper.",
    details: ["50+ Pre-built Templates", "Visual Drag & Drop Builder", "AI Suggestions"],
  },
  {
    number: "02",
    icon: Settings02Icon,
    title: "Infuse Your Logic",
    description: "Add conditions, transformations, and integrations. Like adding the perfect notes to your signature roast.",
    details: ["Conditional Logic", "Data Transformations", "200+ Integrations"],
  },
  {
    number: "03",
    icon: Rocket01Icon,
    title: "Serve at Scale",
    description: "Deploy with one click and watch your workflows run flawlessly. Thousands of executions, zero maintenance.",
    details: ["One-Click Deploy", "Auto-Scaling", "24/7 Monitoring"],
  },
];

export function HowItWorks() {
  const sectionRef = useRef<HTMLDivElement>(null);
  const stepsRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!sectionRef.current) return;

    const ctx = gsap.context(() => {
      // Animate each step
      const stepElements = stepsRef.current?.querySelectorAll(".step-item");
      if (stepElements) {
        stepElements.forEach((step, index) => {
          const isEven = index % 2 === 0;
          
          gsap.fromTo(
            step,
            { 
              x: isEven ? -60 : 60, 
              opacity: 0 
            },
            {
              x: 0,
              opacity: 1,
              duration: 0.8,
              ease: "power3.out",
              scrollTrigger: {
                trigger: step,
                start: "top 80%",
                toggleActions: "play none none none",
              },
            }
          );
        });
      }

      // Animate connecting line
      gsap.fromTo(
        ".connecting-line",
        { scaleY: 0 },
        {
          scaleY: 1,
          duration: 1.5,
          ease: "power2.out",
          scrollTrigger: {
            trigger: stepsRef.current,
            start: "top 70%",
            end: "bottom 30%",
            scrub: 1,
          },
        }
      );
    });

    return () => ctx.revert();
  }, []);

  return (
    <section
      ref={sectionRef}
      id="how-it-works"
      className="relative py-32 bg-rock overflow-hidden"
    >
      {/* Background */}
      <div className="absolute inset-0">
        <div className="absolute top-0 left-0 right-0 h-32 bg-gradient-to-b from-shaft-500 to-transparent" />
      </div>

      <div className="relative z-10 max-w-7xl mx-auto px-6 lg:px-8">
        {/* Header */}
        <div className="text-center max-w-3xl mx-auto mb-20">
          <span className="inline-block text-barley text-sm font-medium tracking-widest uppercase mb-4">
            The Process
          </span>
          <h2 className="font-display text-4xl sm:text-5xl lg:text-6xl font-semibold text-shaft-500 mb-6 leading-tight">
            From Bean to
            <span className="text-barley italic"> Brilliant</span>
          </h2>
          <p className="text-shaft-400/70 text-lg leading-relaxed">
            Our three-step process is as refined as a pour-over ritual. 
            Simple, deliberate, and exceptionally effective.
          </p>
        </div>

        {/* Steps */}
        <div ref={stepsRef} className="relative">
          {/* Connecting Line - Desktop */}
          <div className="hidden lg:block absolute left-1/2 top-0 bottom-0 w-px bg-barley/20 -translate-x-1/2">
            <div className="connecting-line absolute inset-x-0 top-0 bg-barley origin-top" style={{ height: "100%" }} />
          </div>

          <div className="space-y-16 lg:space-y-24">
            {steps.map((step, index) => {
              const Icon = step.icon;
              const isEven = index % 2 === 0;
              
              return (
                <div
                  key={step.number}
                  className={`step-item relative grid lg:grid-cols-2 gap-8 lg:gap-16 items-center ${
                    isEven ? "" : "lg:direction-rtl"
                  }`}
                >
                  {/* Content */}
                  <div className={`${isEven ? "lg:pr-16 lg:text-right" : "lg:order-2 lg:pl-16"}`}>
                    <div className={`inline-flex items-center gap-3 mb-6 ${isEven ? "lg:flex-row-reverse" : ""}`}>
                      <span className="text-5xl font-display font-bold text-barley/20">
                        {step.number}
                      </span>
                      <div className="w-12 h-12 rounded-xl bg-barley/10 flex items-center justify-center">
                        <HugeiconsIcon icon={Icon} className="w-6 h-6 text-barley" />
                      </div>
                    </div>
                    
                    <h3 className="font-display text-3xl sm:text-4xl font-semibold text-shaft-500 mb-4">
                      {step.title}
                    </h3>
                    
                    <p className="text-shaft-400/70 text-lg leading-relaxed mb-6">
                      {step.description}
                    </p>

                    <ul className={`space-y-2 ${isEven ? "lg:text-right" : ""}`}>
                      {step.details.map((detail) => (
                        <li key={detail} className={`flex items-center gap-2 text-shaft-400/60 ${isEven ? "lg:justify-end lg:flex-row-reverse" : ""}`}>
                          <span className="w-1.5 h-1.5 rounded-full bg-barley" />
                          {detail}
                        </li>
                      ))}
                    </ul>
                  </div>

                  {/* Visual */}
                  <div className={`${isEven ? "lg:order-2" : ""}`}>
                    <div className="relative aspect-square max-w-md mx-auto">
                      {/* Background Circle */}
                      <div className="absolute inset-0 rounded-full bg-barley/5 border border-barley/10" />
                      
                      {/* Inner Content */}
                      <div className="absolute inset-8 rounded-full bg-gradient-to-br from-shaft-500 to-shaft-600 flex items-center justify-center shadow-2xl">
                        <HugeiconsIcon icon={Icon} className="w-20 h-20 text-barley/80" />
                      </div>

                      {/* Orbiting Elements */}
                      <div className="absolute inset-0 animate-spin" style={{ animationDuration: "20s" }}>
                        <div className="absolute top-0 left-1/2 -translate-x-1/2 -translate-y-1/2 w-4 h-4 rounded-full bg-barley shadow-lg shadow-barley/50" />
                      </div>
                      <div className="absolute inset-0 animate-spin" style={{ animationDuration: "15s", animationDirection: "reverse" }}>
                        <div className="absolute bottom-0 left-1/2 -translate-x-1/2 translate-y-1/2 w-3 h-3 rounded-full bg-akaroa-400 shadow-lg" />
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* CTA */}
        <div className="mt-20 text-center">
          <button 
            className="group inline-flex items-center gap-2 px-8 py-4 bg-barley text-shaft-500 font-semibold rounded-full transition-all duration-300 hover:shadow-xl hover:shadow-barley/20"
            data-cursor-hover
          >
            Start Your Journey
            <HugeiconsIcon icon={ArrowRight01Icon} className="w-5 h-5 transition-transform duration-300 group-hover:translate-x-1" />
          </button>
        </div>
      </div>
    </section>
  );
}
