import { createFileRoute } from "@tanstack/react-router";
import { useMemo, useState } from "react";
import { MapPin, Building2 } from "lucide-react";
import { PageHeader } from "@/components/shared/PageHeader";
import { StatusBadge } from "@/components/shared/StatusBadge";
import { obras, formatBRL } from "@/lib/mock-data";

export const Route = createFileRoute("/obras")({
  head: () => ({
    meta: [
      { title: "Obras Públicas · Cidade Aberta" },
      { name: "description", content: "Acompanhe as obras públicas em Campina Grande." },
      { property: "og:title", content: "Obras Públicas · Cidade Aberta" },
      { property: "og:description", content: "Acompanhe as obras públicas em Campina Grande." },
    ],
  }),
  component: ObrasPage,
});

function ObrasPage() {
  const [bairro, setBairro] = useState("Todos");
  const [status, setStatus] = useState("Todos");
  const [empresa, setEmpresa] = useState("Todas");

  const bairros = useMemo(() => Array.from(new Set(obras.map(o => o.bairro))), []);
  const empresas = useMemo(() => Array.from(new Set(obras.map(o => o.empresa))), []);

  const filtered = obras.filter((o) =>
    (bairro === "Todos" || o.bairro === bairro) &&
    (status === "Todos" || o.status === status) &&
    (empresa === "Todas" || o.empresa === empresa),
  );

  return (
    <div className="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:px-8">
      <PageHeader title="Obras Públicas" description="Obras em execução, planejadas e concluídas no município." />

      <div className="mt-6 flex flex-wrap gap-3">
        <select value={bairro} onChange={(e) => setBairro(e.target.value)} className="h-10 rounded-md border border-input bg-background px-3 text-sm">
          {["Todos", ...bairros].map(b => <option key={b}>{b}</option>)}
        </select>
        <select value={status} onChange={(e) => setStatus(e.target.value)} className="h-10 rounded-md border border-input bg-background px-3 text-sm">
          {["Todos", "Em andamento", "Concluída", "Paralisada", "Planejada"].map(s => <option key={s}>{s}</option>)}
        </select>
        <select value={empresa} onChange={(e) => setEmpresa(e.target.value)} className="h-10 rounded-md border border-input bg-background px-3 text-sm">
          {["Todas", ...empresas].map(e => <option key={e}>{e}</option>)}
        </select>
      </div>

      <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {filtered.map((o) => (
          <article key={o.id} className="flex flex-col rounded-xl border border-border bg-card p-5 shadow-sm transition hover:shadow-md">
            <div className="flex items-start justify-between gap-3">
              <h3 className="text-base font-semibold leading-snug">{o.nome}</h3>
              <StatusBadge status={o.status} />
            </div>
            <div className="mt-3 flex flex-wrap gap-x-4 gap-y-1 text-xs text-muted-foreground">
              <span className="inline-flex items-center gap-1"><MapPin className="h-3.5 w-3.5" /> {o.bairro}</span>
              <span className="inline-flex items-center gap-1"><Building2 className="h-3.5 w-3.5" /> {o.empresa}</span>
            </div>
            <div className="mt-4">
              <div className="flex items-center justify-between text-xs">
                <span className="text-muted-foreground">Progresso</span>
                <span className="font-medium">{o.progresso}%</span>
              </div>
              <div className="mt-1.5 h-2 w-full overflow-hidden rounded-full bg-muted">
                <div className="h-full rounded-full bg-primary transition-all" style={{ width: `${o.progresso}%` }} />
              </div>
            </div>
            <div className="mt-5 flex items-end justify-between border-t border-border pt-4">
              <div>
                <p className="text-xs text-muted-foreground">Investimento</p>
                <p className="text-lg font-semibold tabular-nums">{formatBRL(o.valor)}</p>
              </div>
              <div className="text-right">
                <p className="text-xs text-muted-foreground">Previsão</p>
                <p className="text-sm font-medium">{new Date(o.previsao).toLocaleDateString("pt-BR")}</p>
              </div>
            </div>
          </article>
        ))}
      </div>
    </div>
  );
}
