"use client";

import * as React from "react";
import { Quote } from "lucide-react";

const testimonials = [
  {
    quote:
      "We cut our agency spend by ₹35,000/month and got better results. RaptorFlow tells us exactly what to do instead of asking us what we want.",
    name: "Raj Patel",
    role: "Founder",
    company: "Bansi Jewellery, Surat",
    metric: "₹35K/month saved",
  },
  {
    quote:
      "I finally know what my competitors are doing. Last week, RaptorFlow spotted a gap in their content strategy that we filled. Got 3 leads from that one article.",
    name: "Priya Sharma",
    role: "CEO",
    company: "TechStart, Bangalore",
    metric: "3 leads from 1 article",
  },
  {
    quote:
      "As a solo founder, I don't have time to become a marketer. RaptorFlow is like having a CMO who works while I sleep.",
    name: "Amit Kumar",
    role: "Founder",
    company: "CloudKitchen, Pune",
    metric: "Solo founder → 10x reach",
  },
];

export function LandingSocialProof() {
  return (
    <section className="py-20 bg-gray-50">
      <div className="mx-auto max-w-6xl px-6 lg:px-8">
        {/* Logos */}
        <div className="text-center mb-16">
          <p className="text-sm font-medium text-gray-500 uppercase tracking-wider mb-8">
            Trusted by founders at
          </p>
          <div className="flex flex-wrap justify-center items-center gap-8 lg:gap-16 opacity-50">
            {["Bansi Jewellery", "TechStart", "CloudKitchen", "MenuIQ", "Pricewell", "FoodOps"].map(
              (name) => (
                <div key={name} className="text-lg font-semibold text-gray-400">
                  {name}
                </div>
              ),
            )}
          </div>
        </div>

        {/* Testimonials */}
        <div className="grid md:grid-cols-3 gap-8">
          {testimonials.map((t, i) => (
            <div
              key={i}
              className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100 hover:shadow-md transition-shadow"
            >
              <Quote className="w-8 h-8 text-orange-200 mb-4" />

              <p className="text-gray-700 leading-relaxed mb-6">{t.quote}</p>

              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-full bg-gradient-to-br from-orange-400 to-orange-600" />
                <div>
                  <div className="font-semibold text-gray-900">{t.name}</div>
                  <div className="text-sm text-gray-500">
                    {t.role}, {t.company}
                  </div>
                </div>
              </div>

              <div className="inline-flex items-center px-3 py-1 rounded-full bg-green-50 text-green-700 text-sm font-medium">
                {t.metric}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
