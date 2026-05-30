# Catálogo de Disponibilidade de Dados
## Projeto Cidade Aberta - Campina Grande (PB)

Este documento fornece um mapeamento técnico, funcional e relacional completo de todos os conjuntos de dados do Portal da Transparência de Campina Grande (PB) e sua expansão no banco de dados SQLite (`transparencia_cg.db`). Ele serve como mapa de engenharia para o desenvolvimento de ferramentas de auditoria social, painéis interativos avançados e modelos de Inteligência Artificial Forense.

---

## 1. Mapeamento dos Módulos Relacionais (20 Tabelas)

Abaixo estão detalhados os dados coletados e mapeados para as 20 tabelas relacionais do banco de dados unificado:

### 1.1 Tabelas Estruturais de Despesas
*   **`institutions`**: Entidades administrativas autônomas do município (ex: Prefeitura, Câmara Municipal, IPSEM).
*   **`organs`**: Secretarias e coordenadorias (ex: Gabinete do Prefeito, Coordenadoria de Comunicação, Sec. de Saúde).
*   **`creditors`**: Fornecedores, empreiteiras, ONGs e servidores credenciados para recebimento de empenhos (com higienização de CNPJ/CPF).
*   **`expense_elements`**: Classificações orçamentárias das despesas (ex: Diárias, Obras, Serviços de Terceiros).
*   **`empenhos`**: Ordens de reserva orçamentária e detalhamento das ações públicas (Função, Subfunção, Programa, Projeto).
*   **`movements`**: Livro razão de transações de cada empenho (Empenho, Liquidação, Pagamento, Anulação).

### 1.2 Tabelas de Governança e Contratos
*   **`receitas`**: Arrecadações fiscais (IPTU, ISS) e repasses federais/estaduais recebidos (FPM, SUS, FUNDEB).
*   **`licitacoes`**: Processos de compras públicas com modalidades (Pregão, Concorrência, Dispensa, Inexigibilidade) e valores homologados.
*   **`contratos`**: Vínculos contratuais celebrados com base em licitações e credores.
*   **`obras`**: Empreendimentos de engenharia civil com percentual de evolução física e financeira.

### 1.3 Tabelas de Recursos Humanos e Operações
*   **`payroll_records`**: Registros salariais e vínculos de servidores (Efetivos, Comissionados, Temporários).
*   **`diarias`**: Ressarcimento financeiro de viagens administrativas de servidores, contendo destinos e justificativas detalhadas.
*   **`publicidade`**: Despesas com campanhas institucionais vinculando agências de propaganda e veículos de comunicação (rádios, TVs, portais).
*   **`emendas`**: Rastreamento de emendas parlamentares federais e municipais vinculadas a empenhos e fornecedores finais.
*   **`divida_ativa`**: Rol de devedores tributários inscritos na dívida ativa municipal.
*   **`sancoes`**: Cadastro de fornecedores sancionados (CEIS, CNEP, etc.), inidôneos ou suspensos para contratação com o poder público.
*   **`relacoes_politicas`**: Cruzamento de sócios corporativos com dados eleitorais públicos de doações ou fornecimento de campanha (TSE).
*   **`convenios`**: Repasses para entidades sem fins lucrativos, termos de fomento, colaboração e parcerias com o terceiro setor.
*   **`veiculos_frota`**: Cadastro da frota municipal (carros próprios, locados ou terceirizados).
*   **`despesas_frota`**: Custos operacionais de abastecimento de combustível (litros e valores) e revisões mecânicas por placa de veículo.

---

## 2. Dicionário Analítico para 18 Auditorias de IA & Controle Social

O novo motor relacional (`analyzer.py`) e CLI (`run_analysis.py`) processam essas bases de dados para expor 18 dimensões investigativas:

| # | Análise Forense | Relação dos Dados | Perguntas e Alertas de Auditoria |
| :- | :--- | :--- | :--- |
| **1** | **Ranking Geral de Fornecedores** | Credor -> Empenho -> Contrato -> Orgão | Quem são os maiores recebedores de recursos? Quantidade de órgãos atendidos e crescimento anual. |
| **2** | **Padrão de Contratação Direta** | Modalidade -> Credor -> Contrato -> Empenho | Quais empresas concentram dispensas e inexigibilidades? Alertas de fracionamento de despesa (mesmo fornecedor/data). |
| **3** | **Monopólios por Categoria** | Objeto -> Projeto -> Credor Dominante | Detecção de monopólios estruturais em 14 nichos (Alimentação, TI, Limpeza, Medicamentos, etc.). |
| **4** | **Gastos com Saúde** | Saúde -> Elemento 339030/339039 -> Credor | Análise de compras emergenciais recorrentes de medicamentos e serviços hospitalares. |
| **5** | **Gastos com Educação** | Educação -> Merenda/Transporte/Reforma -> Credor | Auditoria de repetição de fornecedores ano a ano e custos por transporte/merenda escolar. |
| **6** | **Publicidade Institucional** | Publicidade -> Agência -> Veículo -> Ano | Análise de aumento de gastos em publicidade em anos eleitorais ou pré-eleitorais (ex: 2024/2025). |
| **7** | **Eventos, Cultura e São João** | Cultura -> Cachê Artista -> Estrutura -> Inexigibilidade | Identificação de cachês elevados concentrados por dispensa direta durante os festejos juninos. |
| **8** | **Diárias e Passagens** | Servidor -> Destino -> Justificativa -> Empenho | Servidores com volumes atípicos de diárias de viagens recorrentes com justificativas similares. |
| **9** | **Terceirização e Folha** | Secretaria -> Efetivos -> Comissionados -> Temporários | Relação entre redução de efetivos concursados e aumento de gastos com pessoal temporário/terceirizado. |
| **10** | **Frota e Combustível** | Placa -> Abastecimento -> Litros -> Valor -> Manutenção | Veículos com custos de abastecimento desproporcionais ou gastos mecânicos excessivos. |
| **11** | **Convênios e ONGs** | Entidade -> Termo Fomento -> Valor -> Objeto | Repasses elevados para entidades do terceiro setor com objetos pouco mensuráveis. |
| **12** | **Rastreamento de Emendas** | Deputado/Vereador -> Emenda -> Empenho -> Credor | Rastreio completo do recurso parlamentar até o CNPJ da empresa que executou os serviços. |
| **13** | **Cruzamento com Dívida Ativa** | Credor Contratado -> Devedores Municipais | Alerta de governança cívica: Empresas que ganham milhões da prefeitura, mas devem tributos à cidade. |
| **14** | **Licitantes Sancionados** | Credor -> Sanções CEIS/CNEP -> Contrato Novo | Detecção de fornecedores inidôneos que continuam firmando contratos com órgãos públicos. |
| **15** | **Conexões Políticas (TSE)** | Sócio Empresa -> Doador PF -> Candidato/Prefeito | Identificação de sócios de contratados da prefeitura que aparecem como doadores de campanha. |
| **16** | **Estrutura de Redes (Grafo)** | Nós (Entidades) -> Arestas (Ações) | Visualização completa de clusters de influência (ex: Grupo empresarial contratado em múltiplas secretarias). |
| **17** | **Melhores Análises Integradas** | Dashboard Geral | Exibição de sumários executivos de risco para cidadãos e analistas. |
| **18** | **Auditoria Forense Recortada** | Modelo Integrado Multi-base | Análise agregada de governança sem juízo de valor, atuando como radar de integridade pública. |

---

## 3. Diretrizes de Ingestão e AI Readiness

### 3.1 Unificação de Identificadores (Golden Records)
O banco de dados SQLite unifica as chaves estrangeiras relacionais (`creditor_id`, `empenho_id`, `numero_contrato`) permitindo que modelos cognitivos cruzem dados isolados de licitações, dívidas fiscais e doações ao TSE em frações de segundo.

### 3.2 Higienização Nativa de Ingestão (Data Cleaning)
A camada de limpeza em `scrapping/src/scraper.py` padroniza os dados:
1.  **Moeda**: Conversão de strings formatadas em padrão brasileiro (`"1.500.000,00"`) para floats computáveis (`1500000.00`).
2.  **CNPJ/CPF**: Remoção de caracteres especiais para manter apenas dígitos puros (`"11.111.111/0001-11"` $\rightarrow$ `"11111111000111"`), viabilizando queries de cruzamento instantâneas.
3.  **Datas ISO**: Tradução das datas brasileiras (`"30/05/2026"`) para o formato padrão do SQLite (`"2026-05-30"`), permitindo ordenações cronológicas e cálculos de intervalos temporais.
