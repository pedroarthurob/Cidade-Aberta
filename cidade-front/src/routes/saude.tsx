import { createFileRoute } from "@tanstack/react-router";
import { ResponsiveContainer, PieChart, Pie, Cell, Tooltip, LineChart, Line, XAxis, YAxis, CartesianGrid } from "recharts";
import { useState, useEffect } from "react";
import { PageHeader } from "@/components/shared/PageHeader";
import { KpiCard } from "@/components/shared/KpiCard";
import { ChartCard } from "@/components/shared/ChartCard";
import { unidadesSaude, evolucaoSaude, kpiResumo, formatBRL, formatBRLCompact } from "@/lib/mock-data";

export const Route = createFileRoute("/saude")({
  head: () => ({
    meta: [
      { title: "Saúde · Cidade Aberta" },
      { name: "description", content: "Investimentos da Prefeitura de Campina Grande na rede de saúde." },
      { property: "og:title", content: "Saúde · Cidade Aberta" },
      { property: "og:description", content: "Investimentos da Prefeitura de Campina Grande na rede de saúde." },
    ],
  }),
  component: SaudePage,
});

const COLORS = ["var(--chart-1)", "var(--chart-2)", "var(--chart-3)", "var(--chart-4)", "var(--chart-5)", "oklch(0.55 0.10 200)"];

function SaudePage() {
  const [total, setTotal] = useState(kpiResumo.saude);
  const [unidadesList, setUnidadesList] = useState(unidadesSaude);
  const [evolList, setEvolList] = useState(evolucaoSaude);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/api/summary")
      .then(res => res.json())
      .then(json => {
        if (json.kpi && json.kpi.saude) {
          setTotal(json.kpi.saude);
        }
      })
      .catch(err => console.log("Failed to fetch saude summary:", err));

    fetch("http://127.0.0.1:8000/api/saude")
      .then(res => res.json())
      .then(json => {
        if (json.unidadesSaude) setUnidadesList(json.unidadesSaude);
        if (json.evolucaoSaude) setEvolList(json.evolucaoSaude);
      })
      .catch(err => console.log("Failed to fetch saude details:", err));
  }, []);

  const unidades = unidadesList.length;
  const porUnidade = unidades > 0 ? total / unidades : 0;

  return (
    <div className="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:px-8">
      <PageHeader title="Saúde" description="Investimentos e atendimentos da rede municipal de saúde." />

      <div className="mt-6 grid gap-4 sm:grid-cols-3">
        <KpiCard label="Investimento total" value={formatBRLCompact(total)} tone="primary" />
        <KpiCard label="Investimento por unidade" value={formatBRLCompact(porUnidade)} tone="success" />
        <KpiCard label="Unidades atendidas" value={unidades} />
      </div>

      <div className="mt-6 grid gap-6 lg:grid-cols-2">
        <ChartCard title="Distribuição dos recursos" subtitle="Por unidade de saúde">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie data={unidadesList} dataKey="valor" nameKey="unidade" outerRadius={100} label={(e) => e.unidade}>
                {unidadesList.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
              </Pie>
              <Tooltip formatter={(v: number) => formatBRL(v)} />
            </PieChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="Evolução temporal" subtitle="Investimento mensal">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={evolList}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
              <XAxis dataKey="mes" stroke="var(--muted-foreground)" fontSize={11} />
              <YAxis tickFormatter={(v) => formatBRLCompact(v)} stroke="var(--muted-foreground)" fontSize={11} />
              <Tooltip formatter={(v: number) => formatBRL(v)} />
              <Line type="monotone" dataKey="valor" stroke="var(--chart-1)" strokeWidth={2.5} dot={{ r: 3 }} />
            </LineChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>

      <div className="mt-6 overflow-hidden rounded-xl border border-border bg-card">
        <table className="w-full text-sm">
          <thead className="bg-muted/50 text-left text-xs uppercase tracking-wide text-muted-foreground">
            <tr>
              <th className="px-4 py-3 font-medium">Unidade</th>
              <th className="px-4 py-3 text-right font-medium">Atendimentos</th>
              <th className="px-4 py-3 text-right font-medium">Investimento</th>
              <th className="px-4 py-3 text-right font-medium">Por atendimento</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {unidadesList.map((u) => (
              <tr key={u.unidade} className="hover:bg-accent/40">
                <td className="px-4 py-3 font-medium">{u.unidade}</td>
                <td className="px-4 py-3 text-right tabular-nums">{u.atendimentos.toLocaleString("pt-BR")}</td>
                <td className="px-4 py-3 text-right tabular-nums">{formatBRL(u.valor)}</td>
                <td className="px-4 py-3 text-right tabular-nums">{u.atendimentos > 0 ? formatBRL(Math.round(u.valor / u.atendimentos)) : "R$ 0,00"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
