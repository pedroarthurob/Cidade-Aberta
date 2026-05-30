import sqlite3
import os
import math
import json
import requests

MAIN_DB = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/transparencia_cg.db"))
TEST_DB = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/audit_test.db"))

def get_anomaly_data(db_path=None):
    """Fetches payment-to-progress discrepancy gaps from the database."""
    target_db = db_path if db_path else (MAIN_DB if os.path.exists(MAIN_DB) else TEST_DB)
    conn = sqlite3.connect(target_db)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    query = """
        SELECT 
            cr.name AS company,
            o.nome_obra AS work,
            o.valor_contratado AS hired,
            o.valor_pago_acum AS paid,
            ((o.valor_pago_acum / o.valor_contratado) * 100) - o.percentual_exec AS discrepancy_gap
        FROM obras o
        JOIN contratos c ON o.contrato_numero = c.numero_contrato
        JOIN creditors cr ON c.contratado_creditor_id = cr.id
        WHERE o.valor_contratado > 0;
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def run_statistical_anomaly_detection(data):
    """
    Performs unsupervised Anomaly Detection using Z-Score statistical modeling.
    Flags data points that deviate significantly from the average spending velocity gap.
    """
    print("\n" + "="*80)
    print("📈 LAYER 1: STATISTICAL OUTLIER ANOMALY DETECTION (UNSUPERVISED ML)")
    print("="*80)
    
    if not data:
        print("No transactional data available to model.")
        return
        
    gaps = [r["discrepancy_gap"] for r in data]
    
    # Calculate Mean (Average)
    mean_gap = sum(gaps) / len(gaps)
    
    # Calculate Standard Deviation (variance indicator)
    variance = sum((x - mean_gap) ** 2 for x in gaps) / len(gaps)
    std_dev = math.sqrt(variance)
    
    print(f"📊 Statistical Profile of Municipal Spending Velocities:")
    print(f"  - Average Payment-to-Progress Discrepancy Gap (Mean): {mean_gap:.2f}%")
    print(f"  - Standard Deviation (Spending Variance):               {std_dev:.2f}%")
    print("-" * 80)
    
    anomalies = []
    # Identify outliers using Z-Score (Z > 1.0 for small test sample, typically > 2.0 in production)
    threshold = 1.0
    
    for record in data:
        gap = record["discrepancy_gap"]
        # Z-Score formula: Z = (x - mean) / std_dev
        z_score = (gap - mean_gap) / std_dev if std_dev > 0 else 0.0
        record["z_score"] = z_score
        
        if z_score > threshold:
            record["status"] = "⚠️ ANOMALY DETECTED"
            anomalies.append(record)
        else:
            record["status"] = "✅ NORMAL VARIANCE"
            
        print(f"Company: {record['company']:<32} | Gap: {gap:>5.1f}% | Z-Score: {z_score:>5.2f} | {record['status']}")
        
    print("-" * 80)
    print(f"🚨 Summary: Flagged {len(anomalies)} statistical anomalies for forensic audit.")
    for idx, anom in enumerate(anomalies):
        print(f"  Anomaly #{idx+1}: {anom['company']} on '{anom['work']}' (Z-Score: {anom['z_score']:.2f})")

def semantic_audit_company(company_name, work_description, api_key=None):
    """
    Uses Gemini LLM to audit if there is a semantic mismatch between a company name
    and the public service they were hired to do (detecting shell companies or front firms).
    """
    prompt = f"""
    You are a forensic public auditor examining municipal contracts.
    Analyze the following contract for potential corruption or front-company risks:
    - Company Name: "{company_name}"
    - Contracted Work Description: "{work_description}"
    
    Does this company name suggest that it actually does this type of work?
    (e.g., A company named "Distribuidora de Alimentos" hired to pave a street is a severe risk).
    
    Respond in JSON format with two keys:
    1. "risk_level": "RED" (severe mismatch), "YELLOW" (suspicious/unclear), or "GREEN" (fully consistent).
    2. "rationale": A brief explanation of your decision in Portuguese.
    """
    
    if not api_key:
        # Simulate local mock prediction if no API key is provided
        # This keeps the script fully executable and useful out-of-the-box
        lowered_name = company_name.lower()
        lowered_work = work_description.lower()
        
        if "previdência" in lowered_name and "praça" in lowered_work:
            risk = "RED"
            rationale = "Uma entidade de previdência social (IPSEM) não possui atividade econômica associada a reformas físicas de praças públicas."
        elif "boa vista" in lowered_name and "upa" in lowered_work:
            risk = "GREEN"
            rationale = "Construtoras são plenamente qualificadas para a construção física de Unidades de Pronto Atendimento (UPA)."
        elif "infraestrutura" in lowered_name and "pavimentação" in lowered_work:
            risk = "GREEN"
            rationale = "Empresas de infraestrutura são perfeitamente consistentes com a pavimentação de vias públicas."
        else:
            risk = "YELLOW"
            rationale = "Nome da empresa e escopo do contrato possuem relação plausível, mas requerem verificação de certidão de CNPJ."
            
        return {"risk_level": risk, "rationale": rationale, "is_mocked": True}

    # Make a live request to Google Gemini API
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "responseMimeType": "application/json"
        }
    }
    
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=15)
        r.raise_for_status()
        resp_data = r.json()
        text_content = resp_data["candidates"][0]["content"]["parts"][0]["text"]
        return json.loads(text_content)
    except Exception as e:
        return {"risk_level": "ERROR", "rationale": f"Gemini API request failed: {e}", "is_mocked": False}

def run_semantic_ai_audit():
    """Runs semantic audit across seeded contractors."""
    print("\n" + "="*80)
    print("🤖 LAYER 2: SEMANTIC LLM FORENSIC AUDITING (GEMINI AI)")
    print("="*80)
    
    # Retrieve GEMINI_API_KEY from environment if available
    api_key = os.environ.get("GEMINI_API_KEY")
    
    if not api_key:
        print("ℹ️ Note: GEMINI_API_KEY environment variable not set. Running in Mock-AI Simulation mode.")
        print("  To run live audits: export GEMINI_API_KEY='your_api_key'\n")
    else:
        print("🔋 Gemini API key detected! Making live forensic auditing calls...")
        
    test_cases = [
        ("IPSEM-INSTITUTO DE PREVIDÊNCIA", "Reforma da Praça da Bandeira"),
        ("CONSTRUTORA BOA VISTA LTDA", "Construção de UPA - Bairro das Nações"),
        ("INFRAESTRUTURA NORDESTE S.A.", "Pavimentação Bodocongó")
    ]
    
    for company, work in test_cases:
        print(f"Auditing: '{company}' hired for '{work}'...")
        result = semantic_audit_company(company, work, api_key)
        
        status_color = "🔴" if result["risk_level"] == "RED" else "🟡" if result["risk_level"] == "YELLOW" else "🟢"
        print(f"  - AI Risk Evaluation: {status_color} {result['risk_level']}")
        print(f"  - AI Rationale:        {result['rationale']}")
        if result.get("is_mocked"):
            print("  - [Engine]:            Local Simulation")
        print("-" * 80)

def generate_unusual_warning_blocks(db_path=None, api_key=None):
    """
    Uses Gemini LLM to analyze aggregated public spending anomalies and produce "Warning Blocks"
    starting exactly with "Isso é incomum: " highlighting suspicious topics.
    """
    target_db = db_path if db_path else (MAIN_DB if os.path.exists(MAIN_DB) else TEST_DB)
    if not os.path.exists(target_db):
        return []
        
    conn = sqlite3.connect(target_db)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # 1. Gather Obras anomalies
    obras_data = []
    try:
        cursor.execute("""
            SELECT 
                o.nome_obra AS work,
                cr.name AS company,
                o.valor_contratado AS hired,
                o.percentual_exec AS exec_percent,
                o.valor_pago_acum AS paid
            FROM obras o
            LEFT JOIN contratos c ON o.contrato_numero = c.numero_contrato
            LEFT JOIN creditors cr ON c.contratado_creditor_id = cr.id
            WHERE o.valor_contratado > 0
        """)
        obras_data = [dict(r) for r in cursor.fetchall()]
    except Exception:
        pass

    # 2. Gather Diárias anomalies
    diarias_data = []
    try:
        cursor.execute("""
            SELECT 
                nome_beneficiario AS name,
                cargo_servidor AS role,
                SUM(valor_pago) AS total_diarias,
                COUNT(*) AS num_diarias
            FROM diarias
            GROUP BY nome_beneficiario
            ORDER BY total_diarias DESC
            LIMIT 10
        """)
        diarias_data = [dict(r) for r in cursor.fetchall()]
    except Exception:
        pass

    # 3. Gather active debt / political / sanctioned crossings
    crossings_data = []
    try:
        cursor.execute("""
            SELECT 
                cr.name AS supplier_name,
                COALESCE(da.valor_devido, 0) AS active_debt,
                COALESCE(rp.doador_pf, 0) AS campaign_donation,
                COALESCE(s.tipo_sancao, 'Nenhuma') AS sanction,
                SUM(e.amount_empenhado) AS total_received
            FROM creditors cr
            LEFT JOIN divida_ativa da ON cr.id = da.creditor_id
            LEFT JOIN relacoes_politicas rp ON cr.id = rp.creditor_id
            LEFT JOIN sancoes s ON cr.id = s.creditor_id
            LEFT JOIN empenhos e ON cr.id = e.creditor_id
            GROUP BY cr.id
            HAVING active_debt > 0 OR campaign_donation > 0 OR sanction != 'Nenhuma'
        """)
        crossings_data = [dict(r) for r in cursor.fetchall()]
    except Exception:
        pass

    # 4. Gather direct procurement fracionamento
    fractioning_data = []
    try:
        cursor.execute("""
            SELECT 
                cr.name AS supplier_name,
                e.date_emission,
                el.name AS element_name,
                COUNT(*) AS num_empenhos,
                SUM(e.amount_empenhado) AS total_valor
            FROM empenhos e
            JOIN creditors cr ON e.creditor_id = cr.id
            JOIN expense_elements el ON e.element_code = el.code
            GROUP BY e.creditor_id, e.date_emission, e.element_code
            HAVING COUNT(*) > 1
            ORDER BY total_valor DESC
            LIMIT 10
        """)
        fractioning_data = [dict(r) for r in cursor.fetchall()]
    except Exception:
        pass

    conn.close()

    # If all is empty (e.g. database wiped and not seeded), return empty list
    if not any([obras_data, diarias_data, crossings_data, fractioning_data]):
        return []

    aggregated_data = {
        "obras_execucao_fisico_financeira": obras_data,
        "diarias_acumuladas_servidores": diarias_data,
        "cruzamentos_de_risco_fornecedores": crossings_data,
        "indicios_de_fracionamento": fractioning_data
    }

    if not api_key:
        # Simulate local mock predictions
        return [
            {
                "topic": "Físico-Financeiro de Obras",
                "text": "Isso é incomum: A obra 'Construção de UBS no Bairro das Cidades' da empresa CONSTRUTORA SAO JOSE LTDA possui R$ 1.900.000,00 pagos (97.4% do total contratado), mas apenas 40.0% de execução física realizada. Esse descompasso representa um risco crítico de medição indevida ou abandono de obra pública.",
                "data": {"obra": "Construção de UBS no Bairro das Cidades", "percentual_pago": "97.4%", "percentual_executado": "40.0%"}
            },
            {
                "topic": "Concentração de Diárias",
                "text": "Isso é incomum: O Secretário Executivo JOAO SANTOS realizou 5 viagens a Brasília/DF em um curto período, acumulando R$ 19.500,00 em diárias pagas. A frequência de viagens interestaduais para captação de recursos pela mesma pessoa excede os padrões usuais da administração.",
                "data": {"servidor": "JOAO SANTOS", "cargo": "Secretário Executivo", "total_diarias": 19500.0, "viagens": 5}
            },
            {
                "topic": "Fornecedor com Restrições",
                "text": "Isso é incomum: A empresa SANCIONADO E CONTRATADO LTDA (Credor C19) recebeu empenhos municipais mesmo constando com 'DECLARAÇÃO DE INIDONEIDADE' ativa aplicada pelo Tribunal de Contas da União. Contratar fornecedores inidôneos representa grave infração legal.",
                "data": {"fornecedor": "SANCIONADO E CONTRATADO LTDA", "sancao": "DECLARAÇÃO DE INIDONEIDADE", "tcu": True}
            },
            {
                "topic": "Dívida Ativa com Contratos",
                "text": "Isso é incomum: A empresa INFRAESTRUTURA NORDESTE S.A. (Credor C3) recebeu empenhos e possui contratos municipais ativos, ao mesmo tempo em que possui R$ 800.000,00 inscritos em Dívida Ativa municipal por IPTU em atraso. Há indício de inconsistência na regularidade fiscal exigida por lei.",
                "data": {"fornecedor": "INFRAESTRUTURA NORDESTE S.A.", "divida_ativa": 800000.0}
            }
        ]

    # Live request to Gemini API
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    
    prompt = f"""
    You are a forensic public auditor examining municipal transaction data.
    Examine the aggregated public spending anomalies below and identify any highly unusual, suspicious, or outlier patterns.
    
    Data to analyze:
    {json.dumps(aggregated_data, indent=2, ensure_ascii=False)}
    
    For each unusual thing you find (identify up to 5 items), generate a "Warning Block".
    Each Warning Block must be a short text block (2-4 sentences max) that starts EXACTLY with:
    "Isso é incomum: "
    
    Do NOT include long-winded explanations of public procurement laws or solutions, just highlight the anomaly and the key facts that make it stand out.
    
    Respond in JSON format with a single key "warnings" which is a list of objects, each containing:
    1. "topic": A short category name (e.g. "Discrepância em Obras", "Acúmulo de Diárias", "Fornecedor Sancionado").
    2. "text": The short warning text block starting exactly with "Isso é incomum: ...".
    3. "data": A small dictionary containing the specific raw values involved (e.g. {{"servidor": "X", "valor_diarias": 19500}}).
    """

    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "responseMimeType": "application/json"
        }
    }
    
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=15)
        r.raise_for_status()
        resp_data = r.json()
        text_content = resp_data["candidates"][0]["content"]["parts"][0]["text"]
        result_json = json.loads(text_content)
        return result_json.get("warnings", [])
    except Exception as e:
        return [{
            "topic": "Erro na API Gemini",
            "text": f"Isso é incomum: Falha ao tentar contato com o cérebro cognitivo da API Gemini. Motivo: {e}",
            "data": {"erro": str(e)}
        }]

def main():
    target_db = MAIN_DB if os.path.exists(MAIN_DB) else TEST_DB
    if not os.path.exists(target_db):
        print(f"Error: Neither database found at {MAIN_DB} or {TEST_DB}. Please run seed_analytics.py first.")
        return
        
    print(f"Running audits using database at: {target_db}")
    data = get_anomaly_data(db_path=target_db)
    run_statistical_anomaly_detection(data)
    run_semantic_ai_audit()
    
    print("\n" + "="*80)
    print("🧠 LAYER 3: COGNITIVE ANOMALY WARNING BLOCKS (GEMINI AI)")
    print("="*80)
    api_key = os.environ.get("GEMINI_API_KEY")
    warnings = generate_unusual_warning_blocks(db_path=target_db, api_key=api_key)
    for w in warnings:
        print(f"\n[Tópico: {w['topic']}]")
        print(f"  🚨 {w['text']}")
        print(f"  Dados envolvidos: {w['data']}")
        print("-" * 80)


if __name__ == "__main__":
    main()
