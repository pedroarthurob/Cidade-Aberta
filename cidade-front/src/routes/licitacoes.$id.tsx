import { createFileRoute, Link, useParams } from "@tanstack/react-router";
import { useState, useEffect } from "react";
import { ArrowLeft } from "lucide-react";
import { PageHeader } from "@/components/shared/PageHeader";
import { StatusBadge } from "@/components/shared/StatusBadge";
import { licitacoes, formatBRL } from "@/lib/mock-data";

export const Route = createFileRoute("/licitacoes/$id")({
  head: ({ params }) => ({
    meta: [
      { title: `Licitação ${params.id} · Cidade Aberta` },
      { name: "description", content: "Detalhes completos da licitação." },
    ],
  }),
  component: LicitacaoDetail,
  notFoundComponent: () => <div className="p-10 text-center">Licitação não encontrada.</div>,
});

function LicitacaoDetail() {
  const { id } = useParams({ from: "/licitacoes/$id" });
  const [lic, setLic] = useState(() => licitacoes.find((l) => l.id === id));
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`http://localhost:8000/api/licitacoes/${encodeURIComponent(id)}`)
      .then(res => res.json())
      .then(json => {
        if (json && json.id) setLic(json);
        setLoading(false);
      })
      .catch(err => {
        console.log("Failed to fetch licitacao detail:", err);
        setLoading(false);
      });
  }, [id]);

  if (loading) return <div className="p-10 text-center text-muted-foreground animate-pulse">Carregando detalhes da licitação...</div>;
  if (!lic) return <div className="p-10 text-center">Licitação não encontrada.</div>;

  return (
    <div className="mx-auto max-w-5xl px-4 py-10 sm:px-6 lg:px-8">
      <Link to="/licitacoes" className="mb-6 inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground">
        <ArrowLeft className="h-4 w-4" /> Voltar para licitações
      </Link>
      <PageHeader title={lic.numero} description={lic.objeto} actions={<StatusBadge status={lic.status} />} />

      <div className="mt-6 grid gap-4 sm:grid-cols-2">
        <Info label="Empresa contratada" value={lic.empresa} />
        <Info label="Valor contratado" value={formatBRL(lic.valor)} />
        <Info label="Data" value={lic.data ? new Date(lic.data).toLocaleDateString("pt-BR") : "N/A"} />
        <Info label="Prazo" value={lic.prazo ?? "Não informado"} />
      </div>

      <h2 className="mt-10 text-lg font-semibold">Histórico</h2>
      <ol className="mt-3 space-y-3 border-l border-border pl-4">
        {(lic.historico ?? [{ data: lic.data, evento: "Registro da licitação" }]).map((h, i) => (
          <li key={i} className="relative">
            <span className="absolute -left-[21px] top-1.5 h-2.5 w-2.5 rounded-full bg-primary" />
            <p className="text-sm font-medium">{h.evento}</p>
            <p className="text-xs text-muted-foreground">{h.data ? new Date(h.data).toLocaleDateString("pt-BR") : "N/A"}</p>
          </li>
        ))}
      </ol>
    </div>
  );
}

function Info({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border border-border bg-card p-4">
      <p className="text-xs font-medium text-muted-foreground">{label}</p>
      <p className="mt-1 text-base font-semibold text-foreground">{value}</p>
    </div>
  );
}
