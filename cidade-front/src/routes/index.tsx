import { createFileRoute, Link } from "@tanstack/react-router";
import { ArrowRight, FileText, HeartPulse, GraduationCap, HardHat, Building2, Sparkles } from "lucide-react";
import { ResponsiveContainer, PieChart, Pie, Cell, Tooltip } from "recharts";
import { useState, useEffect } from "react";
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
  const [kpis, setKpis] = useState(kpiResumo);
  const [cats, setCats] = useState(gastosPorCategoria);
  const [warnings, setWarnings] = useState<any[]>([]);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/api/summary")
      .then(res => res.json())
      .then(json => {
        if (json.kpi) setKpis(json.kpi);
      })
      .catch(err => console.log("Failed to fetch summary:", err));

    fetch("http://127.0.0.1:8000/api/categories")
      .then(res => res.json())
      .then(json => {
        if (Array.isArray(json)) setCats(json);
      })
      .catch(err => console.log("Failed to fetch categories:", err));

    fetch("http://127.0.0.1:8000/api/warnings")
      .then(res => res.json())
      .then(json => {
        if (json.warnings) setWarnings(json.warnings);
      })
      .catch(err => console.log("Failed to fetch warnings:", err));
  }, []);

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
          <KpiCard label="Investido em Saúde" value={formatBRLCompact(kpis.saude)} icon={<HeartPulse className="h-5 w-5" />} tone="primary" />
          <KpiCard label="Investido em Educação" value={formatBRLCompact(kpis.educacao)} icon={<GraduationCap className="h-5 w-5" />} tone="success" />
          <KpiCard label="Infraestrutura" value={formatBRLCompact(kpis.infraestrutura)} icon={<HardHat className="h-5 w-5" />} />
          <KpiCard label="Obras em andamento" value={kpis.obrasAndamento} icon={<Building2 className="h-5 w-5" />} />
          <KpiCard label="Licitações ativas" value={kpis.licitacoesAtivas} icon={<FileText className="h-5 w-5" />} tone="warning" />
        </div>
      </section>

      {/* AI Warnings & Anomalies Section */}
      {warnings.length > 0 && (
        <section className="mx-auto max-w-7xl px-4 pb-12 sm:px-6 lg:px-8">
          <div className="rounded-2xl border border-amber-500/20 bg-gradient-to-br from-amber-500/5 to-card p-6 shadow-sm">
            <div className="flex items-center gap-2 text-sm font-semibold text-amber-600 dark:text-amber-500">
              <Sparkles className="h-4.5 w-4.5 animate-pulse" /> Inteligência Cívica · Alertas Forenses da IA
            </div>
            <h2 className="mt-2 text-xl font-semibold tracking-tight">Detecções e Padrões Incomuns</h2>
            <p className="text-xs text-muted-foreground mt-1">
              Nossa inteligência artificial analisa continuamente os repasses, obras e diárias municipais para identificar desvios estatísticos ou semânticos.
            </p>
            <div className="mt-6 grid gap-4 sm:grid-cols-1 md:grid-cols-2">
              {warnings.slice(0, 4).map((w, i) => (
                <div key={i} className="flex flex-col justify-between rounded-xl border border-border bg-background/60 p-4 shadow-2xs hover:shadow-xs transition hover:bg-background/80">
                  <div>
                    <span className="inline-block rounded-full bg-amber-500/10 px-2 py-0.5 text-[10px] font-semibold text-amber-600 dark:text-amber-500">
                      {w.topic}
                    </span>
                    <p className="mt-3 text-xs leading-relaxed text-foreground font-medium">
                      {w.text}
                    </p>
                  </div>
                  {w.data && (
                    <div className="mt-4 border-t border-border pt-3 flex flex-wrap gap-2 text-[10px] text-muted-foreground font-mono">
                      {Object.entries(w.data).map(([key, val]: any) => (
                        <span key={key} className="bg-muted px-1.5 py-0.5 rounded-sm">
                          <strong>{key}:</strong> {typeof val === "number" ? val.toLocaleString("pt-BR") : String(val)}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </section>
      )}

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
                  <Pie data={cats} dataKey="valor" nameKey="categoria" innerRadius={60} outerRadius={100} paddingAngle={2}>
                    {cats.map((_, i) => (
                      <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(v: number) => formatBRL(v)} />
                </PieChart>
              </ResponsiveContainer>
              <div className="-mt-4 flex flex-wrap gap-x-4 gap-y-1 text-xs text-muted-foreground">
                {cats.map((c, i) => (
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
