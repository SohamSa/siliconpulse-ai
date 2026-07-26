import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        canvas: "#0b1220",
        panel: "#121a2b",
        accent: "#3d9cf0",
        warn: "#e3a008",
        danger: "#e35d6a",
        ok: "#3ecf8e",
      },
      fontFamily: {
        display: ["IBM Plex Sans", "Segoe UI", "sans-serif"],
        mono: ["IBM Plex Mono", "Consolas", "monospace"],
      },
    },
  },
  plugins: [],
};

export default config;
