import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{js,ts,jsx,tsx}", "./components/**/*.{js,ts,jsx,tsx}", "./lib/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        panel: "#101114",
        line: "#24272f",
        ember: "#ff3b3b",
        venom: "#f4b13d",
        signal: "#29d7ff",
      },
      boxShadow: {
        glow: "0 0 36px rgba(255, 59, 59, 0.18)",
      },
    },
  },
  plugins: [],
};

export default config;
