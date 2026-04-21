"use client";

import * as React from "react";
import { useRef } from "react";
import gsap from "gsap";
import { useGSAP } from "@gsap/react";
import { MessageCircle } from "lucide-react";

export function WhatsAppFloat() {
  const buttonRef = useRef<HTMLAnchorElement>(null);

  useGSAP(
    () => {
      const mm = gsap.matchMedia();

      mm.add("(prefers-reduced-motion: reduce)", () => {
        gsap.set(".whatsapp-float", { opacity: 1, scale: 1 });
      });

      mm.add("(min-width: 0px)", () => {
        gsap.from(".whatsapp-float", {
          scale: 0,
          opacity: 0,
          duration: 0.5,
          ease: "back.out(1.5)",
          delay: 4,
        });

        gsap.to(".whatsapp-float", {
          scale: 1.06,
          duration: 0.3,
          ease: "power2.inOut",
          yoyo: true,
          repeat: 1,
          delay: 8,
          repeatDelay: 8,
        });
      });

      return () => mm.revert();
    },
    { scope: buttonRef },
  );

  return (
    <a
      ref={buttonRef}
      href="https://wa.me/919600570299?text=Hi%2C+I%27d+like+to+know+more+about+RaptorFlow+for+my+startup"
      target="_blank"
      rel="noopener noreferrer"
      className="whatsapp-float fixed bottom-7 right-7 z-[999] flex items-center gap-2 bg-[#25D366] text-white px-5 py-3 rounded-full font-semibold text-[13px] shadow-lg hover:shadow-xl transition-shadow"
    >
      <MessageCircle className="w-[18px] h-[18px]" />
      <span>Chat with us</span>
    </a>
  );
}
