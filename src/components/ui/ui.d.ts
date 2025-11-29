import React from 'react';
import * as PopoverPrimitive from "@radix-ui/react-popover";

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'default' | 'destructive' | 'outline' | 'secondary' | 'ghost' | 'link';
  size?: 'default' | 'sm' | 'lg' | 'icon';
}
export const Button: React.ForwardRefExoticComponent<ButtonProps & React.RefAttributes<HTMLButtonElement>>;

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {}
export const Input: React.ForwardRefExoticComponent<InputProps & React.RefAttributes<HTMLInputElement>>;

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {}
export const Card: React.ForwardRefExoticComponent<CardProps & React.RefAttributes<HTMLDivElement>>;

export interface CardHeaderProps extends React.HTMLAttributes<HTMLDivElement> {}
export const CardHeader: React.ForwardRefExoticComponent<CardHeaderProps & React.RefAttributes<HTMLDivElement>>;

export interface CardTitleProps extends React.HTMLAttributes<HTMLHeadingElement> {}
export const CardTitle: React.ForwardRefExoticComponent<CardTitleProps & React.RefAttributes<HTMLHeadingElement>>;

export interface CardDescriptionProps extends React.HTMLAttributes<HTMLParagraphElement> {}
export const CardDescription: React.ForwardRefExoticComponent<CardDescriptionProps & React.RefAttributes<HTMLParagraphElement>>;

export interface CardContentProps extends React.HTMLAttributes<HTMLDivElement> {}
export const CardContent: React.ForwardRefExoticComponent<CardContentProps & React.RefAttributes<HTMLDivElement>>;

export interface CardFooterProps extends React.HTMLAttributes<HTMLDivElement> {}
export const CardFooter: React.ForwardRefExoticComponent<CardFooterProps & React.RefAttributes<HTMLDivElement>>;

export const Popover: typeof PopoverPrimitive.Root;
export const PopoverTrigger: typeof PopoverPrimitive.Trigger;
export const PopoverContent: React.ForwardRefExoticComponent<PopoverPrimitive.PopoverContentProps & React.RefAttributes<HTMLDivElement>>;
