"use client";

import { useEffect, useRef, useState } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { HugeiconsIcon } from "@hugeicons/react";
import { 
  PlusSignIcon,
  MinusSignIcon,
  HelpCircleIcon
} from "@hugeicons/core-free-icons";

const faqs = [
  {
    question: "What makes RaptorFlow different from other automation tools?",
    answer: "RaptorFlow combines the precision of enterprise-grade automation with the warmth of artisanal craftsmanship. Unlike rigid, code-heavy platforms, we offer an intuitive visual experience that feels as natural as sketching on paper. Every interaction is deliberate, every animation purposeful.",
  },
  {
    question: "How long does it take to set up my first workflow?",
    answer: "Most users create their first working automation within 15 minutes. Our templates get you started instantly, and the visual builder means no coding required. Complex enterprise workflows typically take a few hours to perfect — not weeks.",
  },
  {
    question: "Can I integrate with my existing tools?",
    answer: "Absolutely. RaptorFlow connects with 200+ popular tools including Slack, Notion, Salesforce, HubSpot, Google Workspace, and many more. We also support custom webhooks and APIs for proprietary systems.",
  },
  {
    question: "Is my data secure?",
    answer: "Security is woven into every layer of RaptorFlow. We use bank-grade AES-256 encryption, are SOC 2 Type II certified, and GDPR compliant. Enterprise plans include dedicated infrastructure and advanced security features like SSO and audit logs.",
  },
  {
    question: "What happens if I exceed my execution limits?",
    answer: "We never stop your workflows mid-stream. If you approach your limit, we'll notify you and offer seamless upgrades. Additional executions are billed at fair overage rates, or you can upgrade your plan instantly.",
  },
  {
    question: "Do you offer refunds?",
    answer: "Yes. If RaptorFlow isn't the perfect blend for your needs, contact us within 30 days for a full refund — no questions asked. We believe in earning your loyalty through exceptional product experience, not lock-ins.",
  },
];

export function FAQ() {
  const sectionRef = useRef<HTMLDivElement>(null);
  const [openIndex, setOpenIndex] = useState<number | null>(0);

  useEffect(() => {
    if (!sectionRef.current) return;

    const ctx = gsap.context(() => {
      gsap.fromTo(
        ".faq-header",
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
        ".faq-item",
        { y: 30, opacity: 0 },
        {
          y: 0,
          opacity: 1,
          duration: 0.5,
          stagger: 0.1,
          ease: "power3.out",
          scrollTrigger: {
            trigger: ".faq-list",
            start: "top 80%",
            toggleActions: "play none none none",
          },
        }
      );
    });

    return () => ctx.revert();
  }, []);

  const toggleFaq = (index: number) => {
    setOpenIndex(openIndex === index ? null : index);
  };

  return (
    <section
      ref={sectionRef}
      id="faq"
      className="relative py-32 bg-shaft-500 overflow-hidden"
    >
      <div className="relative z-10 max-w-4xl mx-auto px-6 lg:px-8">
        {/* Header */}
        <div className="faq-header text-center max-w-2xl mx-auto mb-16">
          <span className="inline-block text-barley text-sm font-medium tracking-widest uppercase mb-4">
            FAQ
          </span>
          <h2 className="font-display text-4xl sm:text-5xl lg:text-6xl font-semibold text-rock mb-6 leading-tight">
            Questions Worth
            <span className="text-barley italic"> Answering</span>
          </h2>
          <p className="text-akaroa-200/60 text-lg leading-relaxed">
            Everything you need to know about brewing the perfect workflow.
          </p>
        </div>

        {/* FAQ List */}
        <div className="faq-list space-y-4">
          {faqs.map((faq, index) => (
            <div
              key={index}
              className="faq-item rounded-2xl bg-shaft-400/20 border border-barley/5 overflow-hidden transition-all duration-300 hover:border-barley/20"
            >
              <button
                onClick={() => toggleFaq(index)}
                className="w-full flex items-center justify-between p-6 text-left"
                data-cursor-hover
              >
                <div className="flex items-center gap-4 pr-4">
                  <div className="w-10 h-10 rounded-lg bg-barley/10 flex items-center justify-center flex-shrink-0">
                    <HugeiconsIcon icon={HelpCircleIcon} className="w-5 h-5 text-barley" />
                  </div>
                  <span className="font-display text-lg text-rock">
                    {faq.question}
                  </span>
                </div>
                <div className={`w-8 h-8 rounded-full bg-barley/10 flex items-center justify-center flex-shrink-0 transition-all duration-300 ${
                  openIndex === index ? "bg-barley rotate-180" : ""
                }`}>
                  {openIndex === index ? (
                    <HugeiconsIcon icon={MinusSignIcon} className={`w-4 h-4 ${openIndex === index ? "text-shaft-500" : "text-barley"}`} />
                  ) : (
                    <HugeiconsIcon icon={PlusSignIcon} className="w-4 h-4 text-barley" />
                  )}
                </div>
              </button>
              
              <div
                className={`overflow-hidden transition-all duration-500 ease-out ${
                  openIndex === index ? "max-h-96" : "max-h-0"
                }`}
              >
                <div className="px-6 pb-6 pl-20">
                  <p className="text-akaroa-200/60 leading-relaxed">
                    {faq.answer}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Contact CTA */}
        <div className="mt-16 text-center p-8 rounded-2xl bg-barley/5 border border-barley/10">
          <p className="text-rock mb-4">Still have questions?</p>
          <button 
            className="text-barley font-medium hover:underline"
            data-cursor-hover
          >
            Chat with our team — we respond within minutes
          </button>
        </div>
      </div>
    </section>
  );
}
