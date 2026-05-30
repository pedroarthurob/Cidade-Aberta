import { createFileRoute, Link } from "@tanstack/react-router";
import { ArrowRight, FileText, HeartPulse, GraduationCap, HardHat, Building2, Sparkles } from "lucide-react";
import { ResponsiveContainer, PieChart, Pie, Cell, Tooltip } from "recharts";
import { KpiCard } from "@/components/shared/KpiCard";
import { ChartCard } from "@/components/shared/ChartCard";
import { kpiResumo, gastosPorCategoria, formatBRLCompact, formatBRL } from "@/lib/mock-data";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "Cidade Aberta · Transparência em Campina Grande" },
      { name: "description", content: "Acompanhe como os recursos públicos estão sendo utilizados em Campina Grande/PB." },
      { property: "og:title", content: "Cidade Aberta · Transparência em Campina Grande" },
      { property: "og:description", content: "Acompanhe como os recursos públicos estão sendo utilizados em Campina Grande/PB." },
    ],
  }),
  component: Home,
});

const PIE_COLORS = [
  "var(--chart-1)",
  "var(--chart-2)",
  "var(--chart-3)",
  "var(--chart-4)",
  "var(--chart-5)",
  "oklch(0.55 0.10 200)",
];

function Home() {
  return (
    <div>
      {/* Hero */}
      <section className="relative overflow-hidden border-b border-border bg-gradient-to-br from-primary-soft via-background to-background">
        <div className="mx-auto max-w-7xl px-4 py-20 sm:px-6 lg:px-8">
          <div className="max-w-3xl">
            <span className="inline-flex items-center gap-2 rounded-full border border-border bg-card/70 px-3 py-1 text-xs font-medium text-primary">
              <Sparkles className="h-3.5 w-3.5" /> Transparência pública · Campina Grande/PB
            </span>
            <h1 className="mt-5 text-4xl font-semibold tracking-tight text-foreground sm:text-5xl">
              Cidade Aberta
            </h1>
            <p className="mt-4 text-lg text-muted-foreground">
              Acompanhe como os recursos públicos estão sendo utilizados em Campina Grande.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Link
                to="/dashboard"
                className="inline-flex items-center gap-2 rounded-md bg-primary px-5 py-3 text-sm font-medium text-primary-foreground shadow-sm transition hover:bg-primary/90"
              >
                Explorar Dados <ArrowRight className="h-4 w-4" />
              </Link>
              <Link
                to="/licitacoes"
                className="inline-flex items-center gap-2 rounded-md border border-border bg-background px-5 py-3 text-sm font-medium text-foreground transition hover:bg-accent"
              >
                Ver Licitações
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* KPIs */}
      <section className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-5">
          <KpiCard label="Investido em Saúde" value={formatBRLCompact(kpiResumo.saude)} icon={<HeartPulse className="h-5 w-5" />} tone="primary" />
          <KpiCard label="Investido em Educação" value={formatBRLCompact(kpiResumo.educacao)} icon={<GraduationCap className="h-5 w-5" />} tone="success" />
          <KpiCard label="Infraestrutura" value={formatBRLCompact(kpiResumo.infraestrutura)} icon={<HardHat className="h-5 w-5" />} />
          <KpiCard label="Obras em andamento" value={kpiResumo.obrasAndamento} icon={<Building2 className="h-5 w-5" />} />
          <KpiCard label="Licitações ativas" value={kpiResumo.licitacoesAtivas} icon={<FileText className="h-5 w-5" />} tone="warning" />
        </div>
      </section>

      {/* Para onde vai o dinheiro */}
      <section className="mx-auto max-w-7xl px-4 pb-16 sm:px-6 lg:px-8">
        <div className="grid gap-6 lg:grid-cols-5">
          <div className="lg:col-span-2">
            <h2 className="text-2xl font-semibold tracking-tight">Para onde vai o dinheiro público?</h2>
            <p className="mt-3 text-sm text-muted-foreground">
              Cada real arrecadado pela Prefeitura é destinado a áreas que impactam diretamente a vida dos campinenses.
              Aqui você visualiza como o orçamento é dividido entre saúde, educação, infraestrutura, assistência social
              e demais setores.
            </p>
            <Link to="/dashboard" className="mt-5 inline-flex items-center gap-2 text-sm font-medium text-primary hover:underline">
              Ver dashboard completo <ArrowRight className="h-4 w-4" />
            </Link>
          </div>
          <div className="lg:col-span-3">
            <ChartCard title="Distribuição geral dos gastos" subtitle="Execução orçamentária por categoria">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie data={gastosPorCategoria} dataKey="valor" nameKey="categoria" innerRadius={60} outerRadius={100} paddingAngle={2}>
                    {gastosPorCategoria.map((_, i) => (
                      <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(v: number) => formatBRL(v)} />
                </PieChart>
              </ResponsiveContainer>
              <div className="-mt-4 flex flex-wrap gap-x-4 gap-y-1 text-xs text-muted-foreground">
                {gastosPorCategoria.map((c, i) => (
                  <span key={c.categoria} className="inline-flex items-center gap-1.5">
                    <span className="h-2.5 w-2.5 rounded-sm" style={{ background: PIE_COLORS[i % PIE_COLORS.length] }} />
                    {c.categoria}
                  </span>
                ))}
              </div>
            </ChartCard>
          </div>
        </div>
      </section>
    </div>
  );
}
