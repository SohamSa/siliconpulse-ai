/**
 * Product brand constants for SiliconPulse AI.
 * Full UI lands in Phase 6; this file proves TypeScript/Vitest wiring.
 */
export const PRODUCT_NAME = "SiliconPulse AI" as const;

export const HEALTHCARE_DISCLAIMER =
  "This module is a simulated device-monitoring demonstration. It is not a medical diagnostic system and must not be used for patient-care decisions." as const;

export function formatProductTitle(page: string): string {
  const trimmed = page.trim();
  if (!trimmed) {
    return PRODUCT_NAME;
  }
  return `${PRODUCT_NAME} · ${trimmed}`;
}
