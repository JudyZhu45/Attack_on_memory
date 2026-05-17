import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AgentMemoryCTF",
  description: "A live CTF for attacking agent memory systems.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body className="scanlines">{children}</body>
    </html>
  );
}
