import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        hydropi: {
          950: "#021e3d",
          900: "#033C73",
          800: "#074d8f",
          700: "#0A5FAA",
          600: "#1271c2",
          500: "#1A82D6",
          400: "#47a3e8",
          300: "#7BBFEF",
          200: "#b0d9f7",
          100: "#D6EEFF",
          50:  "#f0f8ff",
        },
        sensor: {
          ok:    "#16a34a",
          alert: "#dc2626",
          warn:  "#d97706",
        },
      },
      fontFamily: {
        display: ['"DM Serif Display"', "Georgia", "serif"],
        body:    ['"Inter"', "system-ui", "sans-serif"],
      },
      boxShadow: {
        card: "0 1px 3px rgba(3,60,115,0.08), 0 4px 12px rgba(3,60,115,0.07), 0 0 0 1px rgba(3,60,115,0.06)",
        "card-hover": "0 4px 16px rgba(3,60,115,0.14), 0 2px 6px rgba(3,60,115,0.09), 0 0 0 1px rgba(3,60,115,0.07)",
        glow: "0 0 20px 0 rgba(26,130,214,0.25)",
        "btn-primary": "0 1px 3px rgba(3,60,115,0.30), 0 2px 8px -2px rgba(26,130,214,0.25)",
      },
    },
  },
  plugins: [],
} satisfies Config;
