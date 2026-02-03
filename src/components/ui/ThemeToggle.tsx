"use client";

import { useState, useEffect } from "react";
import { Sun, Moon } from "lucide-react";

export function ThemeToggle() {
  const [isDark, setIsDark] = useState(false);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    // Check initial theme
    if (document.documentElement.classList.contains("dark")) {
      setIsDark(true);
    }
  }, []);

  const toggleTheme = () => {
    const newIsDark = !isDark;
    setIsDark(newIsDark);
    
    if (newIsDark) {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }
  };

  if (!mounted) {
    return (
      <button className="p-2 rounded-full bg-[var(--bg-tertiary)] text-[var(--text-primary)] w-10 h-10">
        <span className="sr-only">Toggle theme</span>
      </button>
    );
  }

  return (
    <button
      onClick={toggleTheme}
      className="relative p-2 rounded-full bg-[var(--bg-tertiary)] text-[var(--text-primary)] hover:bg-[var(--border-strong)] transition-colors w-10 h-10 flex items-center justify-center"
      aria-label={isDark ? "Switch to light mode" : "Switch to dark mode"}
    >
      <span className="sr-only">Toggle theme</span>
      <Sun 
        className={`w-5 h-5 transition-all duration-300 ${isDark ? "opacity-0 rotate-90 scale-0 absolute" : "opacity-100 rotate-0 scale-100"}`} 
      />
      <Moon 
        className={`w-5 h-5 transition-all duration-300 ${isDark ? "opacity-100 rotate-0 scale-100" : "opacity-0 -rotate-90 scale-0 absolute"}`} 
      />
    </button>
  );
}

export default ThemeToggle;
