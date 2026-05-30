import sqlite3
import os
import math
import json
import requests

TEST_DB = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/audit_test.db"))

def get_anomaly_data():
    """Fetches payment-to-progress discrepancy gaps from the database."""
    conn = sqlite3.connect(TEST_DB)
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

def main():
    if not os.path.exists(TEST_DB):
        print(f"Error: Test database not found at {TEST_DB}. Please run test_audit.py first to seed the data.")
        return
        
    data = get_anomaly_data()
    run_statistical_anomaly_detection(data)
    run_semantic_ai_audit()

if __name__ == "__main__":
    main()
