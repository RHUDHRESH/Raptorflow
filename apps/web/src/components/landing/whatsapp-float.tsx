"use client";

import * as React from "react";
import { useRef, useState } from "react";
import { MessageCircle, X, ArrowRight, Zap, Shield, Clock, Users } from "lucide-react";

export function WhatsAppFloat() {
  const [isHovered, setIsHovered] = useState(false);
  const [showTooltip, setShowTooltip] = useState(false);

  React.useEffect(() => {
    const timer = setTimeout(() => setShowTooltip(true), 6000);
    const hideTimer = setTimeout(() => setShowTooltip(false), 10000);
    return () => {
      clearTimeout(timer);
      clearTimeout(hideTimer);
    };
  }, []);

  const handleClick = () => {
    window.open(
      "https://wa.me/919600570299?text=Hi%2C+I%27d+like+to+know+more+about+RaptorFlow+for+my+startup",
      "_blank",
      "noopener,noreferrer",
    );
  };

  return (
    <div className="fixed bottom-6 right-6 z-[999] flex flex-col items-end gap-3">
      {/* Tooltip */}
      {showTooltip && (
        <div
          className="bg-white rounded-2xl shadow-xl p-4 max-w-[280px] mb-2 relative animate-in slide-in-from-bottom-2 fade-in duration-300"
          style={{
            boxShadow: "0 20px 50px -12px rgba(0,0,0,0.25)",
          }}
        >
          <button
            onClick={() => setShowTooltip(false)}
            className="absolute top-2 right-2 text-gray-400 hover:text-gray-600"
          >
            <X className="w-4 h-4" />
          </button>
          <p className="text-sm font-medium text-gray-900 pr-6">
            Have questions? We reply in under 5 minutes.
          </p>
          <div className="flex items-center gap-1.5 mt-2">
            <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
            <span className="text-xs text-green-600 font-medium">Online now</span>
          </div>
        </div>
      )}

      {/* Button */}
      <button
        onClick={handleClick}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
        className="group relative flex items-center gap-3 bg-[#25D366] text-white pl-5 pr-6 py-4 rounded-full font-semibold text-sm shadow-lg hover:shadow-2xl transition-all duration-300 hover:scale-105 active:scale-95"
        style={{
          boxShadow: isHovered
            ? "0 20px 40px -10px rgba(37, 211, 102, 0.5)"
            : "0 10px 30px -10px rgba(37, 211, 102, 0.3)",
        }}
      >
        <div className="relative">
          <MessageCircle className="w-6 h-6" />
          <span className="absolute -top-1 -right-1 w-3 h-3 bg-white rounded-full border-2 border-[#25D366]" />
        </div>
        <span className="hidden sm:inline">Chat on WhatsApp</span>
        <ArrowRight
          className={`w-4 h-4 transition-transform duration-300 ${isHovered ? "translate-x-1" : ""}`}
        />
      </button>
    </div>
  );
}
