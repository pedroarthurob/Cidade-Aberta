import sqlite3
import os

DATABASE_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/transparencia_cg.db"))

def get_connection():
    """Establishes a connection to the SQLite database and enables foreign keys."""
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    # Enable foreign keys constraint enforcement in SQLite
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    """Initializes the database schema with tables for the municipal transparency data."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. Institutions (e.g. Prefeitura, Câmara Municipal, STTP)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS institutions (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE
        );
    """)
    
    # 2. Organs / Departments (e.g. PMCG)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS organs (
            code TEXT NOT NULL,
            name TEXT NOT NULL,
            institution_id INTEGER NOT NULL,
            PRIMARY KEY (code, institution_id),
            FOREIGN KEY (institution_id) REFERENCES institutions(id) ON DELETE CASCADE
        );
    """)
    
    # 3. Creditors (e.g. Contractors, public servants)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS creditors (
            id TEXT PRIMARY KEY,
            cpf_cnpj TEXT,
            name TEXT NOT NULL
        );
    """)
    
    # 4. Expense Elements (e.g. Diárias, Material de Consumo)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expense_elements (
            code TEXT PRIMARY KEY,
            group_name TEXT,
            name TEXT NOT NULL,
            short_code TEXT
        );
    """)
    
    # 5. Empenhos (Expense commitments / procurement records)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS empenhos (
            id TEXT PRIMARY KEY,
            code TEXT NOT NULL,
            exercicio INTEGER NOT NULL,
            institution_id INTEGER NOT NULL,
            organ_code TEXT NOT NULL,
            unit_code TEXT,
            unit_name TEXT,
            function_code TEXT,
            function_name TEXT,
            subfunction_code TEXT,
            subfunction_name TEXT,
            program_code TEXT,
            program_name TEXT,
            project_code TEXT,
            project_name TEXT,
            element_code TEXT NOT NULL,
            creditor_id TEXT NOT NULL,
            resource_code TEXT,
            resource_name TEXT,
            date_emission TEXT NOT NULL,
            amount_empenhado REAL DEFAULT 0,
            amount_anulado REAL DEFAULT 0,
            amount_liquidado REAL DEFAULT 0,
            amount_pago REAL DEFAULT 0,
            FOREIGN KEY (institution_id) REFERENCES institutions(id),
            FOREIGN KEY (organ_code, institution_id) REFERENCES organs(code, institution_id),
            FOREIGN KEY (element_code) REFERENCES expense_elements(code),
            FOREIGN KEY (creditor_id) REFERENCES creditors(id)
        );
    """)
    
    # 6. Movements (Transaction ledgers: Empenho, Liquidação, Pagamento, Anulação)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS movements (
            id TEXT PRIMARY KEY,
            empenho_id TEXT NOT NULL,
            date TEXT NOT NULL,
            type TEXT NOT NULL,
            amount REAL NOT NULL,
            type_code INTEGER,
            FOREIGN KEY (empenho_id) REFERENCES empenhos(id) ON DELETE CASCADE
        );
    """)
    
    # 7. Revenues (Receitas)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS receitas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            exercicio INTEGER NOT NULL,
            classificacao TEXT NOT NULL,
            descricao TEXT NOT NULL,
            valor_previsto REAL DEFAULT 0,
            valor_arrecadado REAL DEFAULT 0,
            diferenca REAL DEFAULT 0,
            date_ref TEXT NOT NULL
        );
    """)
    
    # 8. Public Bidding processes (Licitações)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS licitacoes (
            processo TEXT PRIMARY KEY,
            modalidade TEXT NOT NULL,
            objeto TEXT NOT NULL,
            data_abertura TEXT NOT NULL,
            situacao TEXT NOT NULL,
            valor_estimado REAL DEFAULT 0,
            valor_homologado REAL DEFAULT 0
        );
    """)
    
    # 9. Contracts signed with suppliers (Contratos)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contratos (
            numero_contrato TEXT PRIMARY KEY,
            licitacao_processo TEXT,
            contratado_creditor_id TEXT NOT NULL,
            vigencia_inicio TEXT NOT NULL,
            vigencia_fim TEXT NOT NULL,
            valor_contrato REAL NOT NULL,
            FOREIGN KEY (licitacao_processo) REFERENCES licitacoes(processo) ON DELETE SET NULL,
            FOREIGN KEY (contratado_creditor_id) REFERENCES creditors(id)
        );
    """)
    
    # 10. Public Works (Obras)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS obras (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_obra TEXT NOT NULL,
            localizacao TEXT NOT NULL,
            empresa_executora TEXT NOT NULL,
            percentual_exec REAL DEFAULT 0,
            valor_contratado REAL NOT NULL,
            valor_pago_acum REAL DEFAULT 0,
            contrato_numero TEXT,
            FOREIGN KEY (contrato_numero) REFERENCES contratos(numero_contrato) ON DELETE SET NULL
        );
    """)
    
    # 11. Civil Servant Payroll Records (Folha de Pagamento)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS payroll_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            matricula TEXT NOT NULL UNIQUE,
            nome_servidor TEXT NOT NULL,
            cargo TEXT NOT NULL,
            tipo_vinculo TEXT NOT NULL,
            lotacao TEXT NOT NULL,
            data_admissao TEXT,
            salario_base REAL DEFAULT 0,
            vantagens REAL DEFAULT 0,
            descontos REAL DEFAULT 0,
            salario_liquido REAL DEFAULT 0,
            mes INTEGER NOT NULL,
            ano INTEGER NOT NULL
        );
    """)
    
    # 12. Travel Allowances (Diárias)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS diarias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            beneficiario_matricula TEXT NOT NULL,
            nome_beneficiario TEXT NOT NULL,
            cargo_servidor TEXT NOT NULL,
            destino TEXT NOT NULL,
            periodo_viagem TEXT NOT NULL,
            justificativa TEXT NOT NULL,
            valor_pago REAL NOT NULL,
            empenho_id TEXT,
            FOREIGN KEY (beneficiario_matricula) REFERENCES payroll_records(matricula),
            FOREIGN KEY (empenho_id) REFERENCES empenhos(id) ON DELETE SET NULL
        );
    """)
    
    # 13. Institutional Advertising log (Publicidade)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS publicidade (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agencia_creditor_id TEXT NOT NULL,
            veiculo_divulgacao TEXT NOT NULL,
            valor REAL NOT NULL,
            date_ref TEXT NOT NULL, -- YYYY-MM-DD
            secretaria TEXT NOT NULL,
            numero_contrato TEXT,
            FOREIGN KEY (agencia_creditor_id) REFERENCES creditors(id),
            FOREIGN KEY (numero_contrato) REFERENCES contratos(numero_contrato) ON DELETE SET NULL
        );
    """)
    
    # 14. Parliamentary Amendments (Emendas Parlamentares)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS emendas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            parlamentar TEXT NOT NULL,
            valor REAL NOT NULL,
            projeto TEXT NOT NULL,
            secretaria_destinataria TEXT NOT NULL,
            empenho_id TEXT,
            FOREIGN KEY (empenho_id) REFERENCES empenhos(id) ON DELETE SET NULL
        );
    """)
    
    # 15. Active Debt Registry (Dívida Ativa)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS divida_ativa (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            creditor_id TEXT NOT NULL,
            valor_devido REAL NOT NULL,
            origem_debito TEXT NOT NULL,
            data_inscricao TEXT NOT NULL, -- YYYY-MM-DD
            FOREIGN KEY (creditor_id) REFERENCES creditors(id) ON DELETE CASCADE
        );
    """)
    
    # 16. Sanctioned Suppliers (Licitantes Sancionados)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sancoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            creditor_id TEXT NOT NULL,
            tipo_sancao TEXT NOT NULL, -- CEIS, CNEP, etc.
            orgao_sancionador TEXT NOT NULL,
            data_inicio TEXT NOT NULL, -- YYYY-MM-DD
            data_fim TEXT, -- YYYY-MM-DD (Null if permanent/undetermined)
            FOREIGN KEY (creditor_id) REFERENCES creditors(id) ON DELETE CASCADE
        );
    """)
    
    # 17. TSE Campaign Donors and Supplier Connections (Relações Políticas)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS relacoes_politicas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            creditor_id TEXT NOT NULL,
            nome_socio TEXT NOT NULL,
            doador_pf REAL DEFAULT 0,
            fornecedor_campanha REAL DEFAULT 0,
            candidato_beneficiario TEXT,
            partido TEXT,
            FOREIGN KEY (creditor_id) REFERENCES creditors(id) ON DELETE CASCADE
        );
    """)
    
    # 18. Municipal NGO Partnerships (Convênios / Organizações Sociais)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS convenios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entidade_creditor_id TEXT NOT NULL,
            tipo_termo TEXT NOT NULL, -- Termo de Fomento, Colaboração, etc.
            objeto TEXT NOT NULL,
            valor REAL NOT NULL,
            vigencia_inicio TEXT NOT NULL, -- YYYY-MM-DD
            vigencia_fim TEXT NOT NULL, -- YYYY-MM-DD
            secretaria TEXT NOT NULL,
            FOREIGN KEY (entidade_creditor_id) REFERENCES creditors(id)
        );
    """)
    
    # 19. Fleet Vehicles (Frota)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS veiculos_frota (
            placa TEXT PRIMARY KEY,
            modelo TEXT NOT NULL,
            marca TEXT NOT NULL,
            secretaria_alocada TEXT NOT NULL,
            tipo_aquisicao TEXT NOT NULL -- Proprio, Locado, Terceirizado
        );
    """)
    
    # 20. Fleet Fuel and Maintenance costs (Despesas Frota)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS despesas_frota (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            veiculo_placa TEXT NOT NULL,
            data TEXT NOT NULL, -- YYYY-MM-DD
            tipo_despesa TEXT NOT NULL, -- COMBUSTIVEL, MANUTENÇÃO
            valor REAL NOT NULL,
            litros REAL, -- Null if maintenance
            FOREIGN KEY (veiculo_placa) REFERENCES veiculos_frota(placa) ON DELETE CASCADE
        );
    """)

    # 21. Data Ingestion Errors Table (logs malformed or corrupt municipal transparency data)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scraper_errors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
            level TEXT NOT NULL,
            raw_payload TEXT,
            error_message TEXT NOT NULL,
            context_info TEXT
        );
    """)
    
    conn.commit()
    conn.close()
    print(f"Database initialized successfully at {DATABASE_FILE}")


def save_institution(conn, id, name):
    conn.execute(
        "INSERT OR REPLACE INTO institutions (id, name) VALUES (?, ?);",
        (id, name)
    )

def save_organ(conn, code, name, institution_id):
    conn.execute(
        "INSERT OR REPLACE INTO organs (code, name, institution_id) VALUES (?, ?, ?);",
        (code, name, institution_id)
    )

def save_creditor(conn, id, cpf_cnpj, name):
    conn.execute(
        "INSERT OR REPLACE INTO creditors (id, cpf_cnpj, name) VALUES (?, ?, ?);",
        (id, cpf_cnpj, name)
    )

def save_expense_element(conn, code, group_name, name, short_code):
    conn.execute(
        "INSERT OR REPLACE INTO expense_elements (code, group_name, name, short_code) VALUES (?, ?, ?, ?);",
        (code, group_name, name, short_code)
    )

def save_empenho(conn, data):
    conn.execute("""
        INSERT OR REPLACE INTO empenhos (
            id, code, exercicio, institution_id, organ_code, unit_code, unit_name,
            function_code, function_name, subfunction_code, subfunction_name,
            program_code, program_name, project_code, project_name,
            element_code, creditor_id, resource_code, resource_name,
            date_emission, amount_empenhado, amount_anulado, amount_liquidado, amount_pago
        ) VALUES (
            :id, :code, :exercicio, :institution_id, :organ_code, :unit_code, :unit_name,
            :function_code, :function_name, :subfunction_code, :subfunction_name,
            :program_code, :program_name, :project_code, :project_name,
            :element_code, :creditor_id, :resource_code, :resource_name,
            :date_emission, :amount_empenhado, :amount_anulado, :amount_liquidado, :amount_pago
        );
    """, data)

def save_movement(conn, id, empenho_id, date, type, amount, type_code):
    conn.execute(
        "INSERT OR REPLACE INTO movements (id, empenho_id, date, type, amount, type_code) VALUES (?, ?, ?, ?, ?, ?);",
        (id, empenho_id, date, type, amount, type_code)
    )

def save_scraper_error(conn, level, raw_payload, error_message, context_info=None):
    """Saves a technical data parsing error encountered during scraper operations to the database."""
    conn.execute("""
        INSERT INTO scraper_errors (level, raw_payload, error_message, context_info)
        VALUES (?, ?, ?, ?);
    """, (level, raw_payload, error_message, context_info))
    conn.commit()

if __name__ == "__main__":
    init_db()

