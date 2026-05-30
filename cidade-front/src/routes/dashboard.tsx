import { createFileRoute } from "@tanstack/react-router";
import { useMemo, useState, useEffect } from "react";
import {
  ResponsiveContainer, PieChart, Pie, Cell, Tooltip, BarChart, Bar, XAxis, YAxis, CartesianGrid, LineChart, Line, Legend,
} from "recharts";
import { KpiCard } from "@/components/shared/KpiCard";
import { ChartCard } from "@/components/shared/ChartCard";
import { PageHeader } from "@/components/shared/PageHeader";
import {
  ShieldAlert, Coins, AlertTriangle, FileText, Landmark, Truck, Briefcase, CalendarClock, Scale, Sparkles
} from "lucide-react";
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

const TABS = [
  { id: "geral", label: "Orçamento Geral", icon: Landmark },
  { id: "contratacoes", label: "Contratações Diretas", icon: FileText },
  { id: "riscos", label: "Cruzamento de Riscos", icon: ShieldAlert },
  { id: "diarias", label: "Diárias & Viagens", icon: Briefcase },
  { id: "convenios", label: "Convênios & Emendas", icon: Coins },
  { id: "frota", label: "Frota & Despesas", icon: Truck },
];

function Dashboard() {
  const [activeTab, setActiveTab] = useState("geral");
  const [ano, setAno] = useState("2024");
  const [secretaria, setSecretaria] = useState("Todas");
  const [categoria, setCategoria] = useState("Todas");
  const [periodo, setPeriodo] = useState("Ano corrente");

  // Dynamic States
  const [orc, setOrc] = useState(orcamento);
  const [cats, setCats] = useState(gastosPorCategoria);
  const [secs, setSecs] = useState(gastosPorSecretaria);

  // Advanced forensic states
  const [directProc, setDirectProc] = useState<any>({ direct_ranking: [], fractioning_alerts: [] });
  const [diariasList, setDiariasList] = useState<any[]>([]);
  const [crossings, setCrossings] = useState<any>({ active_debt: [], sanctions: [], political: [] });
  const [conveniosList, setConveniosList] = useState<any[]>([]);
  const [emendasList, setEmendasList] = useState<any[]>([]);
  const [frotaList, setFrotaList] = useState<any[]>([]);

  useEffect(() => {
    fetch("http://localhost:8000/api/summary")
      .then(res => res.json())
      .then(json => {
        if (json.orcamento) setOrc(json.orcamento);
      })
      .catch(err => console.log("Failed to fetch summary orcamento:", err));

    fetch("http://localhost:8000/api/categories")
      .then(res => res.json())
      .then(json => {
        if (Array.isArray(json)) setCats(json);
      })
      .catch(err => console.log("Failed to fetch categories:", err));

    fetch("http://localhost:8000/api/secretarias")
      .then(res => res.json())
      .then(json => {
        if (Array.isArray(json)) setSecs(json);
      })
      .catch(err => console.log("Failed to fetch secretarias:", err));

    fetch("http://localhost:8000/api/auditoria/contratacoes-diretas")
      .then(res => res.json())
      .then(json => {
        if (json && json.direct_ranking) setDirectProc(json);
      })
      .catch(err => console.log("Failed to fetch direct procurement:", err));

    fetch("http://localhost:8000/api/auditoria/diarias")
      .then(res => res.json())
      .then(json => {
        if (json && json.diarias) setDiariasList(json.diarias);
      })
      .catch(err => console.log("Failed to fetch diarias:", err));

    fetch("http://localhost:8000/api/auditoria/cruzamentos")
      .then(res => res.json())
      .then(json => {
        if (json && json.active_debt) setCrossings(json);
      })
      .catch(err => console.log("Failed to fetch crossings:", err));

    fetch("http://localhost:8000/api/auditoria/convenios")
      .then(res => res.json())
      .then(json => {
        if (json && json.convenios) setConveniosList(json.convenios);
      })
      .catch(err => console.log("Failed to fetch convenios:", err));

    fetch("http://localhost:8000/api/auditoria/emendas")
      .then(res => res.json())
      .then(json => {
        if (json && json.emendas) setEmendasList(json.emendas);
      })
      .catch(err => console.log("Failed to fetch emendas:", err));

    fetch("http://localhost:8000/api/auditoria/frota")
      .then(res => res.json())
      .then(json => {
        if (json && json.frota) setFrotaList(json.frota);
      })
      .catch(err => console.log("Failed to fetch frota:", err));
  }, []);

  const execPct = useMemo(() => Math.round((orc.executado / orc.anual) * 100), [orc]);

  return (
    <div className="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:px-8">
      <PageHeader
        title="Painel de Auditoria & Transparência"
        description="Consolidado completo das 18 análises de fiscalização social e integridade fiscal."
      />

      {/* Tabs */}
      <div className="mt-6 flex flex-wrap gap-2 border-b border-border pb-px">
        {TABS.map((t) => {
          const Icon = t.icon;
          const active = activeTab === t.id;
          return (
            <button
              key={t.id}
              onClick={() => setActiveTab(t.id)}
              className={`flex items-center gap-2 border-b-2 px-4 py-2.5 text-sm font-medium transition hover:text-foreground ${active ? "border-primary text-primary" : "border-transparent text-muted-foreground"}`}
            >
              <Icon className="h-4 w-4" />
              {t.label}
            </button>
          );
        })}
      </div>

      {/* Visão Geral */}
      {activeTab === "geral" && (
        <div>
          {/* Filtros */}
          <div className="mt-6 grid grid-cols-2 gap-3 rounded-xl border border-border bg-card p-4 sm:grid-cols-4">
            <Select label="Ano" value={ano} onChange={setAno} options={["2024", "2023", "2022"]} />
            <Select label="Secretaria" value={secretaria} onChange={setSecretaria} options={["Todas", ...secs.map(s => s.secretaria)]} />
            <Select label="Categoria" value={categoria} onChange={setCategoria} options={["Todas", ...cats.map(c => c.categoria)]} />
            <Select label="Período" value={periodo} onChange={setPeriodo} options={["Ano corrente", "Últimos 6 meses", "Últimos 12 meses"]} />
          </div>

          {/* KPIs */}
          <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-5">
            <KpiCard label="Orçamento anual" value={formatBRLCompact(orc.anual)} tone="primary" />
            <KpiCard label="Executado" value={formatBRLCompact(orc.executado)} hint={`${execPct}% do orçamento`} tone="success" />
            <KpiCard label="Empenhado" value={formatBRLCompact(orc.empenhado)} />
            <KpiCard label="Liquidado" value={formatBRLCompact(orc.liquidado)} />
            <KpiCard label="Pago" value={formatBRLCompact(orc.pago)} tone="warning" />
          </div>

          {/* Charts */}
          <div className="mt-6 grid gap-6 lg:grid-cols-2">
            <ChartCard title="Gastos por categoria" subtitle="Distribuição percentual">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie data={cats} dataKey="valor" nameKey="categoria" outerRadius={100} label={(e) => e.categoria}>
                    {cats.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                  </Pie>
                  <Tooltip formatter={(v: number) => formatBRL(v)} />
                </PieChart>
              </ResponsiveContainer>
            </ChartCard>

            <ChartCard title="Gastos por secretaria" subtitle="Top secretarias por execução">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={secs} layout="vertical" margin={{ left: 30 }}>
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
      )}

      {/* Contratações Diretas */}
      {activeTab === "contratacoes" && (
        <div className="mt-6 space-y-8">
          <div>
            <h3 className="text-base font-semibold text-foreground">Ranking de Fornecedores por Contratação Direta (Dispensa / Inexigibilidade)</h3>
            <p className="text-xs text-muted-foreground mt-1">Exibição de fornecedores contratados de forma direta por inexigibilidade ou dispensa de licitação.</p>
            
            <div className="mt-4 overflow-hidden rounded-xl border border-border bg-card">
              <table className="w-full text-xs">
                <thead className="bg-muted/50 text-left uppercase tracking-wide text-muted-foreground">
                  <tr>
                    <th className="px-4 py-3 font-medium">Empresa</th>
                    <th className="px-4 py-3 font-medium">CNPJ</th>
                    <th className="px-4 py-3 text-right font-medium">Dispensas</th>
                    <th className="px-4 py-3 text-right font-medium">Inexigibilidades</th>
                    <th className="px-4 py-3 text-right font-medium">Valor Total</th>
                    <th className="px-4 py-3 font-medium">Secretarias</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {directProc.direct_ranking && directProc.direct_ranking.length > 0 ? (
                    directProc.direct_ranking.map((d: any, idx: number) => (
                      <tr key={idx} className="hover:bg-accent/40">
                        <td className="px-4 py-3 font-medium text-foreground">{d.supplier_name}</td>
                        <td className="px-4 py-3 text-muted-foreground font-mono">{d.cnpj}</td>
                        <td className="px-4 py-3 text-right tabular-nums font-medium">{d.num_dispensas}</td>
                        <td className="px-4 py-3 text-right tabular-nums font-medium">{d.num_inexigibilidades}</td>
                        <td className="px-4 py-3 text-right tabular-nums font-semibold text-primary">{formatBRL(d.total_valor)}</td>
                        <td className="px-4 py-3 text-muted-foreground max-w-[200px] truncate" title={d.secretarias}>{d.secretarias}</td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan={6} className="px-4 py-6 text-center text-muted-foreground font-medium">Nenhum fornecedor de contratação direta cadastrado no banco.</td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>

          <div>
            <div className="flex items-center gap-2 text-amber-600 dark:text-amber-500">
              <Sparkles className="h-4.5 w-4.5 animate-pulse" />
              <h3 className="text-base font-semibold text-foreground">Alertas de Fracionamento de Despesa Suspeitos</h3>
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              Desvios estruturais detectados pela IA: Fornecedores com múltiplos empenhos emitidos no mesmo dia para o mesmo elemento de despesa PJ (sinalizando possível fuga do limite legal).
            </p>
            
            <div className="mt-4 overflow-hidden rounded-xl border border-amber-500/20 bg-amber-500/5">
              <table className="w-full text-xs">
                <thead className="bg-amber-500/10 text-left uppercase tracking-wide text-amber-700 dark:text-amber-400">
                  <tr>
                    <th className="px-4 py-3 font-medium">Fornecedor</th>
                    <th className="px-4 py-3 font-medium">Data Emissão</th>
                    <th className="px-4 py-3 font-medium">Elemento</th>
                    <th className="px-4 py-3 text-right font-medium">Quantidade Empenhos</th>
                    <th className="px-4 py-3 text-right font-medium">Valor Acumulado</th>
                    <th className="px-4 py-3 font-medium">Objetos Frequentes</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-amber-500/10 text-foreground">
                  {directProc.fractioning_alerts && directProc.fractioning_alerts.length > 0 ? (
                    directProc.fractioning_alerts.map((a: any, idx: number) => (
                      <tr key={idx} className="hover:bg-amber-500/10">
                        <td className="px-4 py-3 font-medium">{a.supplier_name}</td>
                        <td className="px-4 py-3 font-mono">{a.date_emission}</td>
                        <td className="px-4 py-3">{a.element_name} ({a.element_code})</td>
                        <td className="px-4 py-3 text-right tabular-nums font-semibold">{a.num_ocorrencias} empenhos</td>
                        <td className="px-4 py-3 text-right tabular-nums font-bold text-red-600">{formatBRL(a.total_valor)}</td>
                        <td className="px-4 py-3 text-muted-foreground max-w-[250px] truncate" title={a.objetos}>{a.objetos}</td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan={6} className="px-4 py-8 text-center text-muted-foreground font-medium">✅ Nenhum alerta de fracionamento de despesa em conformidade fiscal.</td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Cruzamento de Riscos */}
      {activeTab === "riscos" && (
        <div className="mt-6 space-y-8">
          <div>
            <div className="flex items-center gap-2 text-red-600 dark:text-red-500">
              <AlertTriangle className="h-4.5 w-4.5" />
              <h3 className="text-base font-semibold text-foreground">Cruzamento: Fornecedores Ativos Inscritos em Dívida Ativa Municipal</h3>
            </div>
            <p className="text-xs text-muted-foreground mt-1">Conflitos fiscais: Empresas que recebem pagamentos públicos enquanto possuem impostos ativos pendentes com o município.</p>
            
            <div className="mt-4 overflow-hidden rounded-xl border border-red-500/20 bg-card">
              <table className="w-full text-xs">
                <thead className="bg-red-500/5 text-left uppercase tracking-wide text-red-600 dark:text-red-400">
                  <tr>
                    <th className="px-4 py-3 font-medium">Empresa devedora</th>
                    <th className="px-4 py-3 font-medium">CNPJ</th>
                    <th className="px-4 py-3 text-right font-medium">Dívida Ativa</th>
                    <th className="px-4 py-3 text-right font-medium">Faturamento Prefeitura</th>
                    <th className="px-4 py-3 font-medium">Origem do Débito</th>
                    <th className="px-4 py-3 font-medium">Inscrição</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {crossings.active_debt && crossings.active_debt.length > 0 ? (
                    crossings.active_debt.map((c: any, idx: number) => (
                      <tr key={idx} className="hover:bg-accent/40">
                        <td className="px-4 py-3 font-medium text-foreground">{c.supplier_name}</td>
                        <td className="px-4 py-3 text-muted-foreground font-mono">{c.cpf_cnpj}</td>
                        <td className="px-4 py-3 text-right tabular-nums font-bold text-red-600">{formatBRL(c.active_debt)}</td>
                        <td className="px-4 py-3 text-right tabular-nums font-semibold text-primary">{formatBRL(c.total_received)}</td>
                        <td className="px-4 py-3 text-muted-foreground">{c.origem_debito}</td>
                        <td className="px-4 py-3 text-muted-foreground font-mono">{new Date(c.data_inscricao).toLocaleDateString("pt-BR")}</td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan={6} className="px-4 py-6 text-center text-muted-foreground font-medium">Nenhum devedor inscrito em dívida ativa municipal com contratos ativos.</td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>

          <div>
            <div className="flex items-center gap-2 text-amber-600 dark:text-amber-500">
              <Coins className="h-4.5 w-4.5" />
              <h3 className="text-base font-semibold text-foreground">Cruzamento: Vínculos Societários & Doações Políticas de Sócios (TSE)</h3>
            </div>
            <p className="text-xs text-muted-foreground mt-1">Interseções de integridade: Sócios de empresas contratadas pela prefeitura que fizeram doações oficiais para campanhas eleitorais.</p>
            
            <div className="mt-4 overflow-hidden rounded-xl border border-border bg-card">
              <table className="w-full text-xs">
                <thead className="bg-muted/50 text-left uppercase tracking-wide text-muted-foreground">
                  <tr>
                    <th className="px-4 py-3 font-medium">Nome do Sócio</th>
                    <th className="px-4 py-3 font-medium">Empresa Habilitada</th>
                    <th className="px-4 py-3 text-right font-medium">Doação Eleitoral (PF)</th>
                    <th className="px-4 py-3 text-right font-medium">Faturamento Campanha</th>
                    <th className="px-4 py-3 font-medium">Candidato / Partido Beneficiado</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {crossings.political && crossings.political.length > 0 ? (
                    crossings.political.map((p: any, idx: number) => (
                      <tr key={idx} className="hover:bg-accent/40">
                        <td className="px-4 py-3 font-medium text-foreground">{p.nome_socio}</td>
                        <td className="px-4 py-3 text-muted-foreground font-semibold">{p.supplier_name}</td>
                        <td className="px-4 py-3 text-right tabular-nums font-bold text-amber-600">{formatBRL(p.campaign_donation)}</td>
                        <td className="px-4 py-3 text-right tabular-nums font-semibold">{formatBRL(p.fornecedor_campanha)}</td>
                        <td className="px-4 py-3 text-muted-foreground font-medium">{p.candidato_beneficiario} ({p.partido})</td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan={5} className="px-4 py-6 text-center text-muted-foreground font-medium">Nenhum vínculo societário ou político encontrado.</td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>

          <div>
            <div className="flex items-center gap-2 text-red-600 dark:text-red-500">
              <ShieldAlert className="h-4.5 w-4.5" />
              <h3 className="text-base font-semibold text-foreground">Cruzamento: Licitantes Sancionados e Punições Ativas (CEIS / CNEP)</h3>
            </div>
            <p className="text-xs text-muted-foreground mt-1">Conformidade legal: Empresas contratadas pela prefeitura que constam com penalidades ou declaração de inidoneidade aplicadas por órgãos federais, estaduais ou municipais.</p>
            
            <div className="mt-4 overflow-hidden rounded-xl border border-destructive/20 bg-card">
              <table className="w-full text-xs">
                <thead className="bg-destructive/5 text-left uppercase tracking-wide text-destructive">
                  <tr>
                    <th className="px-4 py-3 font-medium">Empresa Punitiva</th>
                    <th className="px-4 py-3 font-medium">Tipo de Sanção</th>
                    <th className="px-4 py-3 font-medium">Órgão Sancionador</th>
                    <th className="px-4 py-3 font-medium">Início</th>
                    <th className="px-4 py-3 font-medium">Término</th>
                    <th className="px-4 py-3 text-right font-medium">Contratos Ativos</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {crossings.sanctions && crossings.sanctions.length > 0 ? (
                    crossings.sanctions.map((s: any, idx: number) => (
                      <tr key={idx} className="hover:bg-destructive/5">
                        <td className="px-4 py-3 font-medium text-foreground">{s.supplier_name}</td>
                        <td className="px-4 py-3"><span className="rounded-full bg-red-500/10 px-2 py-0.5 font-semibold text-red-600 text-3xs">{s.sanction}</span></td>
                        <td className="px-4 py-3 text-muted-foreground">{s.orgao_sancionador}</td>
                        <td className="px-4 py-3 font-mono">{new Date(s.data_inicio).toLocaleDateString("pt-BR")}</td>
                        <td className="px-4 py-3 font-mono">{s.data_fim ? new Date(s.data_fim).toLocaleDateString("pt-BR") : "Vigência Permanente"}</td>
                        <td className="px-4 py-3 text-right tabular-nums font-bold text-primary">{formatBRL(s.total_received)}</td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan={6} className="px-4 py-6 text-center text-muted-foreground font-medium">✅ Nenhuma empresa sancionada assinando novos contratos.</td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Diárias & Passagens */}
      {activeTab === "diarias" && (
        <div className="mt-6">
          <h3 className="text-base font-semibold text-foreground">Relatório e Padrões de Viagem de Servidores (Diárias & Ressarcimentos)</h3>
          <p className="text-xs text-muted-foreground mt-1">Transparência em diárias e passagens concedidas para deslocamentos de agentes a serviço do município.</p>
          
          <div className="mt-4 overflow-hidden rounded-xl border border-border bg-card">
            <table className="w-full text-xs">
              <thead className="bg-muted/50 text-left uppercase tracking-wide text-muted-foreground">
                <tr>
                  <th className="px-4 py-3 font-medium">Beneficiário</th>
                  <th className="px-4 py-3 font-medium">Cargo</th>
                  <th className="px-4 py-3 font-medium">Secretaria / Lotação</th>
                  <th className="px-4 py-3 font-medium">Destino</th>
                  <th className="px-4 py-3 font-medium">Justificativa</th>
                  <th className="px-4 py-3 font-medium">Período</th>
                  <th className="px-4 py-3 text-right font-medium">Valor Concedido</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {diariasList && diariasList.length > 0 ? (
                  diariasList.map((d: any, idx: number) => (
                    <tr key={idx} className="hover:bg-accent/40">
                      <td className="px-4 py-3 font-medium text-foreground">{d.servant_name}</td>
                      <td className="px-4 py-3 text-muted-foreground">{d.role}</td>
                      <td className="px-4 py-3 text-muted-foreground">{d.department}</td>
                      <td className="px-4 py-3 font-semibold text-foreground">{d.destination}</td>
                      <td className="px-4 py-3 text-muted-foreground max-w-[200px] truncate" title={d.justification}>{d.justification}</td>
                      <td className="px-4 py-3 font-mono">{d.travel_period}</td>
                      <td className="px-4 py-3 text-right tabular-nums font-bold text-amber-600">{formatBRL(d.amount_paid)}</td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={7} className="px-4 py-6 text-center text-muted-foreground font-medium">Nenhum ressarcimento de diárias registrado no banco.</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Convênios & Emendas */}
      {activeTab === "convenios" && (
        <div className="mt-6 space-y-8">
          <div>
            <h3 className="text-base font-semibold text-foreground">Repasses e Parcerias com ONGs / Convênios e Termos de Fomento</h3>
            <p className="text-xs text-muted-foreground mt-1">Listagem dos recursos transferidos do município para associações civis sem fins lucrativos ou organizações sociais.</p>
            
            <div className="mt-4 overflow-hidden rounded-xl border border-border bg-card">
              <table className="w-full text-xs">
                <thead className="bg-muted/50 text-left uppercase tracking-wide text-muted-foreground">
                  <tr>
                    <th className="px-4 py-3 font-medium">Entidade Beneficiada</th>
                    <th className="px-4 py-3 font-medium">Tipo Termo</th>
                    <th className="px-4 py-3 font-medium">Objeto do Repasse</th>
                    <th className="px-4 py-3 text-right font-medium">Valor Total</th>
                    <th className="px-4 py-3 font-medium">Vigência</th>
                    <th className="px-4 py-3 font-medium">Secretaria</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {conveniosList && conveniosList.length > 0 ? (
                    conveniosList.map((c: any, idx: number) => (
                      <tr key={idx} className="hover:bg-accent/40">
                        <td className="px-4 py-3 font-medium text-foreground">{c.ngo_name}</td>
                        <td className="px-4 py-3"><span className="rounded-sm bg-accent px-1.5 py-0.5 text-3xs font-semibold">{c.partnership_type}</span></td>
                        <td className="px-4 py-3 text-muted-foreground max-w-[250px] truncate" title={c.object_description}>{c.object_description}</td>
                        <td className="px-4 py-3 text-right tabular-nums font-bold text-primary">{formatBRL(c.partnership_value)}</td>
                        <td className="px-4 py-3 font-mono">{new Date(c.start_date).toLocaleDateString("pt-BR")} a {new Date(c.end_date).toLocaleDateString("pt-BR")}</td>
                        <td className="px-4 py-3 text-muted-foreground">{c.department}</td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan={6} className="px-4 py-6 text-center text-muted-foreground font-medium">Nenhum repasse ou convênio com entidade registrado no banco.</td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>

          <div>
            <h3 className="text-base font-semibold text-foreground">Destinação de Emendas Parlamentares Municipais</h3>
            <p className="text-xs text-muted-foreground mt-1">Canais de captação: Rastreamento das verbas indicadas por deputados ou vereadores municipais até a secretaria executora.</p>
            
            <div className="mt-4 overflow-hidden rounded-xl border border-border bg-card">
              <table className="w-full text-xs">
                <thead className="bg-muted/50 text-left uppercase tracking-wide text-muted-foreground">
                  <tr>
                    <th className="px-4 py-3 font-medium">Parlamentar / Autor</th>
                    <th className="px-4 py-3 font-medium">Projeto / Objeto</th>
                    <th className="px-4 py-3 font-medium">Secretaria Responsável</th>
                    <th className="px-4 py-3 text-right font-medium">Valor Destinado</th>
                    <th className="px-4 py-3 font-medium">Vínculo Empenho</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {emendasList && emendasList.length > 0 ? (
                    emendasList.map((e: any, idx: number) => (
                      <tr key={idx} className="hover:bg-accent/40">
                        <td className="px-4 py-3 font-medium text-foreground">{e.parliamentarian}</td>
                        <td className="px-4 py-3 text-muted-foreground">{e.project}</td>
                        <td className="px-4 py-3 text-muted-foreground">{e.department}</td>
                        <td className="px-4 py-3 text-right tabular-nums font-bold text-amber-600">{formatBRL(e.amendment_value)}</td>
                        <td className="px-4 py-3 font-mono text-muted-foreground">{e.empenho_code ? `Empenho ${e.empenho_code}` : "Sem empenho vinculado"}</td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan={5} className="px-4 py-6 text-center text-muted-foreground font-medium">Nenhuma emenda parlamentar destinada registrada no banco.</td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Frota & Despesas */}
      {activeTab === "frota" && (
        <div className="mt-6">
          <h3 className="text-base font-semibold text-foreground">Consumo de Combustíveis e Despesas de Manutenção da Frota</h3>
          <p className="text-xs text-muted-foreground mt-1">Eficiência logística: Custo acumulado e consumo de combustíveis de veículos oficiais alocados por órgão da prefeitura.</p>
          
          <div className="mt-4 overflow-hidden rounded-xl border border-border bg-card">
            <table className="w-full text-xs">
              <thead className="bg-muted/50 text-left uppercase tracking-wide text-muted-foreground">
                <tr>
                  <th className="px-4 py-3 font-medium">Modelo Veículo</th>
                  <th className="px-4 py-3 font-medium">Placa</th>
                  <th className="px-4 py-3 font-medium">Secretaria Alocada</th>
                  <th className="px-4 py-3 font-medium">Aquisição</th>
                  <th className="px-4 py-3 text-right font-medium">Gasto Combustível</th>
                  <th className="px-4 py-3 text-right font-medium">Gasto Manutenção</th>
                  <th className="px-4 py-3 text-right font-medium">Total Acumulado</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {frotaList && frotaList.length > 0 ? (
                  frotaList.map((f: any, idx: number) => {
                    const comb = f.fuel_spent || 0;
                    const maint = f.maint_spent || 0;
                    const total = comb + maint;
                    return (
                      <tr key={idx} className="hover:bg-accent/40">
                        <td className="px-4 py-3 font-medium text-foreground">{f.marca} {f.modelo}</td>
                        <td className="px-4 py-3 font-mono font-semibold">{f.placa}</td>
                        <td className="px-4 py-3 text-muted-foreground">{f.secretaria}</td>
                        <td className="px-4 py-3 text-muted-foreground font-semibold">{f.tipo_aquisicao}</td>
                        <td className="px-4 py-3 text-right tabular-nums text-foreground">{formatBRL(comb)}</td>
                        <td className="px-4 py-3 text-right tabular-nums text-foreground">{formatBRL(maint)}</td>
                        <td className="px-4 py-3 text-right tabular-nums font-bold text-primary">{formatBRL(total)}</td>
                      </tr>
                    );
                  })
                ) : (
                  <tr>
                    <td colSpan={7} className="px-4 py-6 text-center text-muted-foreground font-medium">Nenhum veículo cadastrado na frota oficial do município.</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
