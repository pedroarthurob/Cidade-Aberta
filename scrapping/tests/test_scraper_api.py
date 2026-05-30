import pytest
import requests
import json

BASE_URL = "https://transparencia.campinagrande.pb.gov.br"

def test_portal_connection():
    """Verify that the scraper can connect to the transparency portal home page."""
    url = f"{BASE_URL}/api/despesas"
    try:
        response = requests.get(url, timeout=15)
        assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
        assert "Portal da Transparência" in response.text or "Despesas" in response.text, "Could not find expected title in HTML"
    except requests.RequestException as e:
        pytest.fail(f"Failed to connect to the portal: {e}")

def test_session_cookies():
    """Verify that visiting the portal home page establishes a session with PHPSESSID cookie."""
    url = f"{BASE_URL}/api/despesas"
    session = requests.Session()
    try:
        session.get(url, timeout=15)
        cookies = session.cookies.get_dict()
        assert "PHPSESSID" in cookies, "PHPSESSID session cookie was not set by the server"
        assert len(cookies["PHPSESSID"]) > 0, "PHPSESSID cookie is empty"
    except requests.RequestException as e:
        pytest.fail(f"Failed to fetch session cookies: {e}")

def test_api_fetch_institutions():
    """Verify that the state-bound drill-down API returns correct JSON records."""
    session = requests.Session()
    
    # Step 1: Hit main page to establish cookies
    session.get(f"{BASE_URL}/api/despesas", timeout=15)
    
    # Step 2: Inject filter parameters in session state (imitative of jQuery $.ajax)
    load_url = f"{BASE_URL}/api/despesas/loadLink/1"
    form_data = {
        'iExercicio': '2022',
        'dtDataImportacao': '2022-12-31',
        'sViewAtual': '',
        'iNivel': '3',
        'dtInicio': '01/01',
        'dtFim': '31/12',
        'iIdLink': '1',
        'aHistorico[0][descricao]': 'Descrição',
        'aHistorico[0][valor_empenhado]': 'Valor Empenhado',
        'aHistorico[0][valor_anulado]': 'Valor Anulado',
        'aHistorico[0][valor_liquidado]': 'Valor Liquidado',
        'aHistorico[0][valor_pago]': 'Valor Pago'
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'X-Requested-With': 'XMLHttpRequest',
        'Origin': BASE_URL,
        'Referer': f'{BASE_URL}/api/despesas'
    }
    
    load_resp = session.post(load_url, data=form_data, headers=headers, timeout=15)
    assert load_resp.status_code == 200, "Failed to initialize query filters in session state"
    
    # Step 3: Query the JSON backend endpoint getInstit
    grid_url = f"{BASE_URL}/api/despesas/getInstit"
    oParametros = {
        "iExercicio": "2022",
        "dtDataImportacao": "2022-12-31",
        "sViewAtual": "instituicoes",
        "iNivel": "3",
        "dtInicio": "01/01",
        "dtFim": "31/12",
        "aHistorico": [{
            "descricao": "Descrição",
            "valor_empenhado": "Valor Empenhado",
            "valor_anulado": "Valor Anulado",
            "valor_liquidado": "Valor Liquidado",
            "valor_pago": "Valor Pago"
        }],
        "iIdLink": "1"
    }
    
    grid_data = {
        'aParametros': json.dumps(oParametros),
        'page': '1',
        'rows': '50',
        'sidx': 'descricao',
        'sord': 'asc'
    }
    
    r = session.post(grid_url, data=grid_data, headers=headers, timeout=15)
    assert r.status_code == 200, f"Expected 200 OK from getInstit, got {r.status_code}"
    
    # Step 4: Validate JSON structure of the API response
    try:
        data = r.json()
        assert "rows" in data, "JSON payload is missing the 'rows' key"
        assert "total" in data, "JSON payload is missing the 'total' key"
        assert "records" in data, "JSON payload is missing the 'records' key"
        
        # Verify that we actually received valid records
        assert data["records"] > 0, "No records returned in JSON"
        assert len(data["rows"]) > 0, "The 'rows' array is empty"
        
        # Verify first row structure
        first_row = data["rows"][0]
        assert "id" in first_row, "Row dictionary is missing the unique 'id' key"
        assert "cell" in first_row, "Row dictionary is missing the 'cell' list"
        assert len(first_row["cell"]) >= 5, "Row cell does not contain the 5 expected columns"
        
    except json.JSONDecodeError:
        pytest.fail("Failed to parse response payload as valid JSON")
