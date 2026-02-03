"use client";

import { useEffect, useRef, useState } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { Quote, ChevronLeft, ChevronRight, Star } from "lucide-react";

const testimonials = [
  {
    quote: "RaptorFlow transformed how we think about marketing. It's not just a tool—it's our strategic compass. We went from random acts of marketing to a cohesive system.",
    author: "Sarah Chen",
    role: "CEO, TechStart AI",
    company: "YC W24",
    rating: 5,
    image: "SC",
  },
  {
    quote: "In 6 weeks, we built a marketing foundation that would've taken 6 months traditionally. The AI-powered positioning exercises alone were worth 10x the price.",
    author: "Marcus Johnson",
    role: "Founder, GrowthLabs",
    company: "Series A",
    rating: 5,
    image: "MJ",
  },
  {
    quote: "Finally, a marketing platform that thinks like a founder. RaptorFlow helps us move fast without breaking things. Our team is aligned and executing like never before.",
    author: "Elena Rodriguez",
    role: "CMO, Nexus Health",
    company: "Seed Stage",
    rating: 5,
    image: "ER",
  },
  {
    quote: "We tried every marketing tool out there. RaptorFlow is the first one that actually delivers on the promise of 'strategy meets execution.' It's a game-changer.",
    author: "David Park",
    role: "Co-founder, DataSync",
    company: "Bootstrapped",
    rating: 5,
    image: "DP",
  },
];

export function Testimonials() {
  const sectionRef = useRef<HTMLDivElement>(null);
  const [activeIndex, setActiveIndex] = useState(0);

  useEffect(() => {
    if (!sectionRef.current) return;

    const ctx = gsap.context(() => {
      gsap.fromTo(
        ".testimonials-title",
        { y: 50, opacity: 0 },
        {
          y: 0,
          opacity: 1,
          duration: 0.8,
          ease: "power3.out",
          scrollTrigger: {
            trigger: ".testimonials-title",
            start: "top 80%",
            toggleActions: "play none none reverse",
          },
        }
      );

      gsap.fromTo(
        ".testimonial-card",
        { y: 60, opacity: 0, scale: 0.95 },
        {
          y: 0,
          opacity: 1,
          scale: 1,
          duration: 0.8,
          ease: "power3.out",
          scrollTrigger: {
            trigger: ".testimonial-card",
            start: "top 80%",
            toggleActions: "play none none reverse",
          },
        }
      );
    }, sectionRef);

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
      className="relative py-32 overflow-hidden"
    >
      {/* Background */}
      <div className="absolute inset-0 bg-gradient-to-b from-transparent via-blue-900/5 to-transparent" />

      <div className="relative z-10 max-w-7xl mx-auto px-6 lg:px-8">
        {/* Section Header */}
        <div className="testimonials-title text-center mb-16">
          <span className="inline-block px-4 py-2 rounded-full bg-pink-500/10 border border-pink-500/20 text-pink-300 text-sm font-medium tracking-wide mb-6">
            Testimonials
          </span>
          <h2 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-white mb-6">
            Loved by{" "}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-pink-400 to-purple-400">
              Founders
            </span>
          </h2>
          <p className="text-lg text-white/60 max-w-2xl mx-auto">
            See what visionary founders are saying about their RaptorFlow journey.
          </p>
        </div>

        {/* Testimonial Carousel */}
        <div className="testimonial-card relative max-w-4xl mx-auto">
          {/* Main Card */}
          <div className="relative p-8 md:p-12 rounded-3xl bg-white/[0.03] border border-white/[0.08] backdrop-blur-sm">
            {/* Quote Icon */}
            <div className="absolute -top-6 left-8 md:left-12">
              <div className="p-4 rounded-2xl bg-gradient-to-br from-purple-500 to-blue-500 shadow-lg shadow-purple-500/25">
                <Quote className="w-6 h-6 text-white" />
              </div>
            </div>

            {/* Stars */}
            <div className="flex items-center gap-1 mb-6 pt-4">
              {Array.from({ length: testimonials[activeIndex].rating }).map((_, i) => (
                <Star key={i} className="w-5 h-5 text-amber-400 fill-amber-400" />
              ))}
            </div>

            {/* Quote */}
            <blockquote className="text-xl md:text-2xl text-white/90 leading-relaxed mb-8 transition-opacity duration-500">
              "{testimonials[activeIndex].quote}"
            </blockquote>

            {/* Author */}
            <div className="flex items-center gap-4">
              <div className="w-14 h-14 rounded-full bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center text-white font-bold text-lg">
                {testimonials[activeIndex].image}
              </div>
              <div>
                <div className="text-white font-semibold text-lg">
                  {testimonials[activeIndex].author}
                </div>
                <div className="text-white/50">
                  {testimonials[activeIndex].role}
                </div>
                <div className="text-purple-400 text-sm">
                  {testimonials[activeIndex].company}
                </div>
              </div>
            </div>
          </div>

          {/* Navigation */}
          <div className="flex items-center justify-center gap-4 mt-8">
            <button
              onClick={prevTestimonial}
              className="p-3 rounded-full border border-white/10 text-white/60 hover:bg-white/5 hover:text-white transition-all duration-300"
            >
              <ChevronLeft className="w-5 h-5" />
            </button>

            {/* Dots */}
            <div className="flex items-center gap-2">
              {testimonials.map((_, index) => (
                <button
                  key={index}
                  onClick={() => setActiveIndex(index)}
                  className={`w-2 h-2 rounded-full transition-all duration-300 ${
                    index === activeIndex
                      ? "w-8 bg-gradient-to-r from-purple-500 to-blue-500"
                      : "bg-white/20 hover:bg-white/40"
                  }`}
                />
              ))}
            </div>

            <button
              onClick={nextTestimonial}
              className="p-3 rounded-full border border-white/10 text-white/60 hover:bg-white/5 hover:text-white transition-all duration-300"
            >
              <ChevronRight className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mt-20">
          {[
            { value: "500+", label: "Founders Onboarded" },
            { value: "10M+", label: "Campaigns Executed" },
            { value: "3x", label: "Average ROI Increase" },
            { value: "20min", label: "Setup Time" },
          ].map((stat, index) => (
            <div
              key={index}
              className="text-center p-6 rounded-2xl bg-white/[0.02] border border-white/[0.05]"
            >
              <div className="text-3xl md:text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-blue-400 mb-2">
                {stat.value}
              </div>
              <div className="text-white/50 text-sm">{stat.label}</div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
