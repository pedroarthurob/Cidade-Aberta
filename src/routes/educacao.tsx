import { createFileRoute } from "@tanstack/react-router";
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, BarChart, Bar } from "recharts";
import { PageHeader } from "@/components/shared/PageHeader";
import { KpiCard } from "@/components/shared/KpiCard";
import { ChartCard } from "@/components/shared/ChartCard";
import { investimentoEscolas, evolucaoEducacao, formatBRL, formatBRLCompact, kpiResumo } from "@/lib/mock-data";

export const Route = createFileRoute("/educacao")({
  head: () => ({
    meta: [
      { title: "Educação · Cidade Aberta" },
      { name: "description", content: "Investimentos da Prefeitura de Campina Grande em educação." },
      { property: "og:title", content: "Educação · Cidade Aberta" },
      { property: "og:description", content: "Investimentos da Prefeitura de Campina Grande em educação." },
    ],
  }),
  component: EducacaoPage,
});

function EducacaoPage() {
  const total = kpiResumo.educacao;
  const escolas = investimentoEscolas.length;
  const media = total / escolas;

  return (
    <div className="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:px-8">
      <PageHeader title="Educação" description="Indicadores e investimentos da rede municipal de ensino." />

      <div className="mt-6 grid gap-4 sm:grid-cols-3">
        <KpiCard label="Investimento total" value={formatBRLCompact(total)} tone="primary" />
        <KpiCard label="Investimento médio por escola" value={formatBRLCompact(media)} tone="success" />
        <KpiCard label="Escolas atendidas" value={escolas} />
      </div>

      <div className="mt-6 grid gap-6 lg:grid-cols-2">
        <ChartCard title="Evolução dos investimentos" subtitle="Acumulado mensal">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={evolucaoEducacao}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
              <XAxis dataKey="mes" stroke="var(--muted-foreground)" fontSize={11} />
              <YAxis tickFormatter={(v) => formatBRLCompact(v)} stroke="var(--muted-foreground)" fontSize={11} />
              <Tooltip formatter={(v: number) => formatBRL(v)} />
              <Line type="monotone" dataKey="valor" stroke="var(--chart-2)" strokeWidth={2.5} dot={{ r: 3 }} />
            </LineChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="Distribuição por unidade escolar" subtitle="Top escolas por investimento">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={investimentoEscolas} layout="vertical" margin={{ left: 40 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
              <XAxis type="number" tickFormatter={(v) => formatBRLCompact(v)} stroke="var(--muted-foreground)" fontSize={11} />
              <YAxis type="category" dataKey="escola" width={150} stroke="var(--muted-foreground)" fontSize={10} />
              <Tooltip formatter={(v: number) => formatBRL(v)} />
              <Bar dataKey="valor" fill="var(--chart-2)" radius={[0, 6, 6, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>

      <div className="mt-6 overflow-hidden rounded-xl border border-border bg-card">
        <table className="w-full text-sm">
          <thead className="bg-muted/50 text-left text-xs uppercase tracking-wide text-muted-foreground">
            <tr>
              <th className="px-4 py-3 font-medium">Escola</th>
              <th className="px-4 py-3 text-right font-medium">Alunos</th>
              <th className="px-4 py-3 text-right font-medium">Investimento</th>
              <th className="px-4 py-3 text-right font-medium">Por aluno</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {investimentoEscolas.map((e) => (
              <tr key={e.escola} className="hover:bg-accent/40">
                <td className="px-4 py-3 font-medium">{e.escola}</td>
                <td className="px-4 py-3 text-right tabular-nums">{e.alunos.toLocaleString("pt-BR")}</td>
                <td className="px-4 py-3 text-right tabular-nums">{formatBRL(e.valor)}</td>
                <td className="px-4 py-3 text-right tabular-nums">{formatBRL(Math.round(e.valor / e.alunos))}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
