import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { Sparkles, Send, Loader2 } from "lucide-react";
import { PageHeader } from "@/components/shared/PageHeader";

export const Route = createFileRoute("/pergunte")({
  head: () => ({
    meta: [
      { title: "Pergunte aos Dados · Cidade Aberta" },
      { name: "description", content: "Faça perguntas em linguagem natural sobre os gastos públicos de Campina Grande." },
      { property: "og:title", content: "Pergunte aos Dados · Cidade Aberta" },
      { property: "og:description", content: "Faça perguntas em linguagem natural sobre os gastos públicos de Campina Grande." },
    ],
  }),
  component: PerguntePage,
});

const SUGESTOES = [
  "Quanto foi investido em saúde em 2025?",
  "Quais são as obras paralisadas?",
  "Qual empresa mais recebeu contratos?",
  "Quanto custou a merenda escolar este ano?",
];



function PerguntePage() {
  const [pergunta, setPergunta] = useState("");
  const [resposta, setResposta] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const consultar = (texto?: string) => {
    const q = (texto ?? pergunta).trim();
    if (!q) return;
    setPergunta(q);
    setLoading(true);
    setResposta(null);
    
    fetch(`http://127.0.0.1:8000/api/chat?prompt=${encodeURIComponent(q)}`)
      .then(res => res.json())
      .then(json => {
        setResposta(json.result || json.message || "Sem resposta do servidor.");
        setLoading(false);
      })
      .catch(err => {
        console.error("Failed to fetch chat:", err);
        setResposta(
          `Resposta simulada para: "${q}".\n\nEsta área será conectada a uma IA capaz de responder perguntas em linguagem natural sobre os dados públicos da Prefeitura de Campina Grande. Por enquanto, navegue pelo Dashboard ou pelas seções de Saúde, Educação, Obras e Licitações para encontrar informações detalhadas.`
        );
        setLoading(false);
      });
  };

  return (
    <div className="mx-auto max-w-3xl px-4 py-12 sm:px-6 lg:px-8">
      <PageHeader
        title="Pergunte aos Dados"
        description="Em breve: uma IA capaz de responder perguntas em linguagem natural sobre os gastos públicos."
      />

      <div className="mt-8 rounded-2xl border border-border bg-gradient-to-br from-primary-soft to-card p-6 shadow-sm">
        <div className="flex items-center gap-2 text-sm text-primary">
          <Sparkles className="h-4 w-4" /> Assistente Cidadão · prévia
        </div>
        <div className="mt-4 flex flex-col gap-3 sm:flex-row">
          <input
            value={pergunta}
            onChange={(e) => setPergunta(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && consultar()}
            placeholder="Ex.: Quanto foi gasto em educação em 2025?"
            className="h-12 flex-1 rounded-lg border border-input bg-background px-4 text-sm outline-none ring-ring focus-visible:ring-2"
          />
          <button
            onClick={() => consultar()}
            disabled={loading}
            className="inline-flex h-12 items-center justify-center gap-2 rounded-lg bg-primary px-5 text-sm font-medium text-primary-foreground transition hover:bg-primary/90 disabled:opacity-60"
          >
            {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
            Consultar
          </button>
        </div>

        <div className="mt-4 flex flex-wrap gap-2">
          {SUGESTOES.map((s) => (
            <button
              key={s}
              onClick={() => consultar(s)}
              className="rounded-full border border-border bg-background px-3 py-1 text-xs text-muted-foreground transition hover:bg-accent hover:text-accent-foreground"
            >
              {s}
            </button>
          ))}
        </div>
      </div>

      <div className="mt-6 min-h-[160px] rounded-2xl border border-dashed border-border bg-card p-6">
        {loading && (
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Loader2 className="h-4 w-4 animate-spin" /> Consultando os dados...
          </div>
        )}
        {!loading && resposta && (
          <div>
            <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">Resposta</p>
            <p className="mt-2 whitespace-pre-line text-sm leading-relaxed text-foreground">{resposta}</p>
          </div>
        )}
        {!loading && !resposta && (
          <p className="text-sm text-muted-foreground">
            Faça uma pergunta acima ou escolha uma sugestão para ver uma resposta simulada.
          </p>
        )}
      </div>
    </div>
  );
}
