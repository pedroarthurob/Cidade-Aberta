import { createFileRoute, Link } from "@tanstack/react-router";
import { useState, useEffect } from "react";
import { PageHeader } from "@/components/shared/PageHeader";
import { empresas, formatBRL } from "@/lib/mock-data";

export const Route = createFileRoute("/empresas/")({
  head: () => ({
    meta: [
      { title: "Empresas Contratadas · Cidade Aberta" },
      { name: "description", content: "Empresas com contratos junto à Prefeitura de Campina Grande." },
      { property: "og:title", content: "Empresas Contratadas · Cidade Aberta" },
      { property: "og:description", content: "Empresas com contratos junto à Prefeitura de Campina Grande." },
    ],
  }),
  component: EmpresasPage,
});

function EmpresasPage() {
  const [empList, setEmpList] = useState(empresas);

  useEffect(() => {
    fetch("http://localhost:8000/api/empresas")
      .then(res => res.json())
      .then(json => {
        if (json.empresas) setEmpList(json.empresas);
      })
      .catch(err => console.log("Failed to fetch empresas:", err));
  }, []);

  return (
    <div className="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:px-8">
      <PageHeader title="Empresas Contratadas" description="Fornecedores e prestadores com vínculo contratual ativo." />

      <div className="mt-6 overflow-hidden rounded-xl border border-border bg-card shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-muted/50 text-left text-xs uppercase tracking-wide text-muted-foreground">
              <tr>
                <th className="px-4 py-3 font-medium">Empresa</th>
                <th className="px-4 py-3 font-medium">CNPJ</th>
                <th className="px-4 py-3 text-right font-medium">Contratos</th>
                <th className="px-4 py-3 text-right font-medium">Valor total</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {empList.map((e) => (
                <tr key={e.id} className="hover:bg-accent/40">
                  <td className="px-4 py-3 font-medium">
                    <Link to="/empresas/$id" params={{ id: e.id }} className="text-primary hover:underline">{e.nome}</Link>
                  </td>
                  <td className="px-4 py-3 text-muted-foreground tabular-nums">{e.cnpj}</td>
                  <td className="px-4 py-3 text-right tabular-nums">{e.contratos}</td>
                  <td className="px-4 py-3 text-right tabular-nums">{formatBRL(e.valorTotal)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
