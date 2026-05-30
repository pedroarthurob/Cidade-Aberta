import pytest
import os
import sys

# Append source directory to path to locate our modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from analyzer import CidadeAbertaAnalyzer

# Use the seeded database in the transparency data directory
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/transparencia_cg.db"))

@pytest.fixture
def analyzer():
    """Returns an instance of CidadeAbertaAnalyzer using the real seeded database."""
    return CidadeAbertaAnalyzer(db_path=DB_PATH)

def test_supplier_ranking(analyzer):
    ranking = analyzer.get_supplier_ranking()
    assert isinstance(ranking, list), "Ranking should be a list"
    assert len(ranking) > 0, "Seeded ranking should not be empty"
    # Validate structure
    first = ranking[0]
    assert "creditor_id" in first
    assert "supplier_name" in first
    assert "total_empenhado" in first
    assert "total_pago" in first

def test_procurement_patterns(analyzer):
    patterns = analyzer.get_procurement_patterns()
    assert isinstance(patterns, dict)
    assert "direct_ranking" in patterns
    assert "fractioning_alerts" in patterns
    
    assert isinstance(patterns["direct_ranking"], list)
    assert isinstance(patterns["fractioning_alerts"], list)
    assert len(patterns["direct_ranking"]) > 0, "Should have direct ranking records"
    assert len(patterns["fractioning_alerts"]) > 0, "Should detect fractional spending alerts"

def test_monopolies_by_category(analyzer):
    monopolies = analyzer.get_monopolies_by_category()
    assert isinstance(monopolies, list)
    assert len(monopolies) > 0
    first = monopolies[0]
    assert "categoria" in first
    assert "creditor_name" in first
    assert "total_gasto" in first

def test_health_spending_analysis(analyzer):
    health = analyzer.get_health_spending_analysis()
    assert isinstance(health, list)
    assert len(health) > 0
    assert health[0]["total_empenhado"] > 0

def test_education_spending_analysis(analyzer):
    edu = analyzer.get_education_spending_analysis()
    assert isinstance(edu, list)
    assert len(edu) > 0
    assert edu[0]["total_empenhado"] > 0

def test_publicity_spending(analyzer):
    pub = analyzer.get_publicity_spending()
    assert isinstance(pub, list)
    assert len(pub) > 0
    assert "agency_name" in pub[0]
    assert "vehicle" in pub[0]
    assert "total_pago" in pub[0]

def test_sao_joao_events(analyzer):
    sao_joao = analyzer.get_sao_joao_events_analysis()
    assert isinstance(sao_joao, list)
    assert len(sao_joao) > 0
    assert "supplier_name" in sao_joao[0]
    assert "contract_value" in sao_joao[0]

def test_travel_diarias(analyzer):
    diarias = analyzer.get_travel_diarias_analysis()
    assert isinstance(diarias, list)
    assert len(diarias) > 0
    assert "servant_name" in diarias[0]
    assert "amount_paid" in diarias[0]

def test_payroll_staff(analyzer):
    payroll = analyzer.get_payroll_staff_analysis()
    assert isinstance(payroll, dict)
    assert "staff_structure" in payroll
    assert "outsourced_spent" in payroll
    assert len(payroll["staff_structure"]) > 0

def test_fleet_fuel_efficiency(analyzer):
    fleet = analyzer.get_fleet_fuel_efficiency()
    assert isinstance(fleet, list)
    assert len(fleet) > 0
    assert "plate" in fleet[0]
    assert "spent_fuel" in fleet[0]

def test_ngo_partnerships(analyzer):
    ngos = analyzer.get_ngo_partnerships_analysis()
    assert isinstance(ngos, list)
    assert len(ngos) > 0
    assert "entity_name" in ngos[0]
    assert "total_value" in ngos[0]

def test_amendment_pathway(analyzer):
    pathway = analyzer.get_amendment_pathway()
    assert isinstance(pathway, list)
    assert len(pathway) > 0
    assert "politician_name" in pathway[0]
    assert "amendment_value" in pathway[0]

def test_active_debt_crossings(analyzer):
    crossings = analyzer.get_active_debt_crossings()
    assert isinstance(crossings, list)
    assert len(crossings) > 0
    assert "active_debt_amount" in crossings[0]

def test_sanctioned_supplier_crossings(analyzer):
    crossings = analyzer.get_sanctioned_supplier_crossings()
    assert isinstance(crossings, list)
    assert len(crossings) > 0
    assert "sanction_type" in crossings[0]

def test_political_connections(analyzer):
    connections = analyzer.get_political_connections()
    assert isinstance(connections, list)
    assert len(connections) > 0
    assert "partner_name" in connections[0]
    assert "pf_donation" in connections[0]

def test_network_graph(analyzer):
    graph = analyzer.get_network_graph_data()
    assert isinstance(graph, dict)
    assert "nodes" in graph
    assert "edges" in graph
    assert len(graph["nodes"]) > 0
    assert len(graph["edges"]) > 0

def test_top_highlights(analyzer):
    hl = analyzer.get_top_highlights()
    assert isinstance(hl, dict)
    assert "top_suppliers" in hl
    assert "fractioning_count" in hl

def test_forensic_research_summary(analyzer):
    forensic = analyzer.get_forensic_research_summary()
    assert isinstance(forensic, list)
    assert len(forensic) > 0
    assert "active_debt" in forensic[0]
    assert "campaign_donation" in forensic[0]

def test_scraper_errors_summary(analyzer):
    err = analyzer.get_scraper_errors_summary()
    assert isinstance(err, dict)
    assert "total_errors" in err
    assert "by_level" in err
    assert "recent_samples" in err

