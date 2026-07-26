import { describe, expect, it } from "vitest";
import {
  HEALTHCARE_DISCLAIMER,
  PRODUCT_NAME,
  formatProductTitle,
} from "./brand";

describe("brand", () => {
  it("exposes the product name", () => {
    expect(PRODUCT_NAME).toBe("SiliconPulse AI");
  });

  it("formats page titles", () => {
    expect(formatProductTitle("Fleet")).toBe("SiliconPulse AI · Fleet");
    expect(formatProductTitle("  ")).toBe("SiliconPulse AI");
  });

  it("includes a non-diagnostic healthcare disclaimer", () => {
    expect(HEALTHCARE_DISCLAIMER.toLowerCase()).toContain("not a medical");
    expect(HEALTHCARE_DISCLAIMER.toLowerCase()).toContain("simulated");
  });
});
