import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

/**
 * Fixes garbled UTF-8 strings that were incorrectly decoded as latin-1.
 * This commonly happens with accented names (e.g., "MarÃ­a" → "María")
 * returned by Keycloak when the user comes from an LDAP/AD source.
 */
export function fixEncodingIssue(str: string): string {
  try {
    return decodeURIComponent(escape(str));
  } catch {
    return str;
  }
}
