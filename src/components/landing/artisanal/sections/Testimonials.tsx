"use client";

import { useEffect, useRef, useState } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { HugeiconsIcon } from "@hugeicons/react";
import {
  Quote01Icon,
  StarIcon,
  ArrowLeft01Icon,
  ArrowRight01Icon
} from "@hugeicons/core-free-icons";

const testimonials = [
  {
    quote: "RaptorFlow transformed how we handle content operations. It's like having a master craftsman orchestrating every piece of our workflow.",
    author: "Sarah Chen",
    role: "Head of Content",
    company: "Notion",
    rating: 5,
    avatar: "SC",
  },
  {
    quote: "The attention to detail is remarkable. Every automation feels intentional, every connection meaningful. Pure workflow poetry.",
    author: "Marcus Rodriguez",
    role: " CTO",
    company: "Linear",
    rating: 5,
    avatar: "MR",
  },
  {
    quote: "We evaluated dozens of tools. RaptorFlow was the only one that felt like it was crafted, not just built. The difference is palpable.",
    author: "Emma Watson",
    role: "VP of Operations",
    company: "Figma",
    rating: 5,
    avatar: "EW",
  },
  {
    quote: "From setup to scale, the experience has been exceptional. Our team saves 20+ hours every week on manual tasks.",
    author: "James Park",
    role: "Founder",
    company: "Vercel",
    rating: 5,
    avatar: "JP",
  },
];

export function Testimonials() {
  const sectionRef = useRef<HTMLDivElement>(null);
  const [activeIndex, setActiveIndex] = useState(0);
  const cardsRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!sectionRef.current) return;

    const ctx = gsap.context(() => {
      gsap.fromTo(
        ".testimonials-header",
        { y: 60, opacity: 0 },
        {
          y: 0,
          opacity: 1,
          duration: 0.8,
          ease: "power3.out",
          scrollTrigger: {
            trigger: sectionRef.current,
            start: "top 80%",
            toggleActions: "play none none none",
          },
        }
      );

      gsap.fromTo(
        ".testimonial-card",
        { y: 40, opacity: 0, scale: 0.95 },
        {
          y: 0,
          opacity: 1,
          scale: 1,
          duration: 0.7,
          stagger: 0.15,
          ease: "power3.out",
          scrollTrigger: {
            trigger: cardsRef.current,
            start: "top 80%",
            toggleActions: "play none none none",
          },
        }
      );
    });

    return () => ctx.revert();
  }, []);

  const nextTestimonial = () => {
    setActiveIndex((prev) => (prev + 1) % testimonials.length);
  };

  const prevTestimonial = () => {
    setActiveIndex((prev) => (prev - 1 + testimonials.length) % testimonials.length);
  };

  return (
    <section
      ref={sectionRef}
      className="relative py-32 bg-shaft-500 overflow-hidden"
    >
      {/* Background */}
      <div className="absolute inset-0">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-barley/5 rounded-full blur-[150px]" />
      </div>

      <div className="relative z-10 max-w-7xl mx-auto px-6 lg:px-8">
        {/* Header */}
        <div className="testimonials-header text-center max-w-3xl mx-auto mb-16">
          <span className="inline-block text-barley text-sm font-medium tracking-widest uppercase mb-4">
            Testimonials
          </span>
          <h2 className="font-display text-4xl sm:text-5xl lg:text-6xl font-semibold text-rock mb-6 leading-tight">
            Loved by Teams Who
            <span className="text-barley italic"> Appreciate Craft</span>
          </h2>
        </div>

        {/* Desktop Grid */}
        <div ref={cardsRef} className="hidden lg:grid grid-cols-2 gap-6">
          {testimonials.map((testimonial, index) => (
            <div
              key={index}
              className="testimonial-card group relative p-8 rounded-2xl bg-shaft-400/20 border border-barley/5 hover:border-barley/20 transition-all duration-500"
              data-cursor-hover
            >
              {/* Quote Icon */}
              <HugeiconsIcon icon={QuoteDownIcon} className="w-10 h-10 text-barley/20 mb-6" />

              {/* Stars */}
              <div className="flex gap-1 mb-4">
                {[...Array(testimonial.rating)].map((_, i) => (
                  <HugeiconsIcon key={i} icon={StarIcon} className="w-4 h-4 text-barley fill-barley" />
                ))}
              </div>

              {/* Quote */}
              <p className="text-rock/80 text-lg leading-relaxed mb-8">
                "{testimonial.quote}"
              </p>

              {/* Author */}
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-full bg-barley/20 flex items-center justify-center text-barley font-medium">
                  {testimonial.avatar}
                </div>
                <div>
                  <p className="text-rock font-medium">{testimonial.author}</p>
                  <p className="text-akaroa-200/50 text-sm">
                    {testimonial.role} at {testimonial.company}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Mobile Carousel */}
        <div className="lg:hidden">
          <div className="relative overflow-hidden">
            <div
              className="flex transition-transform duration-500 ease-out"
              style={{ transform: `translateX(-${activeIndex * 100}%)` }}
            >
              {testimonials.map((testimonial, index) => (
                <div
                  key={index}
                  className="w-full flex-shrink-0 px-4"
                >
                  <div className="p-6 rounded-2xl bg-shaft-400/20 border border-barley/10">
                    <HugeiconsIcon icon={QuoteDownIcon} className="w-8 h-8 text-barley/20 mb-4" />
                    <div className="flex gap-1 mb-4">
                      {[...Array(testimonial.rating)].map((_, i) => (
                        <StarIcon key={i} className="w-4 h-4 text-barley fill-barley" variant="solid" />
                      ))}
                    </div>
                    <p className="text-rock/80 text-base leading-relaxed mb-6">
                      "{testimonial.quote}"
                    </p>
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-full bg-barley/20 flex items-center justify-center text-barley text-sm font-medium">
                        {testimonial.avatar}
                      </div>
                      <div>
                        <p className="text-rock font-medium text-sm">{testimonial.author}</p>
                        <p className="text-akaroa-200/50 text-xs">
                          {testimonial.role} at {testimonial.company}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Navigation */}
          <div className="flex items-center justify-center gap-4 mt-8">
            <button
              onClick={prevTestimonial}
              className="p-3 rounded-full bg-shaft-400/30 text-rock hover:bg-barley/20 hover:text-barley transition-colors duration-300"
              data-cursor-hover
            >
              <HugeiconsIcon icon={ArrowLeft01Icon} className="w-5 h-5" />
            </button>

            <div className="flex gap-2">
              {testimonials.map((_, index) => (
                <button
                  key={index}
                  onClick={() => setActiveIndex(index)}
                  className={`w-2 h-2 rounded-full transition-all duration-300 ${
                    index === activeIndex ? "bg-barley w-6" : "bg-rock/20"
                  }`}
                />
              ))}
            </div>

            <button
              onClick={nextTestimonial}
              className="p-3 rounded-full bg-shaft-400/30 text-rock hover:bg-barley/20 hover:text-barley transition-colors duration-300"
              data-cursor-hover
            >
              <HugeiconsIcon icon={ArrowRight01Icon} className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>
    </section>
  );
}
