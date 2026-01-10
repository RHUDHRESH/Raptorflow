import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

// 8px grid spacing utilities
export const spacing = {
  0: '0',
  1: '4px',  // Half unit for fine-tuning
  2: '8px',  // Base unit
  3: '12px',
  4: '16px',
  5: '20px',
  6: '24px',
  8: '32px',
  10: '40px',
  12: '48px',
  16: '64px',
  20: '80px',
  24: '96px',
} as const

export type SpacingValue = keyof typeof spacing

// Helper functions for consistent spacing
export const gap = (value: SpacingValue) => `gap-${value}`
export const p = (value: SpacingValue) => `p-${value}`
export const px = (value: SpacingValue) => `px-${value}`
export const py = (value: SpacingValue) => `py-${value}`
export const pt = (value: SpacingValue) => `pt-${value}`
export const pb = (value: SpacingValue) => `pb-${value}`
export const pl = (value: SpacingValue) => `pl-${value}`
export const pr = (value: SpacingValue) => `pr-${value}`
export const m = (value: SpacingValue) => `m-${value}`
export const mx = (value: SpacingValue) => `mx-${value}`
export const my = (value: SpacingValue) => `my-${value}`
export const mt = (value: SpacingValue) => `mt-${value}`
export const mb = (value: SpacingValue) => `mb-${value}`
export const ml = (value: SpacingValue) => `ml-${value}`
export const mr = (value: SpacingValue) => `mr-${value}`

// Common spacing patterns
export const spacingPatterns = {
  // Component spacing
  cardPadding: 'p-6',
  cardGap: 'gap-6',
  sectionPadding: 'py-12',
  containerPadding: 'px-6',

  // Element spacing
  buttonGap: 'gap-2',
  inputPadding: 'px-4 py-2',
  listItemPadding: 'py-3',

  // Layout spacing
  sidebarWidth: 'w-64',
  contentGap: 'gap-8',
  stackGap: 'gap-4',
  inlineGap: 'gap-2',
} as const
