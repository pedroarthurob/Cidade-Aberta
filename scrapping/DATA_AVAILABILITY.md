# Catálogo de Disponibilidade de Dados
## Portal da Transparência de Campina Grande (PB)

Este documento fornece um mapeamento técnico e funcional completo de todos os conjuntos de dados financeiros, administrativos e operacionais disponíveis no Portal da Transparência de Campina Grande. Este catálogo serve como base para o desenvolvimento do novo sistema de transparência, criação de dashboards interativos e alimentação de motores de auditoria baseados em inteligência artificial.

---

## 1. Mapeamento Geral de Módulos

O portal está estruturado nos seguintes grandes pilares de dados públicos:

1.  **Despesas Públicas**: Fluxo completo de gastos, do empenho ao pagamento final.
2.  **Receitas Públicas**: Arrecadações tributárias, transferências constitucionais e fundos.
3.  **Folha de Pagamento & Pessoal**: Cargos, remunerações e histórico funcional de servidores.
4.  **Licitações**: Processos licitatórios, editais, atas de preços e julgamentos.
5.  **Contratos Administrativos**: Instrumentos contratuais celebrados com fornecedores.
6.  **Diárias e Passagens**: Indenizações de deslocamento de agentes públicos.
7.  **Convênios e Parcerias**: Acordos e termos de fomento/colaboração com o terceiro setor.
8.  **Obras Públicas**: Acompanhamento de infraestrutura física contratada.

---

## 2. Dicionário Técnico por Módulo

### 2.1 Despesas Públicas
Acompanha a aplicação dos recursos públicos. É o módulo mais complexo e detalhado do portal.

*   **URL do Portal**: `https://transparencia.campinagrande.pb.gov.br/api/despesas`
*   **Endpoints REST JSON Descobertos**:
    *   Instituições: `/api/despesas/getInstit`
    *   Órgãos: `/api/despesas/getOrgao`
    *   Elementos de Despesa: `/api/despesas/getElementos`
    *   Credores: `/api/despesas/getCredores`
    *   Empenhos: `/api/despesas/getEmpenhos`
    *   Movimentações de Empenho: `/api/despesas/getMovimentacoesEmpenhos`
    *   Dotações Orçamentárias: `/api/despesas/getDotacaoEmpenho`

#### Campos Disponibilizados na API:
| Campo JSON | Tipo | Descrição | Exemplo |
| :--- | :--- | :--- | :--- |
| `id` | String | Identificador interno da entidade no sistema e-cidade. | `"21928"` |
| `codempenho` | String | Número do empenho formatado (Número / Ano). | `"2934 / 2022"` |
| `dataemissao` | String (Data) | Data de emissão/autorização do gasto (YYYY-MM-DD). | `"2022-09-16"` |
| `funcao_descricao`| String | Função de governo associada ao gasto. | `"EDUCAÇÃO"` |
| `subfuncao_descricao`| String | Subfunção de governo associada ao gasto. | `"ENSINO FUNDAMENTAL"` |
| `programa_descricao`| String | Programa de governo no Plano Plurianual (PPA). | `"Gestão do sistema municipal"`|
| `projeto_descricao`| String | Ação governamental (Projeto ou Atividade). | `"Ações do ensino fundamental"`|
| `recurso_descricao`| String | Fonte de financiamento do recurso. | `"RECURSOS VINCULADOS - MDE"` |
| `valor_empenhado` | Float/String | Valor reservado no orçamento para esta despesa. | `"1980.00"` |
| `valor_liquidado` | Float/String | Valor do serviço/material comprovadamente entregue.| `"1980.00"` |
| `valor_pago` | Float/String | Valor financeiro efetivamente transferido. | `"1980.00"` |
| `cpfcnpj` | String | Documento fiscal do credor (CPF/CNPJ). | `"00000000000"` |
| `nome` | String | Nome ou Razão Social do credor. | `"ADRIANA DE SÁ COSTA"` |

*   **Caso de Uso de IA / UI**: Criação de gráficos de rosca na interface mostrando distribuição de despesas por função (ex: Saúde vs. Educação); Algoritmos de detecção de anomalias (Isolation Forest) para identificar desvios de valores em elementos específicos.

---

### 2.2 Receitas Públicas
Registra todos os valores arrecadados ou recebidos pelo município.

*   **URL do Portal**: `https://transparencia.campinagrande.pb.gov.br/api/receitas`
*   **Endpoints REST JSON**:
    *   Categorias/Instituições: `/api/receitas/loadLink/instituicoes`
    *   Receitas Consolidadas: `/api/receitas/getReceita`

#### Campos Disponibilizados na API:
| Campo JSON | Tipo | Descrição | Exemplo |
| :--- | :--- | :--- | :--- |
| `classificacao` | String | Código estrutural da receita no plano de contas público. | `"1.1.1.8.01.1.1.00.00"` |
| `descricao` | String | Nome da classificação tributária ou de transferência. | `"IPTU - PREFEITURA"` |
| `valor_previsto` | Float | Estimativa de arrecadação na Lei Orçamentária Anual (LOA). | `15000000.00` |
| `valor_arrecadado`| Float | Valor financeiro de fato arrecadado no período. | `14250320.15` |
| `diferenca` | Float | Diferença matemática entre o previsto e o arrecadado. | `-749679.85` |

*   **Caso de Uso de IA / UI**: Gráfico de linha temporal comparando receita prevista vs. arrecadada; AI preditiva (com redes LSTM ou Prophet) para prever arrecadação dos próximos meses e sinalizar possíveis quedas de receita estrutural.

---

### 2.3 Folha de Pagamento & Pessoal
Apresenta os dados funcionais, salariais e contratuais de todos os servidores públicos ativos, inativos e pensionistas.

*   **URL do Portal**: `https://transparencia.campinagrande.pb.gov.br/api/cms/menus/getContent/63`
*   **Endpoints REST JSON**:
    *   Consolidado por Folha: `/api/folha-pagamento/getTotais`
    *   Servidores Detalhado: `/api/folha-pagamento/getServidores`

#### Campos Disponibilizados na API:
| Campo JSON | Tipo | Descrição | Exemplo |
| :--- | :--- | :--- | :--- |
| `matricula` | String | Identificação funcional única do servidor. | `"928122-1"` |
| `nome_servidor` | String | Nome completo do funcionário público. | `"JOAO DA SILVA SOUZA"` |
| `cargo` | String | Denominação do cargo ocupado. | `"MEDICO CLINICO GERAL"` |
| `tipo_vinculo` | String | Regime jurídico (Efetivo, Comissionado, Temporário, Inativo). | `"EFETIVO"` |
| `lotacao` | String | Secretaria ou departamento onde o servidor trabalha. | `"SECRETARIA DE SAUDE"` |
| `data_admissao` | String (Data) | Data de ingresso no serviço público municipal. | `"2015-02-10"` |
| `salario_base` | Float | Remuneração de base definida por lei para o cargo. | `8500.00` |
| `vantagens` | Float | Adicionais, gratificações, insalubridade e quinquênios. | `1250.00` |
| `descontos` | Float | Deduções obrigatórias (Previdência, Imposto de Renda) e outros. | `2400.00` |
| `salario_liquido` | Float | Valor líquido creditado na conta do servidor. | `7350.00` |

*   **Caso de Uso de IA / UI**: Ferramenta de busca com filtros avançados por cargo, secretaria e salário líquido na UI; AI de auditoria para identificar servidores acumulando cargos ilegalmente (cruzando nomes/CPFs com dados estaduais/federais) ou supersalários que extrapolem o teto constitucional.

---

### 2.4 Licitações e Contratos
Controla as compras governamentais de produtos, insumos e contratações de serviços de engenharia e tecnologia.

*   **URL do Portal**: `https://transparencia.campinagrande.pb.gov.br/api/licitacoes`
*   **Endpoints REST JSON**:
    *   Licitações: `/api/licitacoes/pesquisarLicitacoes`
    *   Itens de Licitação: `/api/licitacoes/pesquisarItens`
    *   Contratos Administrativos: `/api/licitacoes/pesquisarContratos`
    *   Atas/Documentos: `/api/licitacoes/pesquisarDocumentos`

#### Campos Disponibilizados na API (Licitações):
| Campo JSON | Tipo | Descrição | Exemplo |
| :--- | :--- | :--- | :--- |
| `processo` | String | Código de identificação do processo licitatório. | `"023/2022"` |
| `modalidade` | String | Tipo de licitação (Pregão Eletrônico, Concorrência, Inexigibilidade).| `"PREGÃO ELETRÔNICO"` |
| `objeto` | String | Descrição detalhada do que está sendo licitado. | `"Aquisição de merenda escolar"`|
| `data_abertura` | String (Data) | Data de sessão pública ou abertura de propostas. | `"2022-04-18"` |
| `situacao` | String | Status da licitação (Homologada, Revogada, Julgada, Em Andamento).| `"HOMOLOGADA"` |
| `valor_estimado` | Float | Orçamento máximo previsto pela prefeitura para a licitação. | `450000.00` |
| `valor_homologado`| Float | Valor final fechado após a fase de lances/propostas. | `412000.00` |

#### Campos Disponibilizados na API (Contratos):
| Campo JSON | Tipo | Descrição | Exemplo |
| :--- | :--- | :--- | :--- |
| `numero_contrato`| String | Número formal do instrumento contratual. | `"124/2022"` |
| `contratado` | String | Razão Social da empresa vencedora. | `"DISTRIBUIDORA DE ALIMENTOS LTDA"`|
| `vigencia_inicio`| String (Data) | Data de início dos serviços/fornecimento. | `"2022-05-01"` |
| `vigencia_fim` | String (Data) | Data de encerramento do contrato. | `"2023-05-01"` |
| `valor_contrato` | Float | Valor total do contrato assinado. | `412000.00` |

*   **Caso de Uso de IA / UI**: Visualizador de cronograma de vigência de contratos com alertas de vencimento na UI; AI NLP (Processamento de Linguagem Natural) para analisar objetos de licitações e agrupar por padrões semânticos para detectar sobrepreço de itens de mercado comuns (ex: insumos de saúde).

---

### 2.5 Diárias e Passagens
Indenizações financeiras e custos de deslocamento urbano, interestadual e internacional concedidos a servidores em missão de interesse público.

*   **URL do Portal**: `https://transparencia.campinagrande.pb.gov.br/api/despesas/loadDiarias`
*   **Endpoints REST JSON**:
    *   Listagem de Diárias: `/api/despesas/loadLink/diarias`

#### Campos Disponibilizados na API:
| Campo JSON | Tipo | Descrição | Exemplo |
| :--- | :--- | :--- | :--- |
| `nome_beneficiario`| String | Servidor ou agente político que recebeu a diária. | `"PEDRO ALBUQUERQUE SOUZA"` |
| `cargo_servidor` | String | Cargo do beneficiário. | `"SECRETÁRIO EXECUTIVO"` |
| `destino` | String | Município/Estado de destino da viagem. | `"Brasília - DF"` |
| `periodo_viagem` | String | Data de início e fim do deslocamento. | `"15/05/2022 a 18/05/2022"` |
| `justificativa` | String | Motivo e interesse público que motivou o deslocamento. | `"Reunião no Ministério da Saúde"`|
| `valor_pago` | Float | Montante indenizatório total transferido. | `2400.00` |

*   **Caso de Uso de IA / UI**: Dashboard interativo exibindo "Os servidores que mais viajaram" e "Destinos mais frequentes"; AI auditora cruzando a agenda pública oficial do servidor com as justificativas informadas na diária para validar se o compromisso público de fato ocorreu.

---

### 2.6 Obras Públicas
Projetos de infraestrutura, pavimentação urbana, saneamento e reformas físicas de prédios municipais.

*   **URL do Portal**: `/api/despesas/loadObras`
*   **Endpoints REST JSON**:
    *   Listagem de Obras: `/api/despesas/loadLink/obras`

#### Campos Disponibilizados na API:
| Campo JSON | Tipo | Descrição | Exemplo |
| :--- | :--- | :--- | :--- |
| `nome_obra` | String | Descrição física do projeto de infraestrutura. | `"Construção de Creche no Bairro Prata"`|
| `localizacao` | String | Endereço ou bairro da obra. | `"Rua Rio Branco, Prata"` |
| `empresa_executora`| String | Construtora encarregada da execução física. | `"CONSTRUTORA ALIANÇA EIRELI"` |
| `percentual_exec` | Float/String | Grau de conclusão física da obra (0.00% a 100.00%). | `"65.5%"` |
| `valor_contratado`| Float | Custo total acordado para execução da obra. | `1250000.00` |
| `valor_pago_acum` | Float | Total financeiro já transferido à construtora até o momento. | `812000.00` |

*   **Caso de Uso de IA / UI**: Mapa interativo integrado a coordenadas geográficas exibindo a localização de todas as obras municipais e seus status físicos na UI; AI de detecção de fraudes que acusa descompasso matemático entre o **andamento físico informado (ex: 90%)** e o **andamento financeiro pago (ex: 20%)** ou vice-versa (obra abandonada com 100% dos valores pagos).

---

## 3. Diretrizes de Ingestão e AI Readiness

### 3.1 Unificação de Identificadores (Golden Records)
Para criar um sistema de IA de alta performance, a base SQLite (`transparencia_cg.db`) deve atuar como o elo de ligação entre esses diferentes bancos de dados independentes. 
```
                 [ Licitação: Processo 023/2022 ]
                                | (Vencedor)
                                v
     [ Credor: DISTRIBUIDORA DE ALIMENTOS LTDA (CPF/CNPJ: XX.XXX.XXX/YYYY-ZZ) ]
                                | (Recebe)
                                v
                 [ Empenho: Código 1442 / 2022 ]
                                | (Movimentos)
                                v
               [ Pagamento: R$ 50.000 em 2022-06-15 ]
```
Isso permite rastrear a jornada completa do dinheiro público: a licitação que originou a compra, o contrato assinado, o empenho orçamentário emitido, e a transferência bancária de pagamento para o credor.

### 3.2 Higienização de Dados (Data Cleaning)
A API do portal e-cidade retorna dados com formatação legada do padrão brasileiro de numeração e pontuação. A pasta `scrapping/scraper.py` implementa a limpeza nativa de:
1.  **Valores Monetários**: Conversão de string de moeda com pontos e vírgula (`"664.544.546,30"`) para ponto flutuante puro em banco de dados (`664544546.30`).
2.  **Documentos Fiscais**: Retirada de traços, barras e pontos de CNPJ/CPF (`"00.000.000/0001-00"` $\rightarrow$ `"00000000000100"`) para otimizar indexações relacionais no SQLite e permitir buscas em velocidade sub-milisegundo.
3.  **Datas ISO**: Tradução do formato brasileiro (`"15/05/2022"`) para o formato padrão do banco de dados SQLite (`"2022-05-15"`), viabilizando queries temporais ordenadas (`ORDER BY date DESC`).
