"use client";

import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { AlertTriangle, ArrowLeft, CheckCircle2, Loader2, Send, Target } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { getHealth, getLevels, submitAttack, type AttackResponse, type HealthResponse, type Level } from "@/lib/api";
import {
  defaultProgress,
  isUnlocked,
  levelScore,
  loadProgress,
  saveProgress,
  type AttemptRecord,
  type ProgressState,
} from "@/lib/progress";
import { Shell } from "@/components/Shell";
import { StatusStrip } from "@/components/StatusStrip";

export default function LevelPage() {
  const params = useParams<{ levelId: string }>();
  const router = useRouter();
  const levelId = params.levelId;
  const [levels, setLevels] = useState<Level[]>([]);
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [progress, setProgress] = useState<ProgressState>(defaultProgress());
  const [prompt, setPrompt] = useState("");
  const [result, setResult] = useState<AttackResponse | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [clientReady, setClientReady] = useState(false);

  useEffect(() => {
    const loaded = loadProgress();
    setProgress(loaded);
    setClientReady(true);
    getLevels().then(setLevels).catch(() => setLevels([]));
    getHealth().then(setHealth).catch(() => setHealth(null));
  }, []);

  const level = levels.find((item) => item.id === levelId);
  const target = progress.selectedTarget;
  const targetProgress = progress.targets[target];
  const attempts = targetProgress.attempts[levelId] ?? 0;
  const unlocked = isUnlocked(progress, target, levelId);
  const completed = targetProgress.completed.includes(levelId);

  const nextLevel = useMemo(() => {
    const nextOrder = Number(levelId.slice(1)) + 1;
    return levels.find((item) => item.id === `l${nextOrder}`);
  }, [levelId, levels]);

  function commitProgress(next: ProgressState) {
    setProgress(next);
    saveProgress(next);
  }

  async function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!prompt.trim() || submitting || !level || !unlocked) return;

    setSubmitting(true);
    setResult(null);
    const attemptNumber = attempts + 1;

    try {
      const response = await submitAttack({
        level_id: level.id,
        target,
        prompt: prompt.trim(),
        session_id: progress.sessionId,
        attempt_number: attemptNumber,
      });

      const score = response.success ? levelScore(attemptNumber) : 0;
      const record: AttemptRecord = {
        levelId: level.id,
        target,
        prompt: prompt.trim(),
        success: response.success,
        message: response.message,
        agentAnswer: response.agent_answer,
        createdAt: new Date().toISOString(),
      };

      const currentTarget = progress.targets[target];
      const completedLevels = response.success && !currentTarget.completed.includes(level.id)
        ? [...currentTarget.completed, level.id]
        : currentTarget.completed;

      const nextProgress: ProgressState = {
        ...progress,
        targets: {
          ...progress.targets,
          [target]: {
            completed: completedLevels,
            attempts: { ...currentTarget.attempts, [level.id]: attemptNumber },
            bestScores: {
              ...currentTarget.bestScores,
              [level.id]: Math.max(currentTarget.bestScores[level.id] ?? 0, score),
            },
          },
        },
        recent: [record, ...progress.recent].slice(0, 20),
      };

      commitProgress(nextProgress);
      setResult(response);
    } catch (error) {
      setResult({
        success: false,
        level_id: level.id,
        target,
        message: "Backend connection failed.",
        agent_answer: null,
        diagnostics: [error instanceof Error ? error.message : "Unknown frontend error."],
      });
    } finally {
      setSubmitting(false);
    }
  }

  if (clientReady && level && !unlocked) {
    return (
      <Shell>
        <section className="mx-auto max-w-2xl border border-line bg-panel p-8 text-center">
          <Lockout />
          <h1 className="mt-5 text-3xl font-semibold text-zinc-100">Level Locked</h1>
          <p className="mt-3 text-sm leading-6 text-zinc-400">Clear the previous breach or enable Practice Mode from the arena map.</p>
          <Link href="/" className="mt-6 inline-flex h-11 items-center justify-center border border-line px-5 text-sm text-zinc-200 hover:border-zinc-500">
            Back to arena
          </Link>
        </section>
      </Shell>
    );
  }

  return (
    <Shell>
      <div className="mb-5 flex items-center justify-between">
        <Link href="/" className="inline-flex items-center gap-2 text-sm text-zinc-400 hover:text-zinc-100">
          <ArrowLeft size={16} />
          Arena
        </Link>
        <div className="text-sm uppercase tracking-[0.2em] text-zinc-500">{target} live run</div>
      </div>

      <div className="grid gap-6 lg:grid-cols-[1fr_360px]">
        <section className="space-y-5">
          <div className="border border-line bg-panel p-5">
            <div className="flex flex-wrap items-center gap-3">
              <span className="border border-ember/70 px-2 py-1 text-xs font-semibold uppercase tracking-[0.2em] text-ember">
                {level?.id.toUpperCase() ?? levelId.toUpperCase()}
              </span>
              <span className="text-xs uppercase tracking-[0.2em] text-zinc-500">{level?.family ?? "Challenge"}</span>
              <span className="text-xs uppercase tracking-[0.2em] text-zinc-500">{level?.difficulty ?? "Loading"}</span>
            </div>
            <h1 className="mt-5 text-4xl font-semibold text-zinc-50">{level?.title ?? "Loading challenge"}</h1>
            <p className="mt-4 max-w-3xl text-sm leading-6 text-zinc-400">{level?.briefing ?? "Fetching mission data..."}</p>
          </div>

          <div className="border border-line bg-panel p-5">
            <div className="mb-3 flex items-center gap-2 text-sm uppercase tracking-[0.22em] text-zinc-500">
              <Target size={15} />
              Objective
            </div>
            <p className="text-lg text-zinc-100">{level?.objective}</p>
          </div>

          <form onSubmit={onSubmit} className="border border-line bg-panel p-5">
            <label htmlFor="prompt" className="text-sm uppercase tracking-[0.22em] text-zinc-500">
              Attack Prompt
            </label>
            <textarea
              id="prompt"
              value={prompt}
              onChange={(event) => setPrompt(event.target.value)}
              minLength={1}
              maxLength={4000}
              rows={9}
              placeholder="Type the prompt you want the agent to process..."
              className="mt-3 w-full resize-y border border-line bg-zinc-950 p-4 text-sm leading-6 text-zinc-100 outline-none placeholder:text-zinc-600 focus:border-ember"
            />
            <div className="mt-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <div className="text-sm text-zinc-500">{attempts} previous attempts on {target}</div>
              <button
                type="submit"
                disabled={submitting || !prompt.trim() || !level}
                className="inline-flex h-12 items-center justify-center gap-2 bg-ember px-6 text-sm font-semibold uppercase tracking-[0.18em] text-white hover:bg-red-500 disabled:cursor-not-allowed disabled:bg-zinc-800 disabled:text-zinc-500"
              >
                {submitting ? <Loader2 className="animate-spin" size={17} /> : <Send size={17} />}
                {submitting ? "Running" : "Submit Attack"}
              </button>
            </div>
          </form>

          {result ? (
            <section className={`border p-5 ${result.success ? "border-signal/70 bg-signal/10" : "border-venom/70 bg-venom/10"}`}>
              <div className="flex items-start gap-3">
                {result.success ? <CheckCircle2 className="mt-1 text-signal" size={24} /> : <AlertTriangle className="mt-1 text-venom" size={24} />}
                <div className="flex-1">
                  <h2 className="text-2xl font-semibold text-zinc-100">{result.success ? "Compromised" : "Blocked"}</h2>
                  <p className="mt-2 text-sm leading-6 text-zinc-300">{result.message}</p>

                  {result.agent_answer && (
                    <div className="mt-4 border border-line bg-zinc-950 p-4">
                      <div className="text-xs uppercase tracking-[0.2em] text-zinc-500">Agent Reply</div>
                      <pre className="mt-3 whitespace-pre-wrap break-words text-sm leading-6 text-zinc-100">{result.agent_answer}</pre>
                    </div>
                  )}

                  {result.hint ? <p className="mt-3 text-sm text-venom">Hint: {result.hint}</p> : null}
                  {result.diagnostics.length ? (
                    <ul className="mt-3 space-y-1 text-sm text-zinc-300">
                      {result.diagnostics.map((item) => (
                        <li key={item}>{item}</li>
                      ))}
                    </ul>
                  ) : null}
                </div>
              </div>
              {result.success && nextLevel ? (
                <Link href={`/levels/${nextLevel.id}`} className="mt-5 inline-flex h-11 items-center justify-center bg-signal px-5 text-sm font-semibold uppercase tracking-[0.18em] text-black">
                  Next Level
                </Link>
              ) : null}
            </section>
          ) : null}
        </section>

        <aside className="space-y-4">
          <StatusStrip health={health} selectedTarget={target} />
          <div className="border border-line bg-panel p-5">
            <div className="text-sm uppercase tracking-[0.22em] text-zinc-500">Run State</div>
            <div className="mt-4 space-y-3 text-sm">
              <div className="flex justify-between border-b border-line pb-2">
                <span className="text-zinc-500">Target</span>
                <span className="font-semibold text-zinc-100">{target}</span>
              </div>
              <div className="flex justify-between border-b border-line pb-2">
                <span className="text-zinc-500">Attempts</span>
                <span className="font-semibold text-zinc-100">{attempts}</span>
              </div>
              <div className="flex justify-between border-b border-line pb-2">
                <span className="text-zinc-500">Best score</span>
                <span className="font-semibold text-zinc-100">{targetProgress.bestScores[levelId] ?? 0}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-zinc-500">Status</span>
                <span className={completed ? "font-semibold text-signal" : "font-semibold text-zinc-100"}>{completed ? "Cleared" : "Open"}</span>
              </div>
            </div>
          </div>
        </aside>
      </div>
    </Shell>
  );
}

function Lockout() {
  return <div className="mx-auto h-16 w-16 border border-zinc-700 bg-zinc-950" />;
}
