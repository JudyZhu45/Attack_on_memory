"use client";

import Link from "next/link";
import { ArrowLeft, Trophy } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { Shell } from "@/components/Shell";
import { defaultProgress, loadProgress, type ProgressState } from "@/lib/progress";

export default function ResultsPage() {
  const [progress, setProgress] = useState<ProgressState>(defaultProgress());

  useEffect(() => {
    setProgress(loadProgress());
  }, []);

  const totals = useMemo(() => {
    return (["mem0", "hindsight"] as const).map((target) => {
      const targetProgress = progress.targets[target];
      return {
        target,
        completed: targetProgress.completed.length,
        score: Object.values(targetProgress.bestScores).reduce((sum, value) => sum + value, 0),
        attempts: Object.values(targetProgress.attempts).reduce((sum, value) => sum + value, 0),
      };
    });
  }, [progress]);

  return (
    <Shell>
      <Link href="/" className="mb-5 inline-flex items-center gap-2 text-sm text-zinc-400 hover:text-zinc-100">
        <ArrowLeft size={16} />
        Arena
      </Link>

      <section className="rounded-2xl border border-line bg-panel p-6">
        <div className="flex items-center gap-3 text-sm uppercase tracking-[0.24em] text-venom">
          <Trophy size={18} />
          Local Scoreboard
        </div>
        <h1 className="mt-4 text-4xl font-semibold text-zinc-50">Breach Record</h1>
        <p className="mt-3 text-sm leading-6 text-zinc-400">Progress is stored only in this browser. Live target memory state is not shown here.</p>
      </section>

      <div className="mt-6 grid gap-4 md:grid-cols-2">
        {totals.map((item) => (
          <section key={item.target} className="rounded-2xl border border-line bg-panel p-5">
            <div className="text-sm uppercase tracking-[0.22em] text-zinc-500">{item.target}</div>
            <div className="mt-5 grid grid-cols-3 gap-3">
              <Metric label="Cleared" value={`${item.completed}/5`} />
              <Metric label="Score" value={String(item.score)} />
              <Metric label="Attempts" value={String(item.attempts)} />
            </div>
          </section>
        ))}
      </div>

      <section className="mt-6 rounded-2xl border border-line bg-panel p-5">
        <div className="text-sm uppercase tracking-[0.22em] text-zinc-500">Recent Attempts</div>
        {progress.recent.length ? (
          <div className="mt-4 divide-y divide-line">
            {progress.recent.map((item) => (
              <div key={`${item.createdAt}-${item.levelId}-${item.target}`} className="grid gap-2 py-3 text-sm md:grid-cols-[90px_110px_1fr_110px]">
                <span className="font-semibold uppercase text-zinc-100">{item.levelId}</span>
                <span className="text-zinc-500">{item.target}</span>
                <span className="min-w-0">
                  <span className="block truncate text-zinc-400">{item.prompt}</span>
                  {item.agentAnswer ? <span className="mt-1 block truncate text-zinc-600">Agent: {item.agentAnswer}</span> : null}
                </span>
                <span className={item.success ? "text-signal" : "text-venom"}>{item.success ? "Compromised" : "Blocked"}</span>
              </div>
            ))}
          </div>
        ) : (
          <p className="mt-4 text-sm text-zinc-500">No attempts yet.</p>
        )}
      </section>
    </Shell>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border border-line bg-zinc-950 p-4">
      <div className="text-2xl font-semibold text-zinc-100">{value}</div>
      <div className="mt-1 text-xs uppercase tracking-[0.18em] text-zinc-500">{label}</div>
    </div>
  );
}
