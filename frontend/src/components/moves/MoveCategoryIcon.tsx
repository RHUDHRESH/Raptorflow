import { Zap, Magnet, Crown, Shield, Heart } from "lucide-react";
import { MoveCategory } from "./types";
import { cn } from "@/lib/utils";

interface MoveCategoryIconProps {
    category: MoveCategory;
    size?: number;
    className?: string;
}

export function MoveCategoryIcon({ category, size = 16, className }: MoveCategoryIconProps) {
    switch (category) {
        case 'ignite':
            return <Zap size={size} className={cn("text-amber-500", className)} />;
        case 'capture':
            return <Magnet size={size} className={cn("text-blue-500", className)} />;
        case 'authority':
            return <Crown size={size} className={cn("text-purple-500", className)} />;
        case 'repair':
            return <Shield size={size} className={cn("text-red-500", className)} />;
        case 'rally':
            return <Heart size={size} className={cn("text-pink-500", className)} />;
        default:
            return <Zap size={size} className={cn("text-[var(--muted)]", className)} />;
    }
}
