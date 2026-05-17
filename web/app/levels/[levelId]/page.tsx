"use client";

import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { AlertTriangle, ArrowLeft, CheckCircle2, ChevronRight, Circle, Loader2, Lock, Send, ShieldCheck, Target, Terminal } from "lucide-react";
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

const familyColor: Record<string, string> = {
  Exfiltration: "border-ember/70 text-ember",
  Poisoning: "border-venom/70 text-venom",
  Structural: "border-signal/70 text-signal",
};

function defenseTags(levelId: string): string[] {
  const [, tierText] = levelId.split("-");
  const tier = Number(tierText);
  if (levelId.startsWith("exfil-")) {
    return [
      "Memory retrieval",
      ...(tier >= 2 ? ["Query intent filter"] : []),
      ...(tier >= 3 ? ["Output classifier"] : []),
      ...(tier >= 4 ? ["Retrieval redaction"] : []),
      ...(tier >= 5 ? ["Strict read defense"] : []),
    ];
  }

  if (levelId.startsWith("poison-")) {
    return [
      "Memory write path",
      ...(tier >= 2 ? ["Input filter"] : []),
      ...(tier >= 3 ? ["Write validator"] : []),
      ...(tier >= 4 ? ["Schema guard"] : []),
      ...(tier >= 5 ? ["Consolidation guard"] : []),
    ];
  }

  return ["Memory target"];
}

export default function LevelPage() {
  const params = useParams<{ levelId: string }>();
  const router = useRouter();
  const levelId = params.levelId;
  const [levels, setLevels] = useState<Level[]>([]);
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [progress, setProgress] = useState<ProgressState>(defaultProgress());
  const [prompt, setPrompt] = useState("");
  const [submittedAnswer, setSubmittedAnswer] = useState("");
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
  const isExfil = levelId.startsWith("exfil-");
  const canSubmit = Boolean(level && unlocked && (isExfil ? prompt.trim() || submittedAnswer.trim() : prompt.trim()));
  const trackLevels = useMemo(() => {
    const prefix = levelId.startsWith("poison-") ? "poison-" : levelId.startsWith("exfil-") ? "exfil-" : "";
    return prefix ? levels.filter((item) => item.id.startsWith(prefix)) : levels;
  }, [levelId, levels]);

  const nextLevel = useMemo(() => {
    if (!level) return undefined;
    return levels.find((item) => item.order > level.order);
  }, [level, levels]);

  function commitProgress(next: ProgressState) {
    setProgress(next);
    saveProgress(next);
  }

  async function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!canSubmit || submitting || !level || !unlocked) return;

    setSubmitting(true);
    setResult(null);
    const attemptNumber = attempts + 1;

    try {
      const response = await submitAttack({
        level_id: level.id,
        target,
        prompt: prompt.trim(),
        submitted_answer: isExfil ? submittedAnswer.trim() || null : null,
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
        <section className="mx-auto max-w-2xl rounded-2xl border border-line bg-panel p-8 text-center">
          <Lockout />
          <h1 className="mt-5 text-3xl font-semibold text-zinc-100">Level Locked</h1>
          <p className="mt-3 text-sm leading-6 text-zinc-400">Clear the previous breach or enable Practice Mode from the arena map.</p>
          <Link href="/" className="mt-6 inline-flex h-11 items-center justify-center rounded-lg border border-line px-5 text-sm text-zinc-200 hover:border-zinc-500">
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
        <div className="text-sm text-zinc-500">{target} live run</div>
      </div>

      <div className="grid gap-5 lg:grid-cols-[minmax(0,1fr)_360px]">
        <section className="space-y-5">
          <div className="rounded-2xl border border-line bg-panel p-5 md:p-6">
            <div className="flex flex-wrap items-center gap-3 text-xs font-semibold">
              <span className={`border px-2 py-1 ${familyColor[level?.family ?? ""] ?? "border-ember/70 text-ember"}`}>
                {level?.id.toUpperCase() ?? levelId.toUpperCase()}
              </span>
              <span className="text-zinc-500">{level?.family ?? "Challenge"}</span>
              <span className="text-zinc-500">{level?.difficulty ?? "Loading"}</span>
            </div>
            <h1 className="mt-5 text-4xl font-semibold text-zinc-50">{level?.title ?? "Loading challenge"}</h1>
            <p className="mt-4 max-w-3xl text-sm leading-6 text-zinc-400">{level?.briefing ?? "Fetching mission data..."}</p>
            <div className="mt-5 flex flex-wrap gap-2">
              {defenseTags(levelId).map((tag) => (
                <span key={tag} className="rounded-full border border-line bg-zinc-950 px-3 py-1 text-xs text-zinc-400">
                  {tag}
                </span>
              ))}
            </div>
          </div>

          <div className="rounded-2xl border border-line bg-panel p-5">
            <div className="mb-3 flex items-center gap-2 text-sm font-semibold text-zinc-300">
              <Target size={15} />
              Objective
            </div>
            <p className="text-lg text-zinc-100">{level?.objective}</p>
          </div>

          <form onSubmit={onSubmit} className="overflow-hidden rounded-2xl border border-line bg-panel">
            <div className="flex items-center justify-between border-b border-line px-5 py-4">
              <label htmlFor="prompt" className="flex items-center gap-2 text-sm font-semibold text-zinc-300">
                <Terminal size={16} />
                Attack Console
              </label>
              <span className="text-xs text-zinc-500">{attempts} previous attempts</span>
            </div>
            <div className="p-5">
            <textarea
              id="prompt"
              value={prompt}
              onChange={(event) => setPrompt(event.target.value)}
              minLength={1}
              maxLength={4000}
              rows={9}
              placeholder="Type the prompt you want the memory agent to process..."
              className="mt-3 w-full resize-y rounded-xl border border-line bg-zinc-950 p-4 text-sm leading-6 text-zinc-100 outline-none placeholder:text-zinc-600 focus:border-ember"
            />
            {isExfil ? (
              <div className="mt-4">
                <label htmlFor="submitted-answer" className="text-sm font-semibold text-zinc-300">
                  Answer Submission
                </label>
                <input
                  id="submitted-answer"
                  value={submittedAnswer}
                  onChange={(event) => setSubmittedAnswer(event.target.value)}
                  maxLength={4000}
                  placeholder="Enter the recovered token here..."
                  className="mt-3 h-12 w-full rounded-lg border border-line bg-zinc-950 px-4 text-sm text-zinc-100 outline-none placeholder:text-zinc-600 focus:border-ember"
                />
                <p className="mt-2 text-xs leading-5 text-zinc-500">
                  Exfiltration levels are scored from this answer field. The attack prompt is used to probe the protected memory system.
                </p>
              </div>
            ) : null}
            <div className="mt-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <div className="text-sm text-zinc-500">Target backend: {target}</div>
              <button
                type="submit"
                disabled={submitting || !canSubmit}
                className="inline-flex h-12 items-center justify-center gap-2 rounded-lg bg-ember px-6 text-sm font-semibold text-slate-950 hover:bg-sky-300 disabled:cursor-not-allowed disabled:bg-zinc-800 disabled:text-zinc-500"
              >
                {submitting ? <Loader2 className="animate-spin" size={17} /> : <Send size={17} />}
                {submitting ? "Running" : "Submit Attack"}
              </button>
            </div>
            </div>
          </form>

          {result ? (
            <section className={`rounded-2xl border p-5 ${result.success ? "border-signal/70 bg-signal/10" : "border-venom/70 bg-venom/10"}`}>
              <div className="flex items-start gap-3">
                {result.success ? <CheckCircle2 className="mt-1 text-signal" size={24} /> : <AlertTriangle className="mt-1 text-venom" size={24} />}
                <div className="flex-1">
                  <h2 className="text-2xl font-semibold text-zinc-100">{result.success ? "Success" : "Memory Response"}</h2>
                  <p className="mt-2 text-sm leading-6 text-zinc-300">{result.message}</p>

                  {result.agent_answer && (
                    <div className="mt-4 rounded-xl border border-line bg-zinc-950 p-4">
                      <div className="text-xs font-semibold text-zinc-500">Memory Response</div>
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
                <Link href={`/levels/${nextLevel.id}`} className="mt-5 inline-flex h-11 items-center justify-center rounded-lg bg-signal px-5 text-sm font-semibold text-black">
                  Next Level
                </Link>
              ) : null}
            </section>
          ) : null}
        </section>

        <aside className="space-y-4">
          <StatusStrip health={health} selectedTarget={target} />
          <div className="rounded-2xl border border-line bg-panel p-5">
            <div className="text-sm font-semibold text-zinc-300">Run State</div>
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

          <div className="rounded-2xl border border-line bg-panel p-5">
            <div className="mb-4 flex items-center gap-2 text-sm font-semibold text-zinc-300">
              <ShieldCheck size={16} />
              Track Progress
            </div>
            <div className="space-y-3">
              {trackLevels.map((item) => {
                const itemUnlocked = isUnlocked(progress, target, item.id);
                const itemComplete = targetProgress.completed.includes(item.id);
                const current = item.id === levelId;
                return (
                  <Link
                    key={item.id}
                    href={itemUnlocked ? `/levels/${item.id}` : "#"}
                    aria-disabled={!itemUnlocked}
                    className={`flex items-center gap-3 rounded-lg border p-3 transition ${
                      current ? "border-ember/80 bg-ember/10" : "border-line bg-zinc-950"
                    } ${itemUnlocked ? "hover:border-zinc-500" : "pointer-events-none opacity-50"}`}
                  >
                    {itemComplete ? (
                      <CheckCircle2 size={18} className="shrink-0 text-signal" />
                    ) : itemUnlocked ? (
                      <Circle size={18} className="shrink-0 text-zinc-500" />
                    ) : (
                      <Lock size={18} className="shrink-0 text-zinc-600" />
                    )}
                    <span className="min-w-0 flex-1">
                      <span className="block truncate text-sm font-semibold text-zinc-100">{item.title}</span>
                      <span className="block text-xs text-zinc-500">{item.difficulty}</span>
                    </span>
                    {current ? <ChevronRight size={16} className="text-ember" /> : null}
                  </Link>
                );
              })}
            </div>
          </div>
        </aside>
      </div>
    </Shell>
  );
}

function Lockout() {
  return <div className="mx-auto h-16 w-16 rounded-2xl border border-zinc-700 bg-zinc-950" />;
}
