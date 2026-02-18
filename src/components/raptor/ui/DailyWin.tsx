"use client";

import React, { useRef, useEffect } from "react";
import { gsap } from "gsap";

interface DailyWinProps {
  title: string;
  description: string;
  impact: "high" | "medium" | "low";
  completed?: boolean;
  onComplete?: () => void;
  onDismiss?: () => void;
}

export function DailyWin({
  title,
  description,
  impact,
  completed = false,
  onComplete,
  onDismiss,
}: DailyWinProps) {
  const cardRef = useRef<HTMLDivElement>(null);
  const checkboxRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    if (!cardRef.current) return;

    // Entrance animation
    gsap.fromTo(
      cardRef.current,
      { opacity: 0, x: -20 },
      { opacity: 1, x: 0, duration: 0.4, ease: "power2.out" }
    );
  }, []);

  useEffect(() => {
    if (!checkboxRef.current || !completed) return;

    // Celebration animation on complete
    gsap.to(checkboxRef.current, {
      scale: 1.2,
      duration: 0.15,
      yoyo: true,
      repeat: 1,
      ease: "power2.out",
    });
  }, [completed]);

  const getImpactStyles = () => {
    switch (impact) {
      case "high":
        return "border-l-2 border-l-[#D4A853] bg-[#F5F0E6]";
      case "medium":
        return "border-l-2 border-l-[#D2CCC0] bg-[#F7F5EF]";
      case "low":
        return "border-l-2 border-l-[#E3DED3] bg-[#EFEDE6]";
      default:
        return "";
    }
  };

  const getImpactLabel = () => {
    switch (impact) {
      case "high":
        return "High Impact";
      case "medium":
        return "Medium";
      case "low":
        return "Low";
      default:
        return "";
    }
  };

  const getImpactDotColor = () => {
    switch (impact) {
      case "high":
        return "bg-[#D4A853]";
      case "medium":
        return "bg-[#5C565B]";
      case "low":
        return "bg-[#847C82]";
      default:
        return "bg-[#847C82]";
    }
  };

  return (
    <div
      ref={cardRef}
      className={`
        relative p-4 rounded-[10px] border border-[#E3DED3]
        ${getImpactStyles()}
        ${completed ? "opacity-60" : "opacity-100"}
        transition-opacity duration-200
      `}
    >
      <div className="flex items-start gap-3">
        {/* Checkbox */}
        <button
          ref={checkboxRef}
          onClick={onComplete}
          className={`
            flex-shrink-0 w-5 h-5 rounded-[6px] border-2 flex items-center justify-center
            transition-colors duration-200
            ${
              completed
                ? "bg-[#2A2529] border-[#2A2529]"
                : "bg-transparent border-[#D2CCC0] hover:border-[#2A2529]"
            }
          `}
          aria-label={completed ? "Mark as incomplete" : "Mark as complete"}
        >
          {completed && (
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="12"
              height="12"
              viewBox="0 0 24 24"
              fill="none"
              stroke="#F3F0E7"
              strokeWidth="3"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <polyline points="20 6 9 17 4 12" />
            </svg>
          )}
        </button>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <h4
              className={`
                text-[14px] font-semibold text-[#2A2529] font-['DM_Sans',system-ui,sans-serif]
                ${completed ? "line-through text-[#847C82]" : ""}
              `}
            >
              {title}
            </h4>
            {impact === "high" && (
              <span className="flex-shrink-0">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="14"
                  height="14"
                  viewBox="0 0 24 24"
                  fill="#D4A853"
                  stroke="#D4A853"
                  strokeWidth="1.5"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" />
                </svg>
              </span>
            )}
          </div>

          <p className="text-[12px] text-[#847C82] font-['DM_Sans',system-ui,sans-serif] line-clamp-2">
            {description}
          </p>

          <div className="mt-2 flex items-center gap-1.5">
            <span className={`w-1.5 h-1.5 rounded-full ${getImpactDotColor()}`} />
            <span className="text-[10px] font-medium text-[#847C82] font-['JetBrains_Mono',monospace] uppercase tracking-wide">
              {getImpactLabel()}
            </span>
          </div>
        </div>

        {/* Dismiss button */}
        {onDismiss && (
          <button
            onClick={onDismiss}
            className="flex-shrink-0 p-1 text-[#847C82] hover:text-[#2A2529] hover:bg-[#F3F0E7] rounded-[6px] transition-colors"
            aria-label="Dismiss"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="14"
              height="14"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <line x1="18" y1="6" x2="6" y2="18" />
              <line x1="6" y1="6" x2="18" y2="18" />
            </svg>
          </button>
        )}
      </div>
    </div>
  );
}
