import * as React from "react";

import { useIsMobile } from "@/hooks/use-mobile";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Drawer,
  DrawerContent,
  DrawerDescription,
  DrawerHeader,
  DrawerTitle,
} from "@/components/ui/drawer";
import { cn } from "@/lib/utils";

const DialogAny = Dialog as unknown as React.ComponentType<any>;
const DialogContentAny = DialogContent as unknown as React.ComponentType<any>;
const DialogHeaderAny = DialogHeader as unknown as React.ComponentType<any>;
const DialogTitleAny = DialogTitle as unknown as React.ComponentType<any>;
const DialogDescriptionAny = DialogDescription as unknown as React.ComponentType<any>;

const DrawerAny = Drawer as unknown as React.ComponentType<any>;
const DrawerContentAny = DrawerContent as unknown as React.ComponentType<any>;
const DrawerHeaderAny = DrawerHeader as unknown as React.ComponentType<any>;
const DrawerTitleAny = DrawerTitle as unknown as React.ComponentType<any>;
const DrawerDescriptionAny = DrawerDescription as unknown as React.ComponentType<any>;

export function Modal({
  open,
  onOpenChange,
  title,
  description,
  children,
  contentClassName,
  desktopOnly,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  title: string;
  description?: string;
  children: React.ReactNode;
  contentClassName?: string;
  desktopOnly?: boolean;
}) {
  const isMobile = useIsMobile();

  if (isMobile && !desktopOnly) {
    return React.createElement(
      DrawerAny as any,
      { open, onOpenChange },
      React.createElement(
        DrawerContentAny as any,
        { className: cn("bg-card border-border", contentClassName) },
        React.createElement(
          DrawerHeaderAny as any,
          { className: "text-left" },
          React.createElement(
            DrawerTitleAny as any,
            { className: "font-serif text-headline-sm text-foreground" },
            title,
          ),
          description
            ? React.createElement(
                DrawerDescriptionAny as any,
                { className: "text-body-sm text-muted-foreground" },
                description,
              )
            : null,
        ),
        React.createElement("div", { className: "px-4 pb-4" }, children),
      ),
    );
  }

  return React.createElement(
    DialogAny as any,
    { open, onOpenChange },
    React.createElement(
      DialogContentAny as any,
      { className: cn("bg-card border-border", contentClassName) },
      React.createElement(
        DialogHeaderAny as any,
        null,
        React.createElement(
          DialogTitleAny as any,
          { className: "font-serif text-headline-sm text-foreground" },
          title,
        ),
        description
          ? React.createElement(
              DialogDescriptionAny as any,
              { className: "text-body-sm text-muted-foreground" },
              description,
            )
          : null,
      ),
      children,
    ),
  );
}
