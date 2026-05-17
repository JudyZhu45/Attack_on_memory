"use client";

import Link from "next/link";
import { Lock, Play, RotateCcw, Swords, Unlock } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { getHealth, getLevels, type HealthResponse, type Level, type TargetName } from "@/lib/api";
import { defaultProgress, isUnlocked, loadProgress, saveProgress, type ProgressState } from "@/lib/progress";
import { Shell } from "@/components/Shell";
import { StatusStrip } from "@/components/StatusStrip";

const familyColor: Record<string, string> = {
  Memorization: "border-signal/70 text-signal",
  Exfiltration: "border-ember/70 text-ember",
  Poisoning: "border-venom/70 text-venom",
  Structural: "border-signal/70 text-signal",
};

export default function HomePage() {
  const [levels, setLevels] = useState<Level[]>([]);
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [progress, setProgress] = useState<ProgressState>(defaultProgress());

  useEffect(() => {
    setProgress(loadProgress());
    getLevels().then(setLevels).catch(() => setLevels([]));
    getHealth().then(setHealth).catch(() => setHealth(null));
  }, []);

  const targetProgress = progress.targets[progress.selectedTarget];
  const totalScore = useMemo(
    () => Object.values(targetProgress.bestScores).reduce((sum, score) => sum + score, 0),
    [targetProgress.bestScores],
  );

  function updateProgress(next: ProgressState) {
    setProgress(next);
    saveProgress(next);
  }

  function setTarget(target: TargetName) {
    updateProgress({ ...progress, selectedTarget: target });
  }

  function resetLocal() {
    const fresh = defaultProgress();
    setProgress(fresh);
    saveProgress(fresh);
  }

  return (
    <Shell>
      <div className="grid gap-6 lg:grid-cols-[1fr_320px]">
        <section>
          <div className="mb-5 flex flex-col justify-between gap-4 border border-line bg-panel p-5 md:flex-row md:items-end">
            <div>
              <div className="mb-2 inline-flex items-center gap-2 text-sm uppercase tracking-[0.24em] text-ember">
                <Swords size={16} />
                Live Memory Attack CTF
              </div>
              <h1 className="max-w-3xl text-4xl font-semibold text-zinc-50 md:text-5xl">Break the agent before it remembers too much.</h1>
              <p className="mt-3 max-w-2xl text-sm leading-6 text-zinc-400">
                Pick a live memory backend and clear two escalating defense tracks: leakage and injection.
              </p>
            </div>
            <div className="grid grid-cols-2 border border-line">
              {(["mem0", "hindsight"] as TargetName[]).map((target) => (
                <button
                  key={target}
                  onClick={() => setTarget(target)}
                  className={`h-11 px-4 text-sm font-semibold uppercase tracking-[0.16em] ${
                    progress.selectedTarget === target ? "bg-ember text-white" : "bg-zinc-950 text-zinc-400 hover:text-zinc-100"
                  }`}
                >
                  {target}
                </button>
              ))}
            </div>
          </div>

          <StatusStrip health={health} selectedTarget={progress.selectedTarget} />

          <div className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {levels.map((level) => {
              const unlocked = isUnlocked(progress, progress.selectedTarget, level.id);
              const complete = targetProgress.completed.includes(level.id);
              const attempts = targetProgress.attempts[level.id] ?? 0;
              const score = targetProgress.bestScores[level.id] ?? 0;
              return (
                <Link
                  key={level.id}
                  href={unlocked ? `/levels/${level.id}` : "#"}
                  aria-disabled={!unlocked}
                  className={`level-link min-h-[220px] border bg-panel p-5 transition ${
                    unlocked ? "border-line hover:-translate-y-1 hover:border-zinc-500" : "pointer-events-none border-zinc-900 opacity-45"
                  }`}
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className={`border px-2 py-1 text-xs font-semibold uppercase tracking-[0.18em] ${familyColor[level.family]}`}>
                      {level.family}
                    </div>
                    {unlocked ? <Unlock size={18} className="text-zinc-500" /> : <Lock size={18} className="text-zinc-600" />}
                  </div>
                  <div className="mt-7 text-sm uppercase tracking-[0.24em] text-zinc-500">{level.id.toUpperCase()}</div>
                  <h2 className="mt-2 text-2xl font-semibold text-zinc-100">{level.title}</h2>
                  <p className="mt-3 line-clamp-2 text-sm leading-6 text-zinc-400">{level.briefing}</p>
                  <div className="mt-5 flex items-center justify-between text-sm">
                    <span className={complete ? "text-signal" : "text-zinc-500"}>{complete ? "Cleared" : level.difficulty}</span>
                    <span className="text-zinc-500">{attempts} attempts · {score} pts</span>
                  </div>
                </Link>
              );
            })}
          </div>
        </section>

        <aside className="space-y-4">
          <div className="border border-line bg-panel p-5">
            <div className="text-sm uppercase tracking-[0.22em] text-zinc-500">Operator</div>
            <div className="mt-4 grid grid-cols-2 gap-3">
              <div className="border border-line bg-zinc-950 p-3">
                <div className="text-2xl font-semibold text-zinc-100">{targetProgress.completed.length}/{levels.length}</div>
                <div className="text-xs uppercase tracking-[0.18em] text-zinc-500">Cleared</div>
              </div>
              <div className="border border-line bg-zinc-950 p-3">
                <div className="text-2xl font-semibold text-zinc-100">{totalScore}</div>
                <div className="text-xs uppercase tracking-[0.18em] text-zinc-500">Score</div>
              </div>
            </div>
          </div>

          <label className="flex cursor-pointer items-center justify-between border border-line bg-panel p-4">
            <span>
              <span className="block text-sm font-semibold text-zinc-100">Practice Mode</span>
              <span className="block text-xs text-zinc-500">Unlock all levels locally.</span>
            </span>
            <input
              type="checkbox"
              checked={progress.practiceMode}
              onChange={(event) => updateProgress({ ...progress, practiceMode: event.target.checked })}
              className="h-5 w-5 accent-red-500"
            />
          </label>

          <button
            onClick={resetLocal}
            className="flex h-11 w-full items-center justify-center gap-2 border border-line bg-zinc-950 text-sm text-zinc-300 hover:border-ember hover:text-white"
          >
            <RotateCcw size={16} />
            Reset Local Progress
          </button>

          <Link href={levels.length ? `/levels/${levels.find((level) => isUnlocked(progress, progress.selectedTarget, level.id) && !targetProgress.completed.includes(level.id))?.id ?? "exfil-1"}` : "#"} className="flex h-12 items-center justify-center gap-2 bg-ember text-sm font-semibold uppercase tracking-[0.18em] text-white hover:bg-red-500">
            <Play size={17} />
            Continue
          </Link>
        </aside>
      </div>
    </Shell>
  );
}
