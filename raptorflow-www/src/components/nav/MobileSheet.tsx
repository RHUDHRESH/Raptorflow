"use client";

import { useState } from "react";
import Link from "next/link";
import { Menu, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet";

export function MobileSheet() {
  const [open, setOpen] = useState(false);

  return (
    <Sheet open={open} onOpenChange={setOpen}>
      <SheetTrigger asChild className="md:hidden">
        <Button variant="ghost" size="icon">
          <Menu className="h-6 w-6" />
        </Button>
      </SheetTrigger>
      <SheetContent side="right" className="bg-rf-card border-rf-mineshaft">
        <SheetHeader>
          <SheetTitle className="text-rf-ink">Menu</SheetTitle>
        </SheetHeader>
        <div className="mt-8 flex flex-col space-y-4">
          <Link
            href="#features"
            onClick={() => setOpen(false)}
            className="text-rf-subtle hover:text-rf-ink transition-colors py-2"
          >
            Features
          </Link>
          <Link
            href="#how-it-works"
            onClick={() => setOpen(false)}
            className="text-rf-subtle hover:text-rf-ink transition-colors py-2"
          >
            How It Works
          </Link>
          <Link
            href="#pricing"
            onClick={() => setOpen(false)}
            className="text-rf-subtle hover:text-rf-ink transition-colors py-2"
          >
            Pricing
          </Link>
          <Link
            href="/docs"
            onClick={() => setOpen(false)}
            className="text-rf-subtle hover:text-rf-ink transition-colors py-2"
          >
            Docs
          </Link>
          <div className="pt-4 space-y-3 border-t border-rf-mineshaft/50 mt-4">
            <Button
              variant="ghost"
              className="w-full text-rf-subtle hover:text-rf-ink"
              onClick={() => setOpen(false)}
            >
              Login
            </Button>
            <Button
              variant="default"
              className="bg-rf-accent hover:bg-rf-accent/90 w-full"
              onClick={() => setOpen(false)}
            >
              Sign Up
            </Button>
          </div>
        </div>
      </SheetContent>
    </Sheet>
  );
}

