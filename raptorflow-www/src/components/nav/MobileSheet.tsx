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
            className="text-rf-subtle hover:text-rf-ink transition-colors"
          >
            Features
          </Link>
          <Link
            href="#pricing"
            onClick={() => setOpen(false)}
            className="text-rf-subtle hover:text-rf-ink transition-colors"
          >
            Pricing
          </Link>
          <Button
            variant="default"
            className="bg-rf-accent hover:bg-rf-accent/90 mt-4"
            onClick={() => setOpen(false)}
          >
            Get started
          </Button>
        </div>
      </SheetContent>
    </Sheet>
  );
}

