export type TargetName = "mem0" | "hindsight";

export type HealthTarget = {
  ready: boolean;
  diagnostics: string[];
};

export type HealthResponse = {
  api: boolean;
  mem0: HealthTarget;
  hindsight: HealthTarget;
};

export type Level = {
  id: string;
  title: string;
  family: string;
  difficulty: string;
  briefing: string;
  objective: string;
  order: number;
};

export type AttackRequest = {
  level_id: string;
  target: TargetName;
  prompt: string;
  submitted_answer?: string | null;
  session_id: string;
  attempt_number: number;
};

export type AttackResponse = {
  success: boolean;
  level_id: string;
  target: TargetName;
  message: string;
  agent_answer: string | null;
  hint?: string | null;
  diagnostics: string[];
};

const API_BASE_URL = (process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000").replace(/\/$/, "");

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    cache: "no-store",
    headers: {
      "Content-Type": "application/json",
      ...init?.headers,
    },
  });

  if (!response.ok) {
    throw new Error(`API request failed with HTTP ${response.status}`);
  }

  return response.json() as Promise<T>;
}

export function getHealth(): Promise<HealthResponse> {
  return request<HealthResponse>("/api/health");
}

export function getLevels(): Promise<Level[]> {
  return request<Level[]>("/api/levels");
}

export function submitAttack(payload: AttackRequest): Promise<AttackResponse> {
  return request<AttackResponse>("/api/attack", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}
