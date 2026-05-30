import pytest
import math
import sys
import os

# Insert src directory to path to load db, scraper, and ai_auditor
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from ai_auditor import run_statistical_anomaly_detection, semantic_audit_company

def test_statistical_outlier_math():
    """Verify that Z-Score anomaly detection calculations are mathematically correct."""
    # Controlled mock data: 3 balanced projects (gap 0%), 1 massive outlier (gap 100%)
    mock_data = [
        {"company": "A", "work": "Work A", "discrepancy_gap": 0.0},
        {"company": "B", "work": "Work B", "discrepancy_gap": 0.0},
        {"company": "C", "work": "Work C", "discrepancy_gap": 0.0},
        {"company": "D", "work": "Work D", "discrepancy_gap": 100.0} # Outlier!
    ]
    
    gaps = [r["discrepancy_gap"] for r in mock_data]
    
    # 1. Manually calculate statistical parameters
    # Mean: (0 + 0 + 0 + 100) / 4 = 25.0
    mean_gap = sum(gaps) / len(gaps)
    assert mean_gap == 25.0, f"Expected mean gap of 25.0, got {mean_gap}"
    
    # Variance: ((0-25)^2 + (0-25)^2 + (0-25)^2 + (100-25)^2) / 4
    # = (625 + 625 + 625 + 5625) / 4 = 7500 / 4 = 1875.0
    # Std Dev: sqrt(1875.0) ≈ 43.30127
    variance = sum((x - mean_gap) ** 2 for x in gaps) / len(gaps)
    std_dev = math.sqrt(variance)
    assert math.isclose(std_dev, 43.30127, rel_tol=1e-5), f"Standard deviation mismatch: {std_dev}"
    
    # 2. Run the detection logic
    run_statistical_anomaly_detection(mock_data)
    
    # Assert anomaly statuses and Z-scores
    # For Outlier D: Z = (100 - 25) / 43.30127 ≈ 1.732 (Should be > 1.0, flagged as anomaly)
    outlier = mock_data[3]
    assert outlier["status"] == "⚠️ ANOMALY DETECTED", "Extreme outlier was not flagged as anomaly"
    assert math.isclose(outlier["z_score"], 1.73205, rel_tol=1e-4)
    
    # For Normal A: Z = (0 - 25) / 43.30127 ≈ -0.577 (Should be <= 1.0, normal variance)
    normal = mock_data[0]
    assert normal["status"] == "✅ NORMAL VARIANCE"
    assert math.isclose(normal["z_score"], -0.57735, rel_tol=1e-4)

def test_semantic_ai_audit_schema():
    """Verify that the semantic AI auditor returns the correct JSON contract schema and risk logic."""
    # Test Anomaly Case: Pension fund hired for construction
    result_red = semantic_audit_company("IPSEM-INSTITUTO DE PREVIDÊNCIA", "Reforma de Praça", api_key=None)
    
    # Assert JSON schema/keys exist
    assert "risk_level" in result_red, "Result is missing risk_level key"
    assert "rationale" in result_red, "Result is missing rationale key"
    
    # Assert semantic logic flags
    assert result_red["risk_level"] == "RED", "Severe semantic mismatch was not flagged as RED"
    assert len(result_red["rationale"]) > 10, "AI rationale explanation is too short"
    
    # Test Normal Case: Construction company hired for construction
    result_green = semantic_audit_company("CONSTRUTORA BOA VISTA LTDA", "Construção de UPA", api_key=None)
    assert result_green["risk_level"] == "GREEN", "Normal compatible contract was not flagged as GREEN"
