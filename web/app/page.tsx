"use client";

import Link from "next/link";
import { CheckCircle2, ChevronRight, Circle, Lock, Play, RotateCcw, ShieldCheck, Swords, Terminal, Unlock } from "lucide-react";
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

const tracks = [
  {
    id: "exfil",
    label: "Memory Leakage",
    family: "Exfiltration",
    accent: "ember",
    description: "Recover protected memory through increasingly hardened read paths.",
  },
  {
    id: "poison",
    label: "Memory Injection",
    family: "Poisoning",
    accent: "venom",
    description: "Plant false memory while write filters, validators, and schema guards evolve.",
  },
] as const;

export default function HomePage() {
  const [levels, setLevels] = useState<Level[]>([]);
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [progress, setProgress] = useState<ProgressState>(defaultProgress());
  const [activeTrackId, setActiveTrackId] = useState<(typeof tracks)[number]["id"]>("exfil");

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
  const activeTrack = tracks.find((track) => track.id === activeTrackId) ?? tracks[0];
  const trackLevels = useMemo(
    () => levels.filter((level) => level.id.startsWith(`${activeTrackId}-`)),
    [activeTrackId, levels],
  );
  const activeLevel = useMemo(() => {
    return (
      trackLevels.find((level) => isUnlocked(progress, progress.selectedTarget, level.id) && !targetProgress.completed.includes(level.id)) ??
      trackLevels.find((level) => isUnlocked(progress, progress.selectedTarget, level.id)) ??
      trackLevels[0]
    );
  }, [progress, targetProgress.completed, trackLevels]);
  const activeAttempts = activeLevel ? targetProgress.attempts[activeLevel.id] ?? 0 : 0;
  const activeScore = activeLevel ? targetProgress.bestScores[activeLevel.id] ?? 0 : 0;

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
      <div className="grid gap-5 lg:grid-cols-[minmax(0,1fr)_340px]">
        <section className="space-y-5">
          <div className="border border-line bg-panel p-5 md:p-6">
            <div className="flex flex-col gap-5 xl:flex-row xl:items-start xl:justify-between">
              <div className="max-w-3xl">
                <div className="mb-3 inline-flex items-center gap-2 text-sm font-semibold text-ember">
                  <Swords size={16} />
                  Live Memory Attack CTF
                </div>
                <h1 className="text-4xl font-semibold text-zinc-50 md:text-5xl">Break the memory layer.</h1>
                <p className="mt-4 max-w-2xl text-sm leading-6 text-zinc-400">
                  Choose a live backend, attack the current defense tier, and clear each track by extracting or corrupting protected memory.
                </p>
              </div>
              <div className="grid min-w-full grid-cols-2 border border-line sm:min-w-[280px]">
                {(["mem0", "hindsight"] as TargetName[]).map((target) => (
                  <button
                    key={target}
                    onClick={() => setTarget(target)}
                    className={`h-11 px-4 text-sm font-semibold ${
                      progress.selectedTarget === target ? "bg-ember text-white" : "bg-zinc-950 text-zinc-400 hover:text-zinc-100"
                    }`}
                  >
                    {target}
                  </button>
                ))}
              </div>
            </div>
          </div>

          <StatusStrip health={health} selectedTarget={progress.selectedTarget} />

          <div className="grid gap-4 md:grid-cols-2">
            {tracks.map((track) => {
              const trackCount = levels.filter((level) => level.id.startsWith(`${track.id}-`)).length;
              const cleared = targetProgress.completed.filter((levelId) => levelId.startsWith(`${track.id}-`)).length;
              const active = track.id === activeTrackId;
              return (
                <button
                  key={track.id}
                  onClick={() => setActiveTrackId(track.id)}
                  className={`border bg-panel p-5 text-left transition hover:border-zinc-500 ${
                    active ? "border-ember/80 shadow-glow" : "border-line"
                  }`}
                >
                  <div className="flex items-center justify-between gap-3">
                    <span className={`border px-2 py-1 text-xs font-semibold ${familyColor[track.family]}`}>{track.family}</span>
                    <span className="text-sm text-zinc-500">
                      {cleared}/{trackCount || 5} clear
                    </span>
                  </div>
                  <h2 className="mt-4 text-2xl font-semibold text-zinc-100">{track.label}</h2>
                  <p className="mt-2 text-sm leading-6 text-zinc-400">{track.description}</p>
                </button>
              );
            })}
          </div>

          <div className="grid gap-5 xl:grid-cols-[minmax(0,1fr)_320px]">
            <section className="border border-line bg-panel p-5 md:p-6">
              <div className="flex flex-wrap items-center gap-3">
                <span className={`border px-2 py-1 text-xs font-semibold ${familyColor[activeTrack.family]}`}>
                  {activeTrack.family}
                </span>
                <span className="text-sm text-zinc-500">{activeLevel?.difficulty ?? "Loading"}</span>
              </div>
              <h2 className="mt-5 text-3xl font-semibold text-zinc-50 md:text-4xl">{activeLevel?.title ?? "Loading challenge"}</h2>
              <p className="mt-4 max-w-2xl text-sm leading-6 text-zinc-400">{activeLevel?.briefing ?? "Fetching live mission data..."}</p>
              <div className="mt-6 border border-line bg-zinc-950 p-4">
                <div className="mb-2 flex items-center gap-2 text-sm font-semibold text-zinc-300">
                  <Terminal size={16} />
                  Objective
                </div>
                <p className="text-sm leading-6 text-zinc-100">{activeLevel?.objective ?? "Waiting for backend."}</p>
              </div>
              <div className="mt-5 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                <div className="grid grid-cols-2 gap-3 text-sm sm:min-w-[260px]">
                  <div className="border border-line bg-zinc-950 p-3">
                    <div className="font-semibold text-zinc-100">{activeAttempts}</div>
                    <div className="text-zinc-500">Attempts</div>
                  </div>
                  <div className="border border-line bg-zinc-950 p-3">
                    <div className="font-semibold text-zinc-100">{activeScore}</div>
                    <div className="text-zinc-500">Best score</div>
                  </div>
                </div>
                <Link
                  href={activeLevel ? `/levels/${activeLevel.id}` : "#"}
                  className="inline-flex h-12 items-center justify-center gap-2 bg-ember px-6 text-sm font-semibold text-white hover:bg-red-500"
                >
                  <Play size={17} />
                  Enter Challenge
                </Link>
              </div>
            </section>

            <section className="border border-line bg-panel p-5">
              <div className="mb-4 flex items-center gap-2 text-sm font-semibold text-zinc-300">
                <ShieldCheck size={16} />
                Defense Ladder
              </div>
              <div className="space-y-3">
                {trackLevels.map((level) => {
                  const unlocked = isUnlocked(progress, progress.selectedTarget, level.id);
                  const complete = targetProgress.completed.includes(level.id);
                  const current = activeLevel?.id === level.id;
                  return (
                    <Link
                      key={level.id}
                      href={unlocked ? `/levels/${level.id}` : "#"}
                      aria-disabled={!unlocked}
                      className={`flex items-center gap-3 border p-3 transition ${
                        current ? "border-ember/80 bg-ember/10" : "border-line bg-zinc-950"
                      } ${unlocked ? "hover:border-zinc-500" : "pointer-events-none opacity-50"}`}
                    >
                      {complete ? (
                        <CheckCircle2 size={18} className="shrink-0 text-signal" />
                      ) : unlocked ? (
                        <Unlock size={18} className="shrink-0 text-zinc-500" />
                      ) : (
                        <Lock size={18} className="shrink-0 text-zinc-600" />
                      )}
                      <span className="min-w-0 flex-1">
                        <span className="block truncate text-sm font-semibold text-zinc-100">{level.title}</span>
                        <span className="block text-xs text-zinc-500">{level.difficulty}</span>
                      </span>
                      {current ? <ChevronRight size={16} className="text-ember" /> : null}
                    </Link>
                  );
                })}
                {!trackLevels.length ? <p className="text-sm text-zinc-500">No levels returned by the backend.</p> : null}
              </div>
            </section>
          </div>

          <section className="grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
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
                  className={`border bg-panel p-4 transition ${
                    unlocked ? "border-line hover:border-zinc-500" : "pointer-events-none border-zinc-900 opacity-45"
                  }`}
                >
                  <div className="flex items-center justify-between gap-3">
                    <span className="text-xs font-semibold text-zinc-500">{level.id.toUpperCase()}</span>
                    {complete ? <CheckCircle2 size={16} className="text-signal" /> : unlocked ? <Circle size={16} className="text-zinc-500" /> : <Lock size={16} className="text-zinc-600" />}
                  </div>
                  <h3 className="mt-3 line-clamp-2 min-h-[44px] text-base font-semibold text-zinc-100">{level.title}</h3>
                  <div className="mt-4 flex items-center justify-between text-xs">
                    <span className={complete ? "text-signal" : "text-zinc-500"}>{complete ? "Cleared" : level.difficulty}</span>
                    <span className="text-zinc-500">{attempts} attempts · {score} pts</span>
                  </div>
                </Link>
              );
            })}
          </section>
        </section>

        <aside className="space-y-4">
          <div className="border border-line bg-panel p-5">
            <div className="text-sm font-semibold text-zinc-300">Operator</div>
            <div className="mt-4 grid grid-cols-2 gap-3">
              <div className="border border-line bg-zinc-950 p-3">
                <div className="text-2xl font-semibold text-zinc-100">{targetProgress.completed.length}/{levels.length}</div>
                <div className="text-xs text-zinc-500">Cleared</div>
              </div>
              <div className="border border-line bg-zinc-950 p-3">
                <div className="text-2xl font-semibold text-zinc-100">{totalScore}</div>
                <div className="text-xs text-zinc-500">Score</div>
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
