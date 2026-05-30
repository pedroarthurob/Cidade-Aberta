import { createFileRoute } from "@tanstack/react-router";
import { useMemo, useState } from "react";
import {
  ResponsiveContainer, PieChart, Pie, Cell, Tooltip, BarChart, Bar, XAxis, YAxis, CartesianGrid, LineChart, Line, Legend,
} from "recharts";
import { KpiCard } from "@/components/shared/KpiCard";
import { ChartCard } from "@/components/shared/ChartCard";
import { PageHeader } from "@/components/shared/PageHeader";
import {
  orcamento, gastosPorCategoria, gastosPorSecretaria, evolucaoMensal, comparacaoAnual, formatBRL, formatBRLCompact,
} from "@/lib/mock-data";

export const Route = createFileRoute("/dashboard")({
  head: () => ({
    meta: [
      { title: "Dashboard de Transparência · Cidade Aberta" },
      { name: "description", content: "Painel completo da execução orçamentária da Prefeitura de Campina Grande." },
      { property: "og:title", content: "Dashboard de Transparência · Cidade Aberta" },
      { property: "og:description", content: "Painel completo da execução orçamentária da Prefeitura de Campina Grande." },
    ],
  }),
  component: Dashboard,
});

const COLORS = ["var(--chart-1)", "var(--chart-2)", "var(--chart-3)", "var(--chart-4)", "var(--chart-5)", "oklch(0.55 0.10 200)"];

function Select({ label, value, onChange, options }: { label: string; value: string; onChange: (v: string) => void; options: string[] }) {
  return (
    <label className="flex flex-col gap-1 text-xs font-medium text-muted-foreground">
      {label}
      <select value={value} onChange={(e) => onChange(e.target.value)} className="h-9 rounded-md border border-input bg-background px-3 text-sm text-foreground outline-none ring-ring focus-visible:ring-2">
        {options.map((o) => <option key={o} value={o}>{o}</option>)}
      </select>
    </label>
  );
}

function Dashboard() {
  const [ano, setAno] = useState("2025");
  const [secretaria, setSecretaria] = useState("Todas");
  const [categoria, setCategoria] = useState("Todas");
  const [periodo, setPeriodo] = useState("Ano corrente");

  const execPct = useMemo(() => Math.round((orcamento.executado / orcamento.anual) * 100), []);

  return (
    <div className="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:px-8">
      <PageHeader
        title="Dashboard de Transparência"
        description="Visão consolidada da execução orçamentária da Prefeitura de Campina Grande."
      />

      {/* Filtros */}
      <div className="mt-6 grid grid-cols-2 gap-3 rounded-xl border border-border bg-card p-4 sm:grid-cols-4">
        <Select label="Ano" value={ano} onChange={setAno} options={["2025", "2024", "2023", "2022", "2021"]} />
        <Select label="Secretaria" value={secretaria} onChange={setSecretaria} options={["Todas", ...gastosPorSecretaria.map(s => s.secretaria)]} />
        <Select label="Categoria" value={categoria} onChange={setCategoria} options={["Todas", ...gastosPorCategoria.map(c => c.categoria)]} />
        <Select label="Período" value={periodo} onChange={setPeriodo} options={["Ano corrente", "Últimos 6 meses", "Últimos 12 meses"]} />
      </div>

      {/* KPIs */}
      <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-5">
        <KpiCard label="Orçamento anual" value={formatBRLCompact(orcamento.anual)} tone="primary" />
        <KpiCard label="Executado" value={formatBRLCompact(orcamento.executado)} hint={`${execPct}% do orçamento`} tone="success" />
        <KpiCard label="Empenhado" value={formatBRLCompact(orcamento.empenhado)} />
        <KpiCard label="Liquidado" value={formatBRLCompact(orcamento.liquidado)} />
        <KpiCard label="Pago" value={formatBRLCompact(orcamento.pago)} tone="warning" />
      </div>

      {/* Charts */}
      <div className="mt-6 grid gap-6 lg:grid-cols-2">
        <ChartCard title="Gastos por categoria" subtitle="Distribuição percentual">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie data={gastosPorCategoria} dataKey="valor" nameKey="categoria" outerRadius={100} label={(e) => e.categoria}>
                {gastosPorCategoria.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
              </Pie>
              <Tooltip formatter={(v: number) => formatBRL(v)} />
            </PieChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="Gastos por secretaria" subtitle="Top secretarias por execução">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={gastosPorSecretaria} layout="vertical" margin={{ left: 30 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
              <XAxis type="number" tickFormatter={(v) => formatBRLCompact(v)} stroke="var(--muted-foreground)" fontSize={11} />
              <YAxis type="category" dataKey="secretaria" stroke="var(--muted-foreground)" fontSize={11} width={90} />
              <Tooltip formatter={(v: number) => formatBRL(v)} />
              <Bar dataKey="valor" fill="var(--chart-1)" radius={[0, 6, 6, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="Evolução mensal dos gastos" subtitle={`Ano de ${ano}`}>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={evolucaoMensal}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
              <XAxis dataKey="mes" stroke="var(--muted-foreground)" fontSize={11} />
              <YAxis tickFormatter={(v) => formatBRLCompact(v)} stroke="var(--muted-foreground)" fontSize={11} />
              <Tooltip formatter={(v: number) => formatBRL(v)} />
              <Line type="monotone" dataKey="valor" stroke="var(--chart-1)" strokeWidth={2.5} dot={{ r: 3 }} />
            </LineChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="Comparação anual" subtitle="Orçamento aprovado por exercício">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={comparacaoAnual}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
              <XAxis dataKey="ano" stroke="var(--muted-foreground)" fontSize={11} />
              <YAxis tickFormatter={(v) => formatBRLCompact(v)} stroke="var(--muted-foreground)" fontSize={11} />
              <Tooltip formatter={(v: number) => formatBRL(v)} />
              <Legend />
              <Bar dataKey="valor" name="Orçamento" fill="var(--chart-2)" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>
    </div>
  );
}
