import sqlite3
import os

DATABASE_FILE = os.path.join(os.path.dirname(__file__), "transparencia_cg.db")

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

if __name__ == "__main__":
    init_db()
