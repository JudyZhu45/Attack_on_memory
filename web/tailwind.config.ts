import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{js,ts,jsx,tsx}", "./components/**/*.{js,ts,jsx,tsx}", "./lib/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        panel: "#101419",
        line: "#26303a",
        ember: "#38bdf8",
        venom: "#a78bfa",
        signal: "#34d399",
      },
      boxShadow: {
        glow: "0 0 36px rgba(56, 189, 248, 0.16)",
      },
    },
  },
  plugins: [],
};

export default config;
