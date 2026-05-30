import { createFileRoute, Link, useParams } from "@tanstack/react-router";
import { useState, useEffect } from "react";
import { ArrowLeft, ShieldAlert, Coins, AlertTriangle } from "lucide-react";
import { PageHeader } from "@/components/shared/PageHeader";
import { StatusBadge } from "@/components/shared/StatusBadge";
import { empresas, licitacoes, obras, formatBRL } from "@/lib/mock-data";

export const Route = createFileRoute("/empresas/$id")({
  head: ({ params }) => ({
    meta: [
      { title: `Empresa ${params.id} · Cidade Aberta` },
      { name: "description", content: "Detalhes da empresa contratada e cruzamentos de risco de auditoria." },
    ],
  }),
  component: EmpresaDetail,
});

interface Politica {
  nome_socio: string;
  doador_pf: number;
  fornecedor_campanha: number;
  candidato_beneficiario: string;
  partido: string;
}

interface Sancao {
  tipo_sancao: string;
  orgao_sancionador: string;
  data_inicio: string;
  data_fim: string;
}

function EmpresaDetail() {
  const { id } = useParams({ from: "/empresas/$id" });
  const mockEmp = empresas.find((e) => e.id === id);
  const mockLics = mockEmp ? licitacoes.filter((l) => mockEmp.licitacoes.includes(l.id)) : [];
  const mockObras = mockEmp ? obras.filter((o) => mockEmp.obras.includes(o.id)) : [];

  const [emp, setEmp] = useState(mockEmp);
  const [empLics, setEmpLics] = useState(mockLics);
  const [empObras, setEmpObras] = useState(mockObras);
  const [activeDebt, setActiveDebt] = useState(0);
  const [political, setPolitical] = useState<Politica[]>([]);
  const [sanctions, setSanctions] = useState<Sancao[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`http://127.0.0.1:8000/api/empresas/${encodeURIComponent(id)}`)
      .then(res => res.json())
      .then(json => {
        if (json && json.emp) {
          setEmp(json.emp);
          setEmpLics(json.licitacoes || []);
          setEmpObras(json.obras || []);
          setActiveDebt(json.active_debt || 0);
          setPolitical(json.political || []);
          setSanctions(json.sanctions || []);
        }
        setLoading(false);
      })
      .catch(err => {
        console.log("Failed to fetch empresa detail:", err);
        setLoading(false);
      });
  }, [id]);

  if (loading) return <div className="p-10 text-center text-muted-foreground animate-pulse">Carregando perfil forense da empresa...</div>;
  if (!emp) return <div className="p-10 text-center">Empresa não encontrada.</div>;

  const hasAlerts = activeDebt > 0 || political.length > 0 || sanctions.length > 0;

  return (
    <div className="mx-auto max-w-5xl px-4 py-10 sm:px-6 lg:px-8">
      <Link to="/empresas" className="mb-6 inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground">
        <ArrowLeft className="h-4 w-4" /> Voltar para empresas
      </Link>
      <PageHeader title={emp.nome} description={`Código / CNPJ ${emp.cnpj}`} />

      {/* Contratos Info */}
      <div className="mt-6 grid gap-4 sm:grid-cols-2">
        <div className="rounded-xl border border-border bg-card p-4 shadow-sm">
          <p className="text-xs text-muted-foreground">Contratos homologados</p>
          <p className="mt-1 text-2xl font-semibold text-foreground">{emp.contratos}</p>
        </div>
        <div className="rounded-xl border border-border bg-card p-4 shadow-sm">
          <p className="text-xs text-muted-foreground">Valor total contratado</p>
          <p className="mt-1 text-2xl font-semibold text-primary">{formatBRL(emp.valorTotal)}</p>
        </div>
      </div>

      {/* Forensic Auditor Panel */}
      <section className="mt-10 rounded-2xl border border-amber-500/20 bg-gradient-to-br from-amber-500/5 to-card p-6 shadow-sm">
        <div className="flex items-center gap-2 font-semibold text-amber-600 dark:text-amber-500">
          <ShieldAlert className="h-5 w-5" /> Painel de Cruzamento de Risco e Governança
        </div>
        <p className="mt-2 text-xs text-muted-foreground">
          Auditoria automatizada que cruza fornecedores da prefeitura com dados de doações partidárias (TSE), sanções oficiais e situação de dívida ativa tributária.
        </p>

        {!hasAlerts ? (
          <div className="mt-4 rounded-xl border border-border bg-background/55 p-4 text-sm text-muted-foreground">
            ✅ Nenhum alerta de governança ou inconsistência fiscal cadastrado para este fornecedor.
          </div>
        ) : (
          <div className="mt-4 grid gap-4 sm:grid-cols-1 md:grid-cols-3">
            {/* Active Debt Alert */}
            {activeDebt > 0 && (
              <div className="rounded-xl border border-red-500/20 bg-background/55 p-4 shadow-2xs">
                <div className="flex items-center gap-2 text-xs font-semibold text-red-600 dark:text-red-500">
                  <AlertTriangle className="h-4 w-4" /> Dívida Ativa Municipal
                </div>
                <p className="mt-2 text-sm font-semibold tabular-nums text-foreground">{formatBRL(activeDebt)}</p>
                <p className="mt-1 text-[10px] text-muted-foreground">Fornecedor possui impostos municipais em atraso enquanto recebe do município.</p>
              </div>
            )}

            {/* Political Connection Alert */}
            {political.length > 0 && (
              <div className="rounded-xl border border-amber-500/20 bg-background/55 p-4 shadow-2xs md:col-span-2">
                <div className="flex items-center gap-2 text-xs font-semibold text-amber-600 dark:text-amber-500">
                  <Coins className="h-4 w-4" /> Vínculo Societário / Doação Eleitoral (TSE)
                </div>
                <div className="mt-2 space-y-2">
                  {political.map((p, idx) => (
                    <div key={idx} className="text-xs text-foreground">
                      👨‍💼 <strong className="font-semibold">{p.nome_socio}</strong> (Sócio) 
                      {p.doador_pf > 0 && ` doou R$ ${p.doador_pf.toLocaleString("pt-BR")} para campanha`}
                      {p.fornecedor_campanha > 0 && ` faturou R$ ${p.fornecedor_campanha.toLocaleString("pt-BR")} em campanha`}
                      {(p.candidato_beneficiario || p.partido) && ` de ${p.candidato_beneficiario} (${p.partido})`}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Sanctions Alert */}
            {sanctions.length > 0 && (
              <div className="rounded-xl border border-red-500/20 bg-background/55 p-4 shadow-2xs md:col-span-3">
                <div className="flex items-center gap-2 text-xs font-semibold text-red-600 dark:text-red-500">
                  <ShieldAlert className="h-4 w-4" /> Registro de Sanções Ativas (Licitante Sancionado)
                </div>
                <div className="mt-2 space-y-1">
                  {sanctions.map((s, idx) => (
                    <div key={idx} className="text-xs text-foreground">
                      🚫 <strong className="font-semibold">{s.tipo_sancao}</strong> aplicada por <span className="font-medium text-muted-foreground">{s.orgao_sancionador}</span> (Início: {s.data_inicio ? new Date(s.data_inicio).toLocaleDateString("pt-BR") : "N/A"}{s.data_fim ? ` - Fim: ${new Date(s.data_fim).toLocaleDateString("pt-BR")}` : " (Vigência por prazo indeterminado)"})
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </section>

      {/* Won Bids */}
      <section className="mt-10">
        <h2 className="mb-3 text-lg font-semibold">Licitações vencidas</h2>
        {empLics.length === 0 ? (
          <p className="text-sm text-muted-foreground">Nenhuma licitação registrada.</p>
        ) : (
          <ul className="divide-y divide-border rounded-xl border border-border bg-card">
            {empLics.map((l) => (
              <li key={l.id} className="flex flex-wrap items-center justify-between gap-3 px-4 py-3">
                <div>
                  <Link to="/licitacoes/$id" params={{ id: l.id }} className="font-medium text-primary hover:underline">{l.numero}</Link>
                  <p className="text-xs text-muted-foreground">{l.objeto}</p>
                </div>
                <div className="flex items-center gap-3">
                  <span className="tabular-nums text-sm font-medium">{formatBRL(l.valor)}</span>
                  <StatusBadge status={l.status} />
                </div>
              </li>
            ))}
          </ul>
        )}
      </section>

      {/* Public Works */}
      <section className="mt-10">
        <h2 className="mb-3 text-lg font-semibold">Obras relacionadas</h2>
        {empObras.length === 0 ? (
          <p className="text-sm text-muted-foreground">Nenhuma obra associada.</p>
        ) : (
          <ul className="divide-y divide-border rounded-xl border border-border bg-card">
            {empObras.map((o) => (
              <li key={o.id} className="flex flex-wrap items-center justify-between gap-3 px-4 py-3">
                <div>
                  <p className="font-medium">{o.nome}</p>
                  <p className="text-xs text-muted-foreground">{o.bairro}</p>
                </div>
                <div className="flex items-center gap-3">
                  <span className="tabular-nums text-sm font-medium">{formatBRL(o.valor)}</span>
                  <StatusBadge status={o.status} />
                </div>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
