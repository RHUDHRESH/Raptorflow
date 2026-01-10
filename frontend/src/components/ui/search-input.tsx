"use client";

import { forwardRef, useState } from "react";
import { Search, Command } from "lucide-react";
import { cn } from "@/lib/utils";

interface SearchInputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  showShortcut?: boolean;
  shortcutKey?: string;
  variant?: "default" | "sidebar";
}

export const SearchInput = forwardRef<HTMLInputElement, SearchInputProps>(
  ({ className, showShortcut = true, shortcutKey = "S", variant = "default", ...props }, ref) => {
    const [isFocused, setIsFocused] = useState(false);

    return (
      <div
        className={cn(
          "group relative flex items-center transition-all duration-200",
          variant === "sidebar" && "w-full",
          className
        )}
      >
        {/* Search icon */}
        <Search
          className={cn(
            "absolute left-3 h-4 w-4 transition-colors duration-200",
            isFocused ? "text-primary" : "text-muted-foreground"
          )}
        />

        {/* Input */}
        <input
          ref={ref}
          type="search"
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
          className={cn(
            "h-10 w-full rounded-xl border bg-card pl-10 pr-4 text-sm text-foreground transition-all duration-200",
            "placeholder:text-muted-foreground",
            "focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary/40",
            isFocused ? "border-primary/40" : "border-border",
            showShortcut && "pr-16",
            variant === "sidebar" && "bg-muted/50 border-transparent hover:bg-muted"
          )}
          {...props}
        />

        {/* Keyboard shortcut badge */}
        {showShortcut && !isFocused && (
          <div className="absolute right-3 flex items-center gap-1 pointer-events-none">
            <kbd className="flex h-5 items-center gap-0.5 rounded border border-border bg-muted px-1.5 text-[10px] font-medium text-muted-foreground">
              <Command className="h-2.5 w-2.5" />
              {shortcutKey}
            </kbd>
          </div>
        )}
      </div>
    );
  }
);

SearchInput.displayName = "SearchInput";
