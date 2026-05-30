import { cn } from "@/lib/utils";

const statusStyles: Record<string, string> = {
  "Em andamento": "bg-primary-soft text-primary",
  "Concluída": "bg-[color-mix(in_oklab,var(--success)_20%,transparent)] text-[oklch(0.40_0.12_155)]",
  "Paralisada": "bg-[color-mix(in_oklab,var(--destructive)_18%,transparent)] text-destructive",
  "Planejada": "bg-muted text-muted-foreground",
  "Aberta": "bg-primary-soft text-primary",
  "Homologada": "bg-[color-mix(in_oklab,var(--success)_20%,transparent)] text-[oklch(0.40_0.12_155)]",
  "Em análise": "bg-[color-mix(in_oklab,var(--warning)_25%,transparent)] text-[oklch(0.40_0.12_75)]",
  "Cancelada": "bg-[color-mix(in_oklab,var(--destructive)_18%,transparent)] text-destructive",
};

export function StatusBadge({ status }: { status: string }) {
  return (
    <span className={cn("inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium", statusStyles[status] ?? "bg-muted text-muted-foreground")}>
      {status}
    </span>
  );
}
