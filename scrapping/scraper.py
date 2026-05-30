import requests
import json
import logging
import time
import os
import sys

# Import our database module
from db import (
    get_connection, init_db, save_institution, save_organ,
    save_creditor, save_expense_element, save_empenho, save_movement
)

# Configure logging to show progress beautifully
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("cg_transparencia_scraper")

BASE_URL = "https://transparencia.campinagrande.pb.gov.br"

def to_float(val):
    """Converts a formatting-ridden string (e.g. 664.544.546,30) to a clean float."""
    if not val:
        return 0.0
    try:
        val_str = str(val).strip()
        if "," not in val_str:
            return float(val_str)
        # Brazilian standard conversion
        val_str = val_str.replace(".", "").replace(",", ".")
        return float(val_str)
    except Exception:
        return 0.0

def serialize_historico(historico):
    """Formats the python dictionary array of aHistorico into POST form fields."""
    data = {}
    for idx, item in enumerate(historico):
        for k, v in item.items():
            data[f"aHistorico[{idx}][{k}]"] = str(v)
    return data

class CampinaGrandeScraper:
    def __init__(self, year=2022, start_date="01/01", end_date="31/12"):
        self.year = year
        self.start_date = start_date
        self.end_date = end_date
        self.session = requests.Session()
        
        # Headers mimicking a standard XMLHttpRequest to bypass basic protections
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.0.0 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest',
            'Origin': BASE_URL,
            'Referer': f'{BASE_URL}/api/despesas'
        }
        
        # The base session parameters dictionary used for jqGrid POST bodies
        self.base_parametros = {
            "iExercicio": str(self.year),
            "dtDataImportacao": f"{self.year}-12-31",
            "sViewAtual": "instituicoes",
            "iNivel": "3",
            "dtInicio": self.start_date,
            "dtFim": self.end_date,
            "aHistorico": [{
                "descricao": "Descrição",
                "valor_empenhado": "Valor Empenhado",
                "valor_anulado": "Valor Anulado",
                "valor_liquidado": "Valor Liquidado",
                "valor_pago": "Valor Pago"
            }],
            "iIdLink": "1"
        }
        
        # Initialize initial state history
        self.base_historico = [{
            "descricao": "Descrição",
            "valor_empenhado": "Valor Empenhado",
            "valor_anulado": "Valor Anulado",
            "valor_liquidado": "Valor Liquidado",
            "valor_pago": "Valor Pago"
        }]

    def init_session(self):
        """Hits the parent page to establish session state and download cookies."""
        logger.info("Initializing session cookies...")
        r = self.session.get(f"{BASE_URL}/api/despesas", timeout=15)
        r.raise_for_status()
        logger.info(f"Session established. Cookies: {self.session.cookies.get_dict()}")

    def _post_load_link(self, view_name, nivel, extra_params=None, historico=None):
        """Simulates a double-click/drilldown change in the PHP session state."""
        url = f"{BASE_URL}/api/despesas/loadLink/1"
        
        form_data = {
            'iExercicio': str(self.year),
            'dtDataImportacao': f'{self.year}-12-31',
            'sViewAtual': view_name,
            'iNivel': str(nivel),
            'dtInicio': self.start_date,
            'dtFim': self.end_date,
            'iIdLink': '1'
        }
        
        if extra_params:
            form_data.update(extra_params)
            
        hist = historico if historico else self.base_historico
        form_data.update(serialize_historico(hist))
        
        logger.debug(f"POST loadLink/{nivel} for {view_name}...")
        r = self.session.post(url, data=form_data, headers=self.headers, timeout=15)
        r.raise_for_status()
        return r.text

    def scrape_all(self, db_conn, limit_institutions=None, limit_organs=None, 
                   limit_elements=None, limit_credores=None, limit_empenhos=None):
        """Runs the complete nested scraper crawling pipeline."""
        
        self.init_session()
        
        # --- LEVEL 3: INSTITUTIONS ---
        # 1. Establish Level 3 inside PHP Session
        self._post_load_link(view_name="", nivel=3)
        
        # 2. Query JSON data of institutions
        logger.info("Fetching institutions (Level 3)...")
        grid_params = {
            'aParametros': json.dumps(self.base_parametros),
            'page': '1',
            'rows': '100',
            'sidx': 'descricao',
            'sord': 'asc'
        }
        
        r = self.session.post(f"{BASE_URL}/api/despesas/getInstit", data=grid_params, headers=self.headers, timeout=15)
        r.raise_for_status()
        instit_data = r.json()
        rows = instit_data.get("rows", [])
        logger.info(f"Found {len(rows)} institutions.")
        
        if limit_institutions:
            rows = rows[:limit_institutions]
            
        for inst_row in rows:
            inst_id = int(inst_row["id"])
            cell = inst_row["cell"]
            inst_name = cell[0]
            
            logger.info(f"[*] Scraping Institution ID {inst_id}: '{inst_name}'")
            save_institution(db_conn, inst_id, inst_name)
            
            # --- LEVEL 4: ORGANS ---
            # Click row to enter Level 4
            hist_4 = self.base_historico + [{
                "descricao": inst_name,
                "valor_empenhado": cell[1],
                "valor_anulado": cell[2],
                "valor_liquidado": cell[3],
                "valor_pago": cell[4]
            }]
            
            self._post_load_link(view_name="instituicoes", nivel=4, 
                                 extra_params={'iInstituicao': str(inst_id)}, 
                                 historico=hist_4)
            
            # Query Organs
            o_params = self.base_parametros.copy()
            o_params.update({
                "sViewAtual": "instituicoes",
                "iNivel": "4",
                "iInstituicao": str(inst_id),
                "aHistorico": hist_4
            })
            
            grid_params_o = {
                'aParametros': json.dumps(o_params),
                'page': '1',
                'rows': '100',
                'sidx': 'descricao',
                'sord': 'asc'
            }
            
            r_o = self.session.post(f"{BASE_URL}/api/despesas/getOrgao", data=grid_params_o, headers=self.headers, timeout=15)
            r_o.raise_for_status()
            organs_rows = r_o.json().get("rows", [])
            logger.info(f"  Found {len(organs_rows)} organs under '{inst_name}'.")
            
            if limit_organs:
                organs_rows = organs_rows[:limit_organs]
                
            for org_row in organs_rows:
                org_cell = org_row["cell"]
                org_name = org_cell[0]
                org_code = org_cell[5] # hidden codorgao column
                
                logger.info(f"  [-] Scraping Organ Code {org_code}: '{org_name}'")
                save_organ(db_conn, org_code, org_name, inst_id)
                db_conn.commit()
                
                # --- LEVEL 5: EXPENSE ELEMENTS ---
                # Click row to enter Level 5
                hist_5 = hist_4 + [{
                    "descricao": org_name,
                    "valor_empenhado": org_cell[1],
                    "valor_anulado": org_cell[2],
                    "valor_liquidado": org_cell[3],
                    "valor_pago": org_cell[4],
                    "codorgao": org_code
                }]
                
                self._post_load_link(view_name="orgaos", nivel=5,
                                     extra_params={'iInstituicao': str(inst_id), 'iOrgao': org_code},
                                     historico=hist_5)
                
                # Query Elements
                el_params = o_params.copy()
                el_params.update({
                    "sViewAtual": "orgaos",
                    "iNivel": "5",
                    "iOrgao": org_code,
                    "aHistorico": hist_5
                })
                
                grid_params_el = {
                    'aParametros': json.dumps(el_params),
                    'page': '1',
                    'rows': '200', # load all elements at once
                    'sidx': 'descricao',
                    'sord': 'asc'
                }
                
                r_el = self.session.post(f"{BASE_URL}/api/despesas/getElementos", data=grid_params_el, headers=self.headers, timeout=15)
                r_el.raise_for_status()
                el_rows = r_el.json().get("rows", [])
                logger.info(f"    Found {len(el_rows)} expense elements under organ '{org_name}'.")
                
                if limit_elements:
                    el_rows = el_rows[:limit_elements]
                    
                for el_row in el_rows:
                    el_cell = el_row["cell"]
                    el_group = el_cell[0]
                    el_name = el_cell[1]
                    el_code = el_cell[6] # hidden codcon column
                    
                    logger.info(f"    [+] Expense Element Code {el_code}: '{el_name}'")
                    save_expense_element(db_conn, el_code, el_group, el_name, el_code)
                    db_conn.commit()
                    
                    # --- LEVEL 6: CREDITORS ---
                    # Click row to enter Level 6
                    hist_6 = hist_5 + [{
                        "grupo": el_group,
                        "descricao": el_name,
                        "valor_empenhado": el_cell[2],
                        "valor_anulado": el_cell[3],
                        "valor_liquidado": el_cell[4],
                        "valor_pago": el_cell[5],
                        "codcon": el_code
                    }]
                    
                    self._post_load_link(view_name="elementos", nivel=6,
                                         extra_params={'iInstituicao': str(inst_id), 'iOrgao': org_code, 'iElemento': el_code},
                                         historico=hist_6)
                    
                    # Query Creditors
                    cred_params = el_params.copy()
                    cred_params.update({
                        "sViewAtual": "elementos",
                        "iNivel": "6",
                        "iElemento": el_code,
                        "aHistorico": hist_6
                    })
                    
                    grid_params_cred = {
                        'aParametros': json.dumps(cred_params),
                        'page': '1',
                        'rows': '100',
                        'sidx': 'nome',
                        'sord': 'asc'
                    }
                    
                    r_cred = self.session.post(f"{BASE_URL}/api/despesas/getCredores", data=grid_params_cred, headers=self.headers, timeout=15)
                    r_cred.raise_for_status()
                    cred_rows = r_cred.json().get("rows", [])
                    logger.info(f"      Found {len(cred_rows)} creditors under '{el_name}'.")
                    
                    if limit_credores:
                        cred_rows = cred_rows[:limit_credores]
                        
                    for cred_row in cred_rows:
                        cred_id = cred_row["id"]
                        cred_cell = cred_row["cell"]
                        cred_cpf = cred_cell[0]
                        cred_nome = cred_cell[1]
                        
                        logger.info(f"      [*] Creditor ID {cred_id}: '{cred_nome}'")
                        save_creditor(db_conn, cred_id, cred_cpf, cred_nome)
                        db_conn.commit()
                        
                        # --- LEVEL 7: EMPENHOS ---
                        # Click row to enter Level 7
                        hist_7 = hist_6 + [{
                            "cpfcnpj": cred_cpf,
                            "nome": cred_nome,
                            "valor_empenhado": cred_cell[2],
                            "valor_anulado": cred_cell[3],
                            "valor_liquidado": cred_cell[4],
                            "valor_pago": cred_cell[5],
                            "descricao": f"{cred_cpf} - {cred_nome}"
                        }]
                        
                        self._post_load_link(view_name="credores", nivel=7,
                                             extra_params={'iInstituicao': str(inst_id), 'iOrgao': org_code, 'iElemento': el_code, 'iCredor': cred_id},
                                             historico=hist_7)
                        
                        # Query Empenhos
                        emp_params = cred_params.copy()
                        emp_params.update({
                            "sViewAtual": "credores",
                            "iNivel": "7",
                            "iCredor": cred_id,
                            "aHistorico": hist_7
                        })
                        
                        grid_params_emp = {
                            'aParametros': json.dumps(emp_params),
                            'page': '1',
                            'rows': '100',
                            'sidx': 'codempenho',
                            'sord': 'desc'
                        }
                        
                        r_emp = self.session.post(f"{BASE_URL}/api/despesas/getEmpenhos", data=grid_params_emp, headers=self.headers, timeout=15)
                        r_emp.raise_for_status()
                        emp_rows = r_emp.json().get("rows", [])
                        logger.info(f"        Found {len(emp_rows)} empenhos for '{cred_nome}'.")
                        
                        if limit_empenhos:
                            emp_rows = emp_rows[:limit_empenhos]
                            
                        for emp_row in emp_rows:
                            emp_id = emp_row["id"]
                            emp_cell = emp_row["cell"]
                            emp_human_code = emp_cell[0] # human readable code (e.g. 2934 / 2022)
                            emp_date = emp_cell[7]       # YYYY-MM-DD
                            
                            logger.info(f"        [-] Empenho ID {emp_id}: '{emp_human_code}' ({emp_date})")
                            
                            # --- LEVEL 8: MOVE-MENTS & BUDGET ALLOCATIONS ---
                            # Click row to enter Level 8
                            hist_8 = hist_7 + [{
                                "codempenho": emp_human_code,
                                "funcao_descricao": emp_cell[1],
                                "subfuncao_descricao": emp_cell[2],
                                "programa_descricao": emp_cell[3],
                                "projeto_descricao": emp_cell[4],
                                "planoconta_descricao": emp_cell[5],
                                "recurso_descricao": emp_cell[6],
                                "dataemissao": emp_date,
                                "valor_empenhado": emp_cell[8],
                                "valor_anulado": emp_cell[9],
                                "valor_liquidado": emp_cell[10],
                                "valor_pago": emp_cell[11],
                                "descricao": f"EMPENHO : {emp_id}"
                            }]
                            
                            self._post_load_link(view_name="empenhos", nivel=8,
                                                 extra_params={'iInstituicao': str(inst_id), 'iOrgao': org_code, 'iElemento': el_code, 'iCredor': cred_id, 'iEmpenho': emp_id},
                                                 historico=hist_8)
                            
                            # Query Detailed Movements & Allocations
                            detail_params = emp_params.copy()
                            detail_params.update({
                                "sViewAtual": "empenhos_movimentacoes",
                                "iNivel": "8",
                                "iEmpenho": emp_id,
                                "aHistorico": hist_8
                            })
                            
                            grid_params_det = {
                                'aParametros': json.dumps(detail_params),
                                'page': '1',
                                'rows': '100',
                                'sidx': 'data',
                                'sord': 'asc'
                            }
                            
                            # 1. Fetch budget allocation code details
                            r_alloc = self.session.post(f"{BASE_URL}/api/despesas/getDotacaoEmpenho", data=grid_params_det, headers=self.headers, timeout=15)
                            r_alloc.raise_for_status()
                            alloc_rows = r_alloc.json().get("rows", [])
                            
                            # Map allocation codes
                            alloc_map = {}
                            for alloc in alloc_rows:
                                cell_data = alloc["cell"]
                                label = cell_data[0].lower().replace(" ", "").replace("/", "").replace("-", "")
                                code = cell_data[1]
                                name = cell_data[2]
                                alloc_map[label] = {"code": code, "name": name}
                            
                            # Extract resolved attributes
                            unit_code = alloc_map.get("unidade", {}).get("code", "")
                            unit_name = alloc_map.get("unidade", {}).get("name", "")
                            func_code = alloc_map.get("função", {}).get("code", "")
                            func_name = alloc_map.get("função", {}).get("name", "")
                            subfunc_code = alloc_map.get("subfunção", {}).get("code", "")
                            subfunc_name = alloc_map.get("subfunção", {}).get("name", "")
                            prog_code = alloc_map.get("programa", {}).get("code", "")
                            prog_name = alloc_map.get("programa", {}).get("name", "")
                            proj_code = alloc_map.get("projetoatividade", {}).get("code", "")
                            proj_name = alloc_map.get("projetoatividade", {}).get("name", "")
                            res_code = alloc_map.get("recurso", {}).get("code", "")
                            res_name = alloc_map.get("recurso", {}).get("name", "")
                            
                            # Assemble the complete detailed Empenho record
                            empenho_db_data = {
                                "id": emp_id,
                                "code": emp_human_code,
                                "exercicio": self.year,
                                "institution_id": inst_id,
                                "organ_code": org_code,
                                "unit_code": unit_code,
                                "unit_name": unit_name,
                                "function_code": func_code,
                                "function_name": func_name,
                                "subfunction_code": subfunc_code,
                                "subfunction_name": subfunc_name,
                                "program_code": prog_code,
                                "program_name": prog_name,
                                "project_code": proj_code,
                                "project_name": proj_name,
                                "element_code": el_code,
                                "creditor_id": cred_id,
                                "resource_code": res_code,
                                "resource_name": res_name,
                                "date_emission": emp_date,
                                "amount_empenhado": to_float(emp_cell[8]),
                                "amount_anulado": to_float(emp_cell[9]),
                                "amount_liquidado": to_float(emp_cell[10]),
                                "amount_pago": to_float(emp_cell[11])
                            }
                            
                            save_empenho(db_conn, empenho_db_data)
                            db_conn.commit()
                            
                            # 2. Fetch movements (Empenho, Liquidação, Pagamentos ledger)
                            r_mov = self.session.post(f"{BASE_URL}/api/despesas/getMovimentacoesEmpenhos", data=grid_params_det, headers=self.headers, timeout=15)
                            r_mov.raise_for_status()
                            mov_rows = r_mov.json().get("rows", [])
                            
                            for mov_row in mov_rows:
                                mov_id = mov_row["id"]
                                mov_cell = mov_row["cell"]
                                mov_date = mov_cell[0]
                                mov_type = mov_cell[1]
                                mov_amount = to_float(mov_cell[2])
                                mov_type_code = int(mov_cell[3])
                                
                                logger.info(f"          [Movement] {mov_date} | {mov_type:<10} | R$ {mov_amount:,.2f}")
                                save_movement(db_conn, mov_id, emp_id, mov_date, mov_type, mov_amount, mov_type_code)
                            db_conn.commit()
                            
                            # Sleep briefly to avoid putting too much load on the city server
                            time.sleep(0.1)

if __name__ == "__main__":
    logger.info("Initializing SQLite database...")
    init_db()
    
    # Establish database connection
    db_conn = get_connection()
    
    # We do a fast "dry run" with small limits so it demonstrates full functionality in a few seconds
    logger.info("Running a fast limited scrape dry-run for 2022 data...")
    scraper = CampinaGrandeScraper(year=2022, start_date="01/01", end_date="31/12")
    
    try:
        scraper.scrape_all(
            db_conn,
            limit_institutions=1, # Only PREFEITURA
            limit_organs=1,       # Only PMCG
            limit_elements=2,     # Scrape only 2 expense elements (e.g. Diárias, etc.)
            limit_credores=2,     # Scrape 2 creditors per element
            limit_empenhos=2      # Scrape 2 empenhos per creditor
        )
        logger.info("Limited dry-run scrape completed successfully!")
        
        # Print database quick stats
        print("\n=== Database Quick Stats ===")
        cursor = db_conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM institutions")
        print(f"Institutions: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM organs")
        print(f"Organs: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM expense_elements")
        print(f"Expense Elements: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM creditors")
        print(f"Creditors: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM empenhos")
        print(f"Empenhos (Contracts): {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM movements")
        print(f"Transaction Movements: {cursor.fetchone()[0]}")
        
    except Exception as e:
        logger.exception("Scraper encountered an error:")
    finally:
        db_conn.close()
