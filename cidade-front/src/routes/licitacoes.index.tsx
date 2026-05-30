import { createFileRoute, Link } from "@tanstack/react-router";
import { useMemo, useState, useEffect } from "react";
import { PageHeader } from "@/components/shared/PageHeader";
import { SearchBar } from "@/components/shared/SearchBar";
import { StatusBadge } from "@/components/shared/StatusBadge";
import { EmptyState } from "@/components/shared/EmptyState";
import { licitacoes, formatBRL } from "@/lib/mock-data";

export const Route = createFileRoute("/licitacoes/")({
  head: () => ({
    meta: [
      { title: "Licitações · Cidade Aberta" },
      { name: "description", content: "Consulte todas as licitações da Prefeitura de Campina Grande." },
      { property: "og:title", content: "Licitações · Cidade Aberta" },
      { property: "og:description", content: "Consulte todas as licitações da Prefeitura de Campina Grande." },
    ],
  }),
  component: LicitacoesPage,
});

function LicitacoesPage() {
  const [licList, setLicList] = useState(licitacoes);
  const [q, setQ] = useState("");
  const [status, setStatus] = useState("Todos");
  const [ano, setAno] = useState("Todos");
  const [empresa, setEmpresa] = useState("Todas");

  useEffect(() => {
    fetch("http://localhost:8000/api/licitacoes")
      .then(res => res.json())
      .then(json => {
        if (json.licitacoes) setLicList(json.licitacoes);
      })
      .catch(err => console.log("Failed to fetch licitacoes:", err));
  }, []);

  const empresas = useMemo(() => Array.from(new Set(licList.map(l => l.empresa))), [licList]);
  const anos = useMemo(() => Array.from(new Set(licList.map(l => l.data ? l.data.slice(0, 4) : "2024"))), [licList]);

  const filtered = licList.filter((l) => {
    const matchQ = !q || l.objeto.toLowerCase().includes(q.toLowerCase()) || l.numero.toLowerCase().includes(q.toLowerCase());
    const matchS = status === "Todos" || l.status === status;
    const matchA = ano === "Todos" || (l.data && l.data.startsWith(ano));
    const matchE = empresa === "Todas" || l.empresa === empresa;
    return matchQ && matchS && matchA && matchE;
  });

  return (
    <div className="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:px-8">
      <PageHeader title="Licitações" description="Processos licitatórios da Prefeitura de Campina Grande." />

      <div className="mt-6 flex flex-col gap-3 sm:flex-row sm:flex-wrap sm:items-end">
        <SearchBar value={q} onChange={setQ} placeholder="Buscar por objeto ou número..." />
        <select value={status} onChange={(e) => setStatus(e.target.value)} className="h-10 rounded-md border border-input bg-background px-3 text-sm">
          {["Todos", "Aberta", "Homologada", "Em análise", "Cancelada"].map(s => <option key={s}>{s}</option>)}
        </select>
        <select value={empresa} onChange={(e) => setEmpresa(e.target.value)} className="h-10 rounded-md border border-input bg-background px-3 text-sm">
          {["Todas", ...empresas].map(e => <option key={e}>{e}</option>)}
        </select>
        <select value={ano} onChange={(e) => setAno(e.target.value)} className="h-10 rounded-md border border-input bg-background px-3 text-sm">
          {["Todos", ...anos].map(a => <option key={a}>{a}</option>)}
        </select>
      </div>

      <div className="mt-6 overflow-hidden rounded-xl border border-border bg-card shadow-sm">
        {filtered.length === 0 ? (
          <EmptyState title="Nenhuma licitação encontrada" description="Ajuste os filtros para ver outros resultados." />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-muted/50 text-left text-xs uppercase tracking-wide text-muted-foreground">
                <tr>
                  <th className="px-4 py-3 font-medium">Número</th>
                  <th className="px-4 py-3 font-medium">Objeto</th>
                  <th className="px-4 py-3 font-medium">Empresa</th>
                  <th className="px-4 py-3 text-right font-medium">Valor</th>
                  <th className="px-4 py-3 font-medium">Data</th>
                  <th className="px-4 py-3 font-medium">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {filtered.map((l) => (
                  <tr key={l.id} className="transition hover:bg-accent/40">
                    <td className="px-4 py-3 font-medium">
                      <Link to="/licitacoes/$id" params={{ id: l.id }} className="text-primary hover:underline">
                        {l.numero}
                      </Link>
                    </td>
                    <td className="px-4 py-3 text-foreground">{l.objeto}</td>
                    <td className="px-4 py-3 text-muted-foreground">{l.empresa}</td>
                    <td className="px-4 py-3 text-right tabular-nums">{formatBRL(l.valor)}</td>
                    <td className="px-4 py-3 text-muted-foreground">{l.data ? new Date(l.data).toLocaleDateString("pt-BR") : "N/A"}</td>
                    <td className="px-4 py-3"><StatusBadge status={l.status} /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
