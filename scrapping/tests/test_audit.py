import sqlite3
import os

TEST_DB = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/audit_test.db"))

def setup_test_data():
    """Creates a temporary test database and seeds it with realistic audit scenarios."""
    print(f"Setting up test database at {TEST_DB}...")
    
    # Connect and enable foreign keys
    conn = sqlite3.connect(TEST_DB)
    conn.execute("PRAGMA foreign_keys = ON;")
    cursor = conn.cursor()
    
    # 1. Create tables
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS creditors (
            id TEXT PRIMARY KEY,
            cpf_cnpj TEXT,
            name TEXT NOT NULL
        );
    """)
    
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
    
    # 2. Seed Mock Creditors / Companies
    companies = [
        ("1000001", "11.111.111/0001-11", "CONSTRUTORA BOA VISTA LTDA"),
        ("1000002", "22.222.222/0001-22", "ENG E CONSTRUCOES CAMPINA GRANDE"),
        ("1000003", "33.333.333/0001-33", "INFRAESTRUTURA NORDESTE S.A."),
        ("1000004", "44.444.444/0001-44", "CONSTRUTORA SEGURA LTDA")
    ]
    cursor.executemany("INSERT OR REPLACE INTO creditors (id, cpf_cnpj, name) VALUES (?, ?, ?);", companies)
    
    # 3. Seed Mock Biddings (Licitações)
    bids = [
        ("020/2021", "CONCORRÊNCIA", "Construção de UPA no Bairro das Nações", "2021-03-10", "HOMOLOGADA", 1100000.0, 1000000.0),
        ("021/2021", "CONCORRÊNCIA", "Reforma da Praça da Bandeira", "2021-04-15", "HOMOLOGADA", 550000.0, 500000.0),
        ("010/2020", "CONCORRÊNCIA", "Pavimentação asfáltica do Bairro Bodocongó", "2020-02-01", "HOMOLOGADA", 2200000.0, 2000000.0),
        ("005/2022", "TOMADA DE PREÇOS", "Ampliação de Escola de Ensino Fundamental", "2022-05-10", "HOMOLOGADA", 850000.0, 800000.0)
    ]
    cursor.executemany("INSERT OR REPLACE INTO licitacoes VALUES (?, ?, ?, ?, ?, ?, ?);", bids)
    
    # 4. Seed Mock Contracts (Contratos)
    contracts = [
        # Expired on 2024-12-31
        ("101/2021", "020/2021", "1000001", "2021-05-01", "2024-12-31", 1000000.0),
        # Active until 2026-12-31
        ("102/2021", "021/2021", "1000002", "2021-06-01", "2026-12-31", 500000.0),
        # Expired on 2023-06-30
        ("103/2020", "010/2020", "1000003", "2020-03-01", "2023-06-30", 2000000.0),
        # Active until 2026-10-31
        ("104/2022", "005/2022", "1000004", "2022-06-01", "2026-10-31", 800000.0)
    ]
    cursor.executemany("INSERT OR REPLACE INTO contratos VALUES (?, ?, ?, ?, ?, ?);", contracts)
    
    # 5. Seed Mock Public Works (Obras)
    works = [
        # ANOMALY A: Expired contract (expired 2024), 90% paid, but only 30% built!
        ("Construção de UPA - Bairro das Nações", "Rua das Nações, s/n", "CONSTRUTORA BOA VISTA LTDA", 30.0, 1000000.0, 900000.0, "101/2021"),
        # NORMAL B: On track, active contract, 90% paid and 95% finished.
        ("Reforma da Praça da Bandeira", "Centro, Campina Grande", "ENG E CONSTRUCOES CAMPINA GRANDE", 95.0, 500000.0, 450000.0, "102/2021"),
        # ANOMALY C: Severe delay & Expired contract (expired 2023), 95% paid, but only 50% paved!
        ("Pavimentação Bodocongó", "Bodocongó, Campina Grande", "INFRAESTRUTURA NORDESTE S.A.", 50.0, 2000000.0, 1900000.0, "103/2020"),
        # NORMAL D: Balanced active contract, 40% paid and 40% finished.
        ("Ampliação de Escola", "Malvinas, Campina Grande", "CONSTRUTORA SEGURA LTDA", 40.0, 800000.0, 320000.0, "104/2022")
    ]
    cursor.executemany("INSERT OR REPLACE INTO obras (nome_obra, localizacao, empresa_executora, percentual_exec, valor_contratado, valor_pago_acum, contrato_numero) VALUES (?, ?, ?, ?, ?, ?, ?);", works)
    
    conn.commit()
    conn.close()
    print("Database seeding completed!\n")

def run_audit_queries():
    """Executes audit SQL queries to detect incomplete, delayed, or overpaid jobs."""
    conn = sqlite3.connect(TEST_DB)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Audit 1: Hired companies whose contracts have EXPIRED but work is INCOMPLETE
    print("=========================================================================")
    print("🚩 AUDIT DETECT 1: EXPIRED CONTRACTS WITH INCOMPLETE WORKS")
    print("=========================================================================")
    
    query1 = """
        SELECT 
            cr.name AS Company,
            o.nome_obra AS Work,
            c.numero_contrato AS Contract,
            c.vigencia_fim AS Expiration,
            o.percentual_exec AS Progress_Pct,
            o.valor_contratado AS Hired_Value,
            o.valor_pago_acum AS Paid_Value
        FROM obras o
        JOIN contratos c ON o.contrato_numero = c.numero_contrato
        JOIN creditors cr ON c.contratado_creditor_id = cr.id
        WHERE 
            c.vigencia_fim < '2026-05-30'  -- simulating check relative to local system date
            AND o.percentual_exec < 100.0
        ORDER BY c.vigencia_fim ASC;
    """
    
    cursor.execute(query1)
    rows1 = cursor.fetchall()
    
    if not rows1:
        print("No expired incomplete contracts found.")
    else:
        for idx, row in enumerate(rows1):
            print(f"Alert #{idx+1}:")
            print(f"  🏢 Company:    {row['Company']}")
            print(f"  🏗️ Work:       {row['Work']} (Contract: {row['Contract']})")
            print(f"  📅 Expired:    {row['Expiration']}")
            print(f"  📊 Progress:   {row['Progress_Pct']}% completed")
            print(f"  💰 Financial:  Hired for R$ {row['Hired_Value']:,.2f} | Received R$ {row['Paid_Value']:,.2f}")
            print("-" * 73)
            
    # Audit 2: High Financial Execution vs Low Physical Execution (Discrepancy Gap)
    print("\n=========================================================================")
    print("🚩 AUDIT DETECT 2: OVERPAID VS UNDER-DELIVERED DISCREPANCIES (LEAKS)")
    print("=========================================================================")
    
    query2 = """
        SELECT 
            cr.name AS Company,
            o.nome_obra AS Work,
            c.numero_contrato AS Contract,
            o.valor_contratado AS Hired,
            o.valor_pago_acum AS Paid,
            ROUND((o.valor_pago_acum / o.valor_contratado) * 100, 2) AS Paid_Pct,
            o.percentual_exec AS Progress_Pct,
            ROUND(((o.valor_pago_acum / o.valor_contratado) * 100) - o.percentual_exec, 2) AS Discrepancy_Gap
        FROM obras o
        JOIN contratos c ON o.contrato_numero = c.numero_contrato
        JOIN creditors cr ON c.contratado_creditor_id = cr.id
        WHERE 
            o.valor_contratado > 0
            -- Flag where payment exceeds progress by over 30%
            AND ((o.valor_pago_acum / o.valor_contratado) * 100) - o.percentual_exec > 30.0
        ORDER BY Discrepancy_Gap DESC;
    """
    
    cursor.execute(query2)
    rows2 = cursor.fetchall()
    
    if not rows2:
        print("No overpayment leakage patterns detected.")
    else:
        for idx, row in enumerate(rows2):
            print(f"Leak Alert #{idx+1}:")
            print(f"  🏢 Company:         {row['Company']}")
            print(f"  🏗️ Work:            {row['Work']} (Contract: {row['Contract']})")
            print(f"  📈 Paid Percent:    {row['Paid_Pct']}%  <-->  Physical Progress: {row['Progress_Pct']}%")
            print(f"  ⚠️ Leakage Gap:     {row['Discrepancy_Gap']}% (Payment significantly exceeds work done!)")
            print(f"  💰 Monetary Leak:   Received R$ {row['Paid']:,.2f} of R$ {row['Hired']:,.2f}")
            print("-" * 73)
            
    conn.close()

if __name__ == "__main__":
    setup_test_data()
    run_audit_queries()
