# Cidade Aberta - Portal da Transparência Campina Grande (PB)

Este é o repositório central do projeto **Cidade Aberta**, uma iniciativa de dados cívicos voltada à melhoria da transparência pública do município de Campina Grande (PB).

O projeto é projetado para extrair informações brutas do Portal da Transparência municipal, normalizá-las em um banco de dados estruturado local e viabilizar análises de auditoria automatizadas por IA e interfaces de visualização de alto desempenho.

---

## 💻 Estrutura de Organização do Projeto

A pasta central de captação e processamento de dados (`scrapping/`) foi estruturada de forma altamente modular e limpa para separar as preocupações do sistema:

```
Cidade-Aberta/
├── .venv/                      # Ambiente virtual Python
├── README.md                   # Este guia de entrada do projeto
└── scrapping/                  # Módulo de Captura e Processamento
    ├── data/                   # Arquivos de Bancos de Dados SQLite (.db)
    │   ├── transparencia_cg.db # Banco de dados ativo populado pelo Scraper
    │   └── audit_test.db       # Banco de dados de testes e simulações
    ├── docs/                   # Documentação detalhada e catálogos técnicos
    │   ├── README.md           # Manual de engenharia reversa de API e arquitetura do DB
    │   └── DATA_AVAILABILITY.md# Dicionário de dados, endpoints JSON e metas de IA
    ├── src/                    # Código Fonte Principal (Engine)
    │   ├── db.py               # Módulo de conexão e definição de tabelas SQL
    │   └── scraper.py          # Script de automação de raspagem e sessão e-cidade
    └── tests/                  # Testes e Simulações de Auditoria
        ├── test_scraper_api.py # Casos de teste Pytest (verificação de conexões e API)
        └── test_audit.py       # Simulação prática de cruzamentos SQL (obras inacabadas)
```

---

## 🚀 Como Executar o Sistema

### 1. Requisitos e Dependências
Certifique-se de ativar o ambiente virtual e ter as dependências instaladas:
```bash
# Para instalar as dependências no ambiente virtual do projeto:
.venv/bin/pip install requests pytest
```

### 2. Executar uma Ingestão de Dados (Scraper)
O scraper coleta os dados diretamente da API JSON do município em múltiplos níveis e os insere de forma organizada em `scrapping/data/transparencia_cg.db`.
```bash
# Executa a raspagem (atualmente configurado no modo 'dry-run' rápido e limitado):
.venv/bin/python scrapping/src/scraper.py
```

### 3. Executar o Suite de Testes Pytest
O pytest roda uma bateria de testes de rede e de integridade da API para garantir que o município não alterou seus contratos de JSON na web:
```bash
# Executa os testes automatizados de conexão e API:
.venv/bin/pytest scrapping/tests/test_scraper_api.py -v
```

### 4. Executar a Simulação de Auditoria de Obras
Roda as queries relacionais cruzando obras públicas expiradas e empresas super-pagas com entrega física incompleta (detecção de desvios fiscais):
```bash
# Executa a auditoria simulada contra o banco de testes:
.venv/bin/python scrapping/tests/test_audit.py
```

---

## 📚 Documentações Disponíveis

Para aprofundar-se nos detalhes de engenharia de dados do projeto, visite a pasta **`scrapping/docs/`**:
*   📘 **[Manual de Engenharia de Dados](file:///home/adson/Codes/Cidade-Aberta/scrapping/docs/README.md)**: Detalha o diagrama de relacionamento de entidades (ERD) em Mermaid, formatações limpas, chaves primárias compostas de órgãos, regras de cascata e segredos de sessões PHP da plataforma *e-cidade*.
*   📙 **[Catálogo de Disponibilidade de Dados](file:///home/adson/Codes/Cidade-Aberta/scrapping/docs/DATA_AVAILABILITY.md)**: Dicionário detalhado mapeando os campos JSON e endpoints para Diárias, Receitas, Folha de Pagamento de Servidores, Obras Públicas, Licitações, Contratos e Parcerias Sociais.