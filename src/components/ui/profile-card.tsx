"use client";

import { ReactNode, useRef, useEffect } from "react";
import { Avatar, AvatarFallback, AvatarImage } from "./avatar";
import { cn } from "@/lib/utils";
import gsap from "gsap";

interface ProfileCardProps {
  name: string;
  role?: string;
  avatarUrl?: string;
  avatarFallback: string;
  stats?: Array<{
    label: string;
    value: string | number;
    icon?: ReactNode;
  }>;
  action?: ReactNode;
  className?: string;
  animate?: boolean;
}

export function ProfileCard({
  name,
  role,
  avatarUrl,
  avatarFallback,
  stats,
  action,
  className,
  animate = true,
}: ProfileCardProps) {
  const cardRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!animate || !cardRef.current) return;

    const ctx = gsap.context(() => {
      gsap.fromTo(
        cardRef.current,
        { opacity: 0, y: 16 },
        {
          opacity: 1,
          y: 0,
          duration: 0.4,
          ease: "power3.out",
        }
      );
    }, cardRef);

    return () => ctx.revert();
  }, [animate]);

  return (
    <div
      ref={cardRef}
      className={cn(
        "overflow-hidden rounded-xl border border-border bg-card shadow-card transition-all duration-200 hover:shadow-card-hover",
        className
      )}
    >
      {/* Header with avatar and name */}
      <div className="flex items-center justify-between p-4">
        <div className="flex items-center gap-3">
          <Avatar className="h-10 w-10 border border-border/50">
            <AvatarImage src={avatarUrl} alt={name} />
            <AvatarFallback className="bg-primary/10 text-primary text-sm font-medium">
              {avatarFallback}
            </AvatarFallback>
          </Avatar>
          <div>
            <h4 className="text-[14px] font-semibold text-foreground">{name}</h4>
            {role && (
              <p className="text-[12px] text-muted-foreground">{role}</p>
            )}
          </div>
        </div>
        {action}
      </div>

      {/* Stats row */}
      {stats && stats.length > 0 && (
        <div className="flex items-center justify-between border-t border-border px-4 py-3">
          {stats.map((stat, index) => (
            <div key={index} className="flex items-center gap-1.5">
              {stat.icon && (
                <span className="text-muted-foreground">{stat.icon}</span>
              )}
              <span className="text-[12px] text-muted-foreground">
                {stat.label}
              </span>
              <span className="text-[12px] font-semibold text-foreground">
                {stat.value}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

interface UserAvatarRowProps {
  users: Array<{
    name: string;
    avatarUrl?: string;
    avatarFallback: string;
  }>;
  maxVisible?: number;
  size?: "sm" | "md" | "lg";
  className?: string;
}

export function UserAvatarRow({
  users,
  maxVisible = 4,
  size = "md",
  className,
}: UserAvatarRowProps) {
  const visible = users.slice(0, maxVisible);
  const remaining = users.length - maxVisible;

  const sizeClasses = {
    sm: "h-6 w-6 text-[10px]",
    md: "h-8 w-8 text-xs",
    lg: "h-10 w-10 text-sm",
  };

  return (
    <div className={cn("flex items-center -space-x-2", className)}>
      {visible.map((user, index) => (
        <Avatar
          key={index}
          className={cn(
            sizeClasses[size],
            "border-2 border-card ring-0 transition-transform hover:z-10 hover:scale-110"
          )}
        >
          <AvatarImage src={user.avatarUrl} alt={user.name} />
          <AvatarFallback className="bg-primary/10 text-primary font-medium">
            {user.avatarFallback}
          </AvatarFallback>
        </Avatar>
      ))}
      {remaining > 0 && (
        <div
          className={cn(
            sizeClasses[size],
            "flex items-center justify-center rounded-full border-2 border-card bg-muted font-medium text-muted-foreground"
          )}
        >
          +{remaining}
        </div>
      )}
    </div>
  );
}
