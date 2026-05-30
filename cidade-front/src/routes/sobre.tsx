import { createFileRoute } from "@tanstack/react-router";
import { PageHeader } from "@/components/shared/PageHeader";

export const Route = createFileRoute("/sobre")({
  head: () => ({
    meta: [
      { title: "Sobre · Cidade Aberta" },
      { name: "description", content: "Sobre o projeto Cidade Aberta — transparência pública em Campina Grande." },
      { property: "og:title", content: "Sobre · Cidade Aberta" },
      { property: "og:description", content: "Sobre o projeto Cidade Aberta — transparência pública em Campina Grande." },
    ],
  }),
  component: SobrePage,
});

function SobrePage() {
  return (
    <div className="mx-auto max-w-3xl px-4 py-12 sm:px-6 lg:px-8">
      <PageHeader title="Sobre o projeto" description="Conheça o Cidade Aberta e a importância da transparência pública." />

      <article className="prose prose-slate mt-8 max-w-none text-foreground">
        <h2 className="text-xl font-semibold">O que é o Cidade Aberta</h2>
        <p className="mt-2 text-muted-foreground">
          O Cidade Aberta é uma plataforma de transparência pública voltada para a população de Campina Grande/PB.
          Seu objetivo é tornar informações sobre gastos públicos acessíveis, compreensíveis e visualmente intuitivas
          para qualquer cidadão — sem exigir conhecimento técnico.
        </p>

        <h2 className="mt-8 text-xl font-semibold">Por que transparência importa</h2>
        <p className="mt-2 text-muted-foreground">
          A transparência é um pilar essencial da democracia. Quando os dados públicos estão disponíveis de forma
          clara, a população pode exercer o controle social, fiscalizar a aplicação dos recursos e participar
          ativamente das decisões que afetam a cidade.
        </p>

        <h2 className="mt-8 text-xl font-semibold">Como interpretar os dados</h2>
        <ul className="mt-2 list-disc space-y-1 pl-5 text-muted-foreground">
          <li><strong>Empenhado:</strong> recurso reservado para uma despesa.</li>
          <li><strong>Liquidado:</strong> serviço prestado ou produto entregue.</li>
          <li><strong>Pago:</strong> valor efetivamente transferido ao fornecedor.</li>
          <li><strong>Licitação:</strong> processo legal de contratação pelo poder público.</li>
        </ul>

        <h2 className="mt-8 text-xl font-semibold">Origem dos Dados</h2>
        <p className="mt-2 text-muted-foreground">
          Este portal está integrado diretamente ao banco de dados consolidado pelo scraper oficial
          da Prefeitura de Campina Grande/PB. Os dados exibidos de licitações, despesas de saúde, educação, frota, 
          diárias, publicidade, convênios e cruzamentos de risco representam transações reais obtidas a partir 
          das consultas públicas governamentais e de auditorias estatísticas cognitivas suportadas por Inteligência Artificial.
        </p>
      </article>
    </div>
  );
}
