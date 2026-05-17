import Link from "next/link";
import { Shield, Trophy } from "lucide-react";

export function Shell({ children }: { children: React.ReactNode }) {
  return (
    <main className="mx-auto flex min-h-screen w-full max-w-7xl flex-col px-4 py-5 sm:px-6 lg:px-8">
      <header className="mb-6 flex items-center justify-between border-b border-line pb-4">
        <Link href="/" className="flex items-center gap-3">
          <span className="flex h-10 w-10 items-center justify-center border border-ember/60 bg-ember/10 text-ember shadow-glow">
            <Shield size={20} />
          </span>
          <span>
            <span className="block text-sm uppercase tracking-[0.28em] text-zinc-500">AgentMemoryCTF</span>
            <span className="block text-lg font-semibold text-zinc-100">Memory Breach Arena</span>
          </span>
        </Link>
        <Link
          href="/results"
          className="inline-flex h-10 items-center gap-2 border border-line bg-panel px-3 text-sm text-zinc-200 hover:border-zinc-500"
        >
          <Trophy size={16} />
          Results
        </Link>
      </header>
      {children}
    </main>
  );
}
