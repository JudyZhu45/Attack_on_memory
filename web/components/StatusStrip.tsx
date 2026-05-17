"use client";

import { Activity, AlertTriangle, CheckCircle2 } from "lucide-react";
import type { HealthResponse, TargetName } from "@/lib/api";

export function StatusStrip({
  health,
  selectedTarget,
}: {
  health: HealthResponse | null;
  selectedTarget: TargetName;
}) {
  const target = health?.[selectedTarget];
  const ready = Boolean(target?.ready);

  return (
    <section className="grid gap-3 md:grid-cols-[1fr_2fr]">
      <div className="rounded-xl border border-line bg-panel p-4">
        <div className="flex items-center gap-2 text-sm uppercase tracking-[0.22em] text-zinc-500">
          <Activity size={15} />
          Live Target
        </div>
        <div className="mt-3 flex items-center gap-3">
          {ready ? <CheckCircle2 className="text-signal" size={22} /> : <AlertTriangle className="text-venom" size={22} />}
          <div>
            <div className="font-semibold text-zinc-100">{selectedTarget === "mem0" ? "mem0" : "Hindsight"}</div>
            <div className="text-sm text-zinc-500">{ready ? "Ready for live attacks" : "Diagnostics required"}</div>
          </div>
        </div>
      </div>
      <div className="rounded-xl border border-line bg-panel p-4">
        <div className="text-sm uppercase tracking-[0.22em] text-zinc-500">Diagnostics</div>
        {!health ? (
          <p className="mt-3 text-sm text-zinc-400">Checking backend at localhost:8000...</p>
        ) : target?.diagnostics.length ? (
          <ul className="mt-3 space-y-1 text-sm text-venom">
            {target.diagnostics.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        ) : (
          <p className="mt-3 text-sm text-zinc-400">Backend, credentials, and selected target are reachable.</p>
        )}
      </div>
    </section>
  );
}
