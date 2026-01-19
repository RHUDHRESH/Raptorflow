import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

/**
 * Generates a Unique Customer ID in the format RF-YYYY-XXXX
 * @param sequenceNumber The numeric sequence for the user
 * @returns Formatted UCID string
 */
/**
 * Generates a Unique Customer ID in the format RF-YYYY-XXXX
 * @param sequenceNumber The numeric sequence for the user
 * @returns Formatted UCID string
 */
export function generateUCID(sequenceNumber: number): string {
  const year = new Date().getFullYear();
  const sequenceStr = sequenceNumber.toString().padStart(4, '0');
  return `RF-${year}-${sequenceStr}`;
}
