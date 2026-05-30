import { createFileRoute, Link, useParams } from "@tanstack/react-router";
import { ArrowLeft } from "lucide-react";
import { PageHeader } from "@/components/shared/PageHeader";
import { StatusBadge } from "@/components/shared/StatusBadge";
import { empresas, licitacoes, obras, formatBRL } from "@/lib/mock-data";

export const Route = createFileRoute("/empresas/$id")({
  head: ({ params }) => ({
    meta: [
      { title: `Empresa ${params.id} · Cidade Aberta` },
      { name: "description", content: "Detalhes da empresa contratada." },
    ],
  }),
  component: EmpresaDetail,
});

function EmpresaDetail() {
  const { id } = useParams({ from: "/empresas/$id" });
  const emp = empresas.find((e) => e.id === id);
  if (!emp) return <div className="p-10 text-center">Empresa não encontrada.</div>;

  const empLics = licitacoes.filter((l) => emp.licitacoes.includes(l.id));
  const empObras = obras.filter((o) => emp.obras.includes(o.id));

  return (
    <div className="mx-auto max-w-5xl px-4 py-10 sm:px-6 lg:px-8">
      <Link to="/empresas" className="mb-6 inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground">
        <ArrowLeft className="h-4 w-4" /> Voltar para empresas
      </Link>
      <PageHeader title={emp.nome} description={`CNPJ ${emp.cnpj}`} />

      <div className="mt-6 grid gap-4 sm:grid-cols-2">
        <div className="rounded-xl border border-border bg-card p-4">
          <p className="text-xs text-muted-foreground">Contratos</p>
          <p className="mt-1 text-2xl font-semibold">{emp.contratos}</p>
        </div>
        <div className="rounded-xl border border-border bg-card p-4">
          <p className="text-xs text-muted-foreground">Valor total contratado</p>
          <p className="mt-1 text-2xl font-semibold">{formatBRL(emp.valorTotal)}</p>
        </div>
      </div>

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
                  <span className="tabular-nums text-sm">{formatBRL(l.valor)}</span>
                  <StatusBadge status={l.status} />
                </div>
              </li>
            ))}
          </ul>
        )}
      </section>

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
                  <span className="tabular-nums text-sm">{formatBRL(o.valor)}</span>
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
