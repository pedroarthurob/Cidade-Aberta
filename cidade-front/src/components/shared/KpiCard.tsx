import type { ReactNode } from "react";
import { cn } from "@/lib/utils";

interface KpiCardProps {
  label: string;
  value: ReactNode;
  hint?: string;
  icon?: ReactNode;
  tone?: "default" | "primary" | "success" | "warning";
}

export function KpiCard({ label, value, hint, icon, tone = "default" }: KpiCardProps) {
  const tones: Record<NonNullable<KpiCardProps["tone"]>, string> = {
    default: "bg-card",
    primary: "bg-primary-soft",
    success: "bg-[color-mix(in_oklab,var(--success)_15%,var(--card))]",
    warning: "bg-[color-mix(in_oklab,var(--warning)_18%,var(--card))]",
  };
  return (
    <div className={cn("rounded-xl border border-border p-5 shadow-sm transition hover:shadow-md", tones[tone])}>
      <div className="flex items-start justify-between gap-3">
        <p className="text-sm font-medium text-muted-foreground">{label}</p>
        {icon ? <span className="text-primary">{icon}</span> : null}
      </div>
      <p className="mt-2 text-2xl font-semibold tracking-tight text-foreground">{value}</p>
      {hint ? <p className="mt-1 text-xs text-muted-foreground">{hint}</p> : null}
    </div>
  );
}
