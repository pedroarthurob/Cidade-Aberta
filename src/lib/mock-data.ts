// Mock data for Cidade Aberta — Campina Grande/PB
// Estruturado para facilitar futura integração com APIs REST.

export type Status = "Em andamento" | "Concluída" | "Paralisada" | "Planejada";
export type LicitacaoStatus = "Aberta" | "Homologada" | "Em análise" | "Cancelada";

export interface KpiResumo {
  saude: number;
  educacao: number;
  infraestrutura: number;
  obrasAndamento: number;
  licitacoesAtivas: number;
}

export interface OrcamentoResumo {
  anual: number;
  executado: number;
  empenhado: number;
  liquidado: number;
  pago: number;
}

export interface CategoriaGasto { categoria: string; valor: number; }
export interface SecretariaGasto { secretaria: string; valor: number; }
export interface EvolucaoMensal { mes: string; valor: number; }
export interface ComparacaoAnual { ano: string; valor: number; }

export interface Licitacao {
  id: string;
  numero: string;
  objeto: string;
  empresa: string;
  valor: number;
  data: string;
  status: LicitacaoStatus;
  prazo?: string;
  historico?: { data: string; evento: string }[];
}

export interface Obra {
  id: string;
  nome: string;
  bairro: string;
  empresa: string;
  valor: number;
  progresso: number;
  previsao: string;
  status: Status;
}

export interface EscolaInvestimento { escola: string; valor: number; alunos: number; }
export interface UnidadeSaude { unidade: string; valor: number; atendimentos: number; }

export interface Empresa {
  id: string;
  nome: string;
  cnpj: string;
  contratos: number;
  valorTotal: number;
  obras: string[];
  licitacoes: string[];
}

const BRL = (n: number) => n;

export const kpiResumo: KpiResumo = {
  saude: 248_500_000,
  educacao: 312_700_000,
  infraestrutura: 184_200_000,
  obrasAndamento: 27,
  licitacoesAtivas: 14,
};

export const orcamento: OrcamentoResumo = {
  anual: 1_420_000_000,
  executado: 982_000_000,
  empenhado: 1_104_000_000,
  liquidado: 906_000_000,
  pago: 871_000_000,
};

export const gastosPorCategoria: CategoriaGasto[] = [
  { categoria: "Saúde", valor: BRL(248_500_000) },
  { categoria: "Educação", valor: BRL(312_700_000) },
  { categoria: "Infraestrutura", valor: BRL(184_200_000) },
  { categoria: "Assistência Social", valor: BRL(96_400_000) },
  { categoria: "Administração", valor: BRL(74_300_000) },
  { categoria: "Outros", valor: BRL(65_900_000) },
];

export const gastosPorSecretaria: SecretariaGasto[] = [
  { secretaria: "Saúde", valor: 248_500_000 },
  { secretaria: "Educação", valor: 312_700_000 },
  { secretaria: "Obras", valor: 184_200_000 },
  { secretaria: "Assistência", valor: 96_400_000 },
  { secretaria: "Cultura", valor: 28_900_000 },
  { secretaria: "Fazenda", valor: 45_300_000 },
];

export const evolucaoMensal: EvolucaoMensal[] = [
  { mes: "Jan", valor: 78_000_000 },
  { mes: "Fev", valor: 82_500_000 },
  { mes: "Mar", valor: 91_200_000 },
  { mes: "Abr", valor: 88_700_000 },
  { mes: "Mai", valor: 95_300_000 },
  { mes: "Jun", valor: 102_400_000 },
  { mes: "Jul", valor: 110_800_000 },
  { mes: "Ago", valor: 98_100_000 },
  { mes: "Set", valor: 104_600_000 },
  { mes: "Out", valor: 112_900_000 },
  { mes: "Nov", valor: 0 },
  { mes: "Dez", valor: 0 },
];

export const comparacaoAnual: ComparacaoAnual[] = [
  { ano: "2021", valor: 1_120_000_000 },
  { ano: "2022", valor: 1_240_000_000 },
  { ano: "2023", valor: 1_330_000_000 },
  { ano: "2024", valor: 1_380_000_000 },
  { ano: "2025", valor: 1_420_000_000 },
];

export const licitacoes: Licitacao[] = [
  {
    id: "lic-001",
    numero: "PE 014/2025",
    objeto: "Aquisição de medicamentos para UBS",
    empresa: "Farma Nordeste Ltda",
    valor: 4_280_000,
    data: "2025-03-12",
    status: "Homologada",
    prazo: "12 meses",
    historico: [
      { data: "2025-02-01", evento: "Publicação do edital" },
      { data: "2025-02-20", evento: "Sessão pública" },
      { data: "2025-03-12", evento: "Homologação" },
    ],
  },
  {
    id: "lic-002",
    numero: "CC 008/2025",
    objeto: "Reforma de escolas municipais — Lote 1",
    empresa: "Construtora Borborema",
    valor: 12_900_000,
    data: "2025-04-02",
    status: "Aberta",
    prazo: "18 meses",
  },
  {
    id: "lic-003",
    numero: "PE 021/2025",
    objeto: "Manutenção da iluminação pública",
    empresa: "LuzCG Engenharia",
    valor: 6_450_000,
    data: "2025-04-18",
    status: "Em análise",
    prazo: "24 meses",
  },
  {
    id: "lic-004",
    numero: "TP 003/2025",
    objeto: "Pavimentação de vias — Bairro Catolé",
    empresa: "Pavimenta CG",
    valor: 18_700_000,
    data: "2025-05-10",
    status: "Homologada",
    prazo: "10 meses",
  },
  {
    id: "lic-005",
    numero: "PE 030/2025",
    objeto: "Merenda escolar — 2º semestre",
    empresa: "Nutri Norte",
    valor: 8_120_000,
    data: "2025-06-01",
    status: "Aberta",
    prazo: "6 meses",
  },
  {
    id: "lic-006",
    numero: "CC 011/2025",
    objeto: "Construção de UBS — Bairro Bodocongó",
    empresa: "Construtora Borborema",
    valor: 9_640_000,
    data: "2025-06-20",
    status: "Aberta",
    prazo: "14 meses",
  },
  {
    id: "lic-007",
    numero: "PE 035/2025",
    objeto: "Equipamentos de informática para escolas",
    empresa: "TecnoCG",
    valor: 3_120_000,
    data: "2025-07-05",
    status: "Cancelada",
  },
];

export const obras: Obra[] = [
  { id: "obr-001", nome: "Pavimentação Rua Aprígio Veloso", bairro: "Bodocongó", empresa: "Pavimenta CG", valor: 4_200_000, progresso: 78, previsao: "2025-12-20", status: "Em andamento" },
  { id: "obr-002", nome: "Construção UBS Bodocongó", bairro: "Bodocongó", empresa: "Construtora Borborema", valor: 9_640_000, progresso: 32, previsao: "2026-04-15", status: "Em andamento" },
  { id: "obr-003", nome: "Reforma EMEF Cônego Maciel", bairro: "Centro", empresa: "Construtora Borborema", valor: 2_180_000, progresso: 100, previsao: "2025-08-10", status: "Concluída" },
  { id: "obr-004", nome: "Drenagem Bairro Catolé", bairro: "Catolé", empresa: "Pavimenta CG", valor: 6_700_000, progresso: 18, previsao: "2026-07-30", status: "Em andamento" },
  { id: "obr-005", nome: "Praça do Açude Novo — revitalização", bairro: "Centro", empresa: "Verde Urbano", valor: 1_950_000, progresso: 60, previsao: "2025-11-30", status: "Em andamento" },
  { id: "obr-006", nome: "Iluminação LED — Av. Floriano Peixoto", bairro: "Prata", empresa: "LuzCG Engenharia", valor: 3_450_000, progresso: 0, previsao: "2026-02-10", status: "Planejada" },
  { id: "obr-007", nome: "Ampliação Hospital Pedro I", bairro: "Monte Castelo", empresa: "Construtora Borborema", valor: 14_200_000, progresso: 45, previsao: "2026-09-01", status: "Paralisada" },
  { id: "obr-008", nome: "Quadra poliesportiva — Liberdade", bairro: "Liberdade", empresa: "Verde Urbano", valor: 1_280_000, progresso: 85, previsao: "2025-10-15", status: "Em andamento" },
];

export const investimentoEscolas: EscolaInvestimento[] = [
  { escola: "EMEF Cônego Maciel", valor: 4_200_000, alunos: 820 },
  { escola: "EMEF Estêvam Marinho", valor: 3_800_000, alunos: 740 },
  { escola: "EMEF Anísio Teixeira", valor: 5_100_000, alunos: 960 },
  { escola: "EMEF Solon de Lucena", valor: 2_900_000, alunos: 610 },
  { escola: "EMEF Severino Cabral", valor: 3_300_000, alunos: 680 },
  { escola: "EMEF Castro Alves", valor: 4_700_000, alunos: 880 },
];

export const evolucaoEducacao: EvolucaoMensal[] = [
  { mes: "Jan", valor: 22_000_000 },
  { mes: "Fev", valor: 24_300_000 },
  { mes: "Mar", valor: 26_800_000 },
  { mes: "Abr", valor: 25_100_000 },
  { mes: "Mai", valor: 28_700_000 },
  { mes: "Jun", valor: 31_200_000 },
  { mes: "Jul", valor: 27_900_000 },
  { mes: "Ago", valor: 29_500_000 },
  { mes: "Set", valor: 32_400_000 },
  { mes: "Out", valor: 30_100_000 },
];

export const unidadesSaude: UnidadeSaude[] = [
  { unidade: "Hospital Pedro I", valor: 42_000_000, atendimentos: 128_000 },
  { unidade: "UBS Bodocongó", valor: 6_800_000, atendimentos: 42_000 },
  { unidade: "UBS Catolé", valor: 7_200_000, atendimentos: 48_000 },
  { unidade: "UBS Liberdade", valor: 5_900_000, atendimentos: 39_000 },
  { unidade: "UPA do Catolé", valor: 18_400_000, atendimentos: 96_000 },
  { unidade: "Hospital da Mulher", valor: 22_700_000, atendimentos: 64_000 },
];

export const evolucaoSaude: EvolucaoMensal[] = [
  { mes: "Jan", valor: 17_000_000 },
  { mes: "Fev", valor: 19_200_000 },
  { mes: "Mar", valor: 20_500_000 },
  { mes: "Abr", valor: 22_100_000 },
  { mes: "Mai", valor: 21_800_000 },
  { mes: "Jun", valor: 24_300_000 },
  { mes: "Jul", valor: 23_700_000 },
  { mes: "Ago", valor: 25_900_000 },
  { mes: "Set", valor: 24_100_000 },
  { mes: "Out", valor: 26_400_000 },
];

export const empresas: Empresa[] = [
  { id: "emp-001", nome: "Construtora Borborema", cnpj: "12.345.678/0001-90", contratos: 4, valorTotal: 38_960_000, obras: ["obr-002", "obr-003", "obr-007"], licitacoes: ["lic-002", "lic-006"] },
  { id: "emp-002", nome: "Pavimenta CG", cnpj: "23.456.789/0001-12", contratos: 3, valorTotal: 29_600_000, obras: ["obr-001", "obr-004"], licitacoes: ["lic-004"] },
  { id: "emp-003", nome: "Farma Nordeste Ltda", cnpj: "34.567.890/0001-33", contratos: 2, valorTotal: 4_280_000, obras: [], licitacoes: ["lic-001"] },
  { id: "emp-004", nome: "LuzCG Engenharia", cnpj: "45.678.901/0001-44", contratos: 2, valorTotal: 9_900_000, obras: ["obr-006"], licitacoes: ["lic-003"] },
  { id: "emp-005", nome: "Verde Urbano", cnpj: "56.789.012/0001-55", contratos: 2, valorTotal: 3_230_000, obras: ["obr-005", "obr-008"], licitacoes: [] },
  { id: "emp-006", nome: "Nutri Norte", cnpj: "67.890.123/0001-66", contratos: 1, valorTotal: 8_120_000, obras: [], licitacoes: ["lic-005"] },
  { id: "emp-007", nome: "TecnoCG", cnpj: "78.901.234/0001-77", contratos: 1, valorTotal: 3_120_000, obras: [], licitacoes: ["lic-007"] },
];

export const formatBRL = (v: number) =>
  v.toLocaleString("pt-BR", { style: "currency", currency: "BRL", maximumFractionDigits: 0 });

export const formatBRLCompact = (v: number) => {
  if (v >= 1_000_000_000) return `R$ ${(v / 1_000_000_000).toFixed(2).replace(".", ",")} bi`;
  if (v >= 1_000_000) return `R$ ${(v / 1_000_000).toFixed(1).replace(".", ",")} mi`;
  if (v >= 1_000) return `R$ ${(v / 1_000).toFixed(0)} mil`;
  return formatBRL(v);
};
