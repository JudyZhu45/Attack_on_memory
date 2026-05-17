import type { TargetName } from "./api";

export type AttemptRecord = {
  levelId: string;
  target: TargetName;
  prompt: string;
  success: boolean;
  message: string;
  agentAnswer?: string | null;
  createdAt: string;
};

export type TargetProgress = {
  completed: string[];
  attempts: Record<string, number>;
  bestScores: Record<string, number>;
};

export type ProgressState = {
  sessionId: string;
  selectedTarget: TargetName;
  practiceMode: boolean;
  targets: Record<TargetName, TargetProgress>;
  recent: AttemptRecord[];
};

const STORAGE_KEY = "agent-memory-ctf-progress";
const TARGETS: TargetName[] = ["mem0", "hindsight"];

function newSessionId(): string {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
    return crypto.randomUUID();
  }

  return `session-${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

function emptyTargetProgress(): TargetProgress {
  return {
    completed: [],
    attempts: {},
    bestScores: {},
  };
}

export function defaultProgress(): ProgressState {
  return {
    sessionId: newSessionId(),
    selectedTarget: "mem0",
    practiceMode: false,
    targets: {
      mem0: emptyTargetProgress(),
      hindsight: emptyTargetProgress(),
    },
    recent: [],
  };
}

export function levelScore(attemptNumber: number): number {
  return Math.max(20, 100 - (attemptNumber - 1) * 15);
}

export function isUnlocked(progress: ProgressState, target: TargetName, levelId: string): boolean {
  if (progress.practiceMode || levelId === "l1") {
    return true;
  }

  const previousOrder = Number(levelId.slice(1)) - 1;
  if (!Number.isFinite(previousOrder) || previousOrder < 1) {
    return false;
  }

  return progress.targets[target].completed.includes(`l${previousOrder}`);
}

export function loadProgress(): ProgressState {
  if (typeof window === "undefined") {
    return defaultProgress();
  }

  const fallback = defaultProgress();
  const raw = window.localStorage.getItem(STORAGE_KEY);
  if (!raw) {
    return fallback;
  }

  try {
    const parsed = JSON.parse(raw) as Partial<ProgressState>;
    const selectedTarget = TARGETS.includes(parsed.selectedTarget as TargetName)
      ? (parsed.selectedTarget as TargetName)
      : fallback.selectedTarget;

    return {
      ...fallback,
      ...parsed,
      sessionId: typeof parsed.sessionId === "string" ? parsed.sessionId : fallback.sessionId,
      selectedTarget,
      practiceMode: Boolean(parsed.practiceMode),
      targets: {
        mem0: { ...emptyTargetProgress(), ...parsed.targets?.mem0 },
        hindsight: { ...emptyTargetProgress(), ...parsed.targets?.hindsight },
      },
      recent: Array.isArray(parsed.recent) ? parsed.recent.slice(0, 20) : [],
    };
  } catch {
    return fallback;
  }
}

export function saveProgress(progress: ProgressState): void {
  if (typeof window === "undefined") {
    return;
  }

  window.localStorage.setItem(STORAGE_KEY, JSON.stringify(progress));
}
