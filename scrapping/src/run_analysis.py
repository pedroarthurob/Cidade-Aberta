import os
import sys
import json
from analyzer import CidadeAbertaAnalyzer
from ai_auditor import run_statistical_anomaly_detection, run_semantic_ai_audit, get_anomaly_data, generate_unusual_warning_blocks

# Ensure standard output uses UTF-8 to handle PT-BR characters cleanly in console
sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None

# Terminal color constants
BLUE = "\033[94m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
RESET = "\033[0m"
CYAN = "\033[96m"

def fmt_currency(val):
    """Formats float value into standard PT-BR currency representation (R$ X.XXX,XX)."""
    if val is None:
        return "R$ 0,00"
    return f"R$ {val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def print_header(title):
    print("\n" + "="*80)
    print(f" {BOLD}{BLUE}{title}{RESET}")
    print("="*80)

def print_table(headers, rows, col_widths, alignments=None):
    """
    Renders a beautiful ASCII table with clean borders.
    - alignments: list of 'L' or 'R' representing Left or Right alignment for each column.
    """
    if not alignments:
        alignments = ['L'] * len(headers)
        
    # Render header row
    header_parts = []
    for h, w, a in zip(headers, col_widths, alignments):
        if a == 'R':
            header_parts.append(h.rjust(w)[:w])
        else:
            header_parts.append(h.ljust(w)[:w])
    print(f"| {' | '.join(header_parts)} |")
    print("|" + "|".join(["-" * (w + 2) for w in col_widths]) + "|")
    
    # Render data rows
    for row in rows:
        row_parts = []
        for cell, w, a in zip(row, col_widths, alignments):
            cell_str = str(cell)
            if a == 'R':
                row_parts.append(cell_str.rjust(w)[:w])
            else:
                row_parts.append(cell_str.ljust(w)[:w])
        print(f"| {' | '.join(row_parts)} |")

def main():
    analyzer = CidadeAbertaAnalyzer()
    
    while True:
        print("\n" + "╔" + "═"*78 + "╗")
        print(f"║ {BOLD}{CYAN}SISTEMA CIVICO CIDADE ABERTA - CAMPINA GRANDE (PB){RESET}                             ║")
        print(f"║ {BOLD}{YELLOW}PAINEL INTERATIVO DE AUDITORIAS E ANALISES CIVICAS{RESET}                             ║")
        print("╠" + "═"*78 + "╣")
        print("║ Escolha uma das análises e auditorias disponíveis:                           ║")
        print("║                                                                              ║")
        print("║  1. Ranking Geral de Fornecedores da Prefeitura                              ║")
        print("║  2. Padrão de Contratação Direta (Dispensas / Inexigibilidades)               ║")
        print("║  3. Monopólios e Dominância por Categorias de Gasto                          ║")
        print("║  4. Auditoria de Gastos com Saúde                                            ║")
        print("║  5. Auditoria de Gastos com Educação                                         ║")
        print("║  6. Despesas com Publicidade Institucional                                   ║")
        print("║  7. Gastos com Eventos, Cultura e São João                                   ║")
        print("║  8. Diárias e Passagens de Servidores                                        ║")
        print("║  9. Proporção de Terceirizações, Temporários e Quadro Funcional              ║")
        print("║ 10. Custos e Consumo de Combustível da Frota                                 ║")
        print("║ 11. Repasses para ONGs e Organizações Sociais                                ║")
        print("║ 12. Rastreamento de Emendas Parlamentares                                    ║")
        print("║ 13. Cruzamento de Contratos com Dívida Ativa                                 ║")
        print("║ 14. Monitoramento de Licitantes Sancionados                                  ║")
        print("║ 15. Relações Políticas (TSE / Quadro Societário / Doadores)                  ║")
        print("║ 16. Estrutura de Redes (Nós e Conexões para Grafos JSON)                     ║")
        print("║ 17. Dashboard Geral (Melhores Análises Integradas)                           ║")
        print("║ 18. Recorte de Pesquisa / Auditoria Forense Integrada                        ║")
        print("║ 19. Executar Auditoria com Inteligência Artificial (Outliers & Semântica)    ║")
        print("║ 20. Auditoria de Qualidade de Dados (Erros & Lacunas do Portal)              ║")
        print("║  0. Sair do Painel                                                           ║")
        print("╚" + "═"*78 + "╝")

        
        try:
            choice = input(f"{BOLD}Digite o número da opção desejada: {RESET}").strip()
        except KeyboardInterrupt:
            print("\nEncerrando...")
            break
            
        if choice == '0':
            print("Saindo do painel Cidade Aberta. Até logo!")
            break
            
        elif choice == '1':
            print_header("RANKING GERAL DE FORNECEDORES DA PREFEITURA")
            ranking = analyzer.get_supplier_ranking()
            headers = ["CNPJ/CPF", "Fornecedor", "Empenhos", "Contratos", "Secs", "Total Empenhado", "Total Pago"]
            col_widths = [18, 25, 8, 9, 4, 16, 16]
            alignments = ['L', 'L', 'R', 'R', 'R', 'R', 'R']
            rows = []
            for r in ranking[:15]:  # show top 15
                rows.append([
                    r["cpf_cnpj"] or "N/D",
                    r["supplier_name"][:25],
                    str(r["num_empenhos"]),
                    str(r["num_contratos"]),
                    str(r["num_secretarias"]),
                    fmt_currency(r["total_empenhado"]),
                    fmt_currency(r["total_pago"])
                ])
            print_table(headers, rows, col_widths, alignments)
            
        elif choice == '2':
            print_header("PADRÃO DE CONTRATAÇÃO: CONTRATAÇÃO DIRETA E APURAÇÃO DE FRACIONAMENTO")
            patterns = analyzer.get_procurement_patterns()
            
            print(f"\n{BOLD}{YELLOW}A. Empresas que mais faturam por Contratação Direta (Dispensas / Inexigibilidades):{RESET}")
            direct = patterns["direct_ranking"]
            if not direct:
                print("Nenhum registro de contratação direta encontrado.")
            else:
                headers = ["CNPJ", "Empresa", "Dispensas", "Inexig", "Valor Total", "Secretarias"]
                col_widths = [18, 30, 9, 6, 16, 25]
                alignments = ['L', 'L', 'R', 'R', 'R', 'L']
                rows = []
                for r in direct[:10]:
                    rows.append([
                        r["cnpj"] or "N/D",
                        r["supplier_name"][:30],
                        str(r["num_dispensas"]),
                        str(r["num_inexigibilidades"]),
                        fmt_currency(r["total_valor"]),
                        r["secretarias"][:25] if r["secretarias"] else ""
                    ])
                print_table(headers, rows, col_widths, alignments)
                
            print(f"\n{BOLD}{RED}B. Alertas de Fracionamento Suspeito de Despesas (Mesmo Fornecedor / Mesma Data):{RESET}")
            alerts = patterns["fractioning_alerts"]
            if not alerts:
                print("✅ Nenhum indício óbvio de fracionamento de despesa detectado nos limites legais.")
            else:
                headers = ["Fornecedor", "Data Emissão", "Elemento", "Qtd", "Total Acumulado", "Descrição Objetos"]
                col_widths = [28, 12, 10, 3, 16, 25]
                alignments = ['L', 'L', 'L', 'R', 'R', 'L']
                rows = []
                for r in alerts[:10]:
                    rows.append([
                        r["supplier_name"][:28],
                        r["date_emission"],
                        r["element_code"],
                        str(r["num_ocorrencias"]),
                        fmt_currency(r["total_valor"]),
                        r["objetos"][:25]
                    ])
                print_table(headers, rows, col_widths, alignments)
                
        elif choice == '3':
            print_header("EMPRESAS QUE VENCEM / DOMINAM CATEGORIAS DE GASTO")
            monopolies = analyzer.get_monopolies_by_category()
            if not monopolies:
                print("Nenhum dado categorizado disponível.")
            else:
                headers = ["Categoria de Gasto", "Empresa Dominante", "Total Contratado", "Ano", "Qtd Ocorr."]
                col_widths = [22, 30, 16, 4, 10]
                alignments = ['L', 'L', 'R', 'R', 'R']
                rows = []
                for r in monopolies[:20]:
                    rows.append([
                        r["categoria"],
                        r["creditor_name"][:30],
                        fmt_currency(r["total_gasto"]),
                        str(r["exercicio"]),
                        str(r["num_ocorrencias"])
                    ])
                print_table(headers, rows, col_widths, alignments)
                
        elif choice == '4':
            print_header("AUDITORIA DE GASTOS COM SAÚDE (MEDICAMENTOS & SERVIÇOS)")
            health = analyzer.get_health_spending_analysis()
            headers = ["Fornecedor Saúde", "Insumo / Projeto", "Valor Empenhado", "Valor Pago", "Ano"]
            col_widths = [30, 25, 16, 16, 4]
            alignments = ['L', 'L', 'R', 'R', 'R']
            rows = []
            for r in health[:15]:
                rows.append([
                    r["supplier_name"][:30],
                    r["item_or_project"][:25],
                    fmt_currency(r["total_empenhado"]),
                    fmt_currency(r["total_pago"]),
                    str(r["exercicio"])
                ])
            print_table(headers, rows, col_widths, alignments)
            
        elif choice == '5':
            print_header("AUDITORIA DE GASTOS COM EDUCAÇÃO (MERENDA, TRANSPORTE E REFORMAS)")
            edu = analyzer.get_education_spending_analysis()
            headers = ["Fornecedor Educação", "Item / Ação", "Valor Empenhado", "Valor Pago", "Ano"]
            col_widths = [30, 25, 16, 16, 4]
            alignments = ['L', 'L', 'R', 'R', 'R']
            rows = []
            for r in edu[:15]:
                rows.append([
                    r["supplier_name"][:30],
                    r["item_or_project"][:25],
                    fmt_currency(r["total_empenhado"]),
                    fmt_currency(r["total_pago"]),
                    str(r["exercicio"])
                ])
            print_table(headers, rows, col_widths, alignments)
            
        elif choice == '6':
            print_header("DESPESAS COM PUBLICIDADE INSTITUCIONAL E PROPAGANDA")
            pub = analyzer.get_publicity_spending()
            headers = ["Agência de Publicidade", "Veículo de Divulgação", "Secretaria / Órgão", "Total Pago", "Ano"]
            col_widths = [25, 23, 20, 16, 4]
            alignments = ['L', 'L', 'L', 'R', 'R']
            rows = []
            for r in pub:
                rows.append([
                    r["agency_name"][:25],
                    r["vehicle"][:23],
                    r["department"][:20],
                    fmt_currency(r["total_pago"]),
                    str(r["ano"])
                ])
            print_table(headers, rows, col_widths, alignments)
            
        elif choice == '7':
            print_header("EVENTOS, CULTURA, SHOWS E O MAIOR SÃO JOÃO DO MUNDO")
            events = analyzer.get_sao_joao_events_analysis()
            if not events:
                print("Nenhum contrato associado a eventos ou cultura catalogado.")
            else:
                headers = ["Fornecedor Eventos", "Modalidade", "Valor Contrato", "Objeto Contratado"]
                col_widths = [28, 22, 16, 35]
                alignments = ['L', 'L', 'R', 'L']
                rows = []
                for r in events:
                    rows.append([
                        r["supplier_name"][:28],
                        r["procurement_mode"][:22],
                        fmt_currency(r["contract_value"]),
                        r["object_description"][:35]
                    ])
                print_table(headers, rows, col_widths, alignments)
                
        elif choice == '8':
            print_header("DIÁRIAS E PASSAGENS PAGAS A AGENTES PÚBLICOS")
            diarias = analyzer.get_travel_diarias_analysis()
            headers = ["Servidor Beneficiário", "Cargo", "Destino da Viagem", "Período", "Valor Recebido"]
            col_widths = [24, 20, 15, 22, 14]
            alignments = ['L', 'L', 'L', 'L', 'R']
            rows = []
            for r in diarias[:15]:
                rows.append([
                    r["servant_name"][:24],
                    r["role"][:20],
                    r["destination"][:15],
                    r["travel_period"][:22],
                    fmt_currency(r["amount_paid"])
                ])
            print_table(headers, rows, col_widths, alignments)
            
        elif choice == '9':
            print_header("TERCEIRIZAÇÕES, TEMPORÁRIOS E PESSOAL")
            payroll = analyzer.get_payroll_staff_analysis()
            
            print(f"\n{BOLD}{YELLOW}A. Quadro de Servidores Municipais Efetivos, Comissionados e Temporários:{RESET}")
            headers = ["Secretaria / Lotação", "Efetivos", "Comissionados", "Temporários", "Total Folha Líquida"]
            col_widths = [30, 9, 13, 11, 20]
            alignments = ['L', 'R', 'R', 'R', 'R']
            rows = []
            for r in payroll["staff_structure"]:
                rows.append([
                    r["department"][:30],
                    str(r["num_efetivos"]),
                    str(r["num_comissionados"]),
                    str(r["num_temporarios"]),
                    fmt_currency(r["total_salario_liquido"])
                ])
            print_table(headers, rows, col_widths, alignments)
            
            print(f"\n{BOLD}{YELLOW}B. Maiores Contratos de Serviços Terceirizados PJ Identificados:{RESET}")
            outsourced = payroll["outsourced_spent"]
            if not outsourced:
                print("Nenhum gasto específico catalogado como terceirização estrutural.")
            else:
                headers = ["Empresa de Terceirização PJ", "Secretaria Solicitante", "Total Empenhado"]
                col_widths = [35, 30, 16]
                alignments = ['L', 'L', 'R']
                rows = []
                for r in outsourced:
                    rows.append([
                        r["outsourced_company"][:35],
                        r["department"][:30],
                        fmt_currency(r["total_spent"])
                    ])
                print_table(headers, rows, col_widths, alignments)
                
        elif choice == '10':
            print_header("FROTA DE VEÍCULOS MUNICIPAIS E DESPESAS DE COMBUSTÍVEL")
            fleet = analyzer.get_fleet_fuel_efficiency()
            headers = ["Placa", "Modelo / Marca", "Secretaria Alocada", "Aquisição", "Gasto Gasolina", "Total Litros", "Manutenção"]
            col_widths = [9, 20, 20, 12, 16, 12, 16]
            alignments = ['L', 'L', 'L', 'L', 'R', 'R', 'R']
            rows = []
            for r in fleet:
                rows.append([
                    r["plate"],
                    f"{r['model']} ({r['brand']})"[:20],
                    r["department"][:20],
                    r["acquisition_type"],
                    fmt_currency(r["spent_fuel"]),
                    f"{r['total_liters']:.1f} L" if r['total_liters'] else "0 L",
                    fmt_currency(r["spent_maintenance"])
                ])
            print_table(headers, rows, col_widths, alignments)
            
        elif choice == '11':
            print_header("REPASSES FINANCEIROS PARA ONGS E ORGANIZAÇÕES SOCIAIS")
            ngos = analyzer.get_ngo_partnerships_analysis()
            if not ngos:
                print("Nenhum convênio ou termo de fomento para ONGs catalogado.")
            else:
                headers = ["Entidade / ONG", "Tipo Termo", "Valor Convênio", "Vigência", "Secretaria"]
                col_widths = [32, 18, 16, 22, 20]
                alignments = ['L', 'L', 'R', 'L', 'L']
                rows = []
                for r in ngos:
                    rows.append([
                        r["entity_name"][:32],
                        r["partnership_type"][:18],
                        fmt_currency(r["total_value"]),
                        f"{r['start_date']} a {r['end_date']}",
                        r["department"][:20]
                    ])
                print_table(headers, rows, col_widths, alignments)
                
        elif choice == '12':
            print_header("RASTREAMENTO DE DESTINAÇÃO DE EMENDAS PARLAMENTARES")
            pathway = analyzer.get_amendment_pathway()
            headers = ["Parlamentar Destinatário", "Valor Emenda", "Projeto Indicado", "Empresa Executora", "Empenhado", "Pago"]
            col_widths = [24, 14, 25, 25, 14, 14]
            alignments = ['L', 'R', 'L', 'L', 'R', 'R']
            rows = []
            for r in pathway:
                rows.append([
                    r["politician_name"][:24],
                    fmt_currency(r["amendment_value"]),
                    r["amendment_project"][:25],
                    (r["executing_supplier"] or "N/D")[:25],
                    fmt_currency(r["spent_empenhado"]),
                    fmt_currency(r["spent_pago"])
                ])
            print_table(headers, rows, col_widths, alignments)
            
        elif choice == '13':
            print_header("CRUZAMENTO DE RISCO: CONTRATADOS MUNICIPAIS INSCRITOS NA DÍVIDA ATIVA")
            crossings = analyzer.get_active_debt_crossings()
            headers = ["Fornecedor com Dívida", "Dívida Ativa Devida", "Origem Débito", "Faturamento Prefeitura", "Total Pago Real"]
            col_widths = [30, 16, 22, 16, 16]
            alignments = ['L', 'R', 'L', 'R', 'R']
            rows = []
            for r in crossings:
                rows.append([
                    r["supplier_name"][:30],
                    fmt_currency(r["active_debt_amount"]),
                    r["debt_origin"][:22],
                    fmt_currency(r["total_empenhado_prefeitura"]),
                    fmt_currency(r["total_pago_prefeitura"])
                ])
            print_table(headers, rows, col_widths, alignments)
            
        elif choice == '14':
            print_header("MONITORAMENTO DE LICITANTES E FORNECEDORES SANCIONADOS")
            crossings = analyzer.get_sanctioned_supplier_crossings()
            if not crossings:
                print("✅ Nenhuma empresa contratada ativa possui registro de sanção de inidoneidade municipal/federal.")
            else:
                headers = ["Fornecedor Punido", "Tipo Sanção", "Órgão Sancionador", "Vigência Sanção", "Contrato Número", "Valor Contrato"]
                col_widths = [24, 22, 20, 22, 15, 14]
                alignments = ['L', 'L', 'L', 'L', 'L', 'R']
                rows = []
                for r in crossings:
                    rows.append([
                        r["supplier_name"][:24],
                        r["sanction_type"][:22],
                        r["sanctioning_body"][:20],
                        f"{r['start_date']} a {r['end_date'] or 'N/D'}",
                        r["contract_number"] or "N/D",
                        fmt_currency(r["contract_value"])
                    ])
                print_table(headers, rows, col_widths, alignments)
                
        elif choice == '15':
            print_header("CRUZAMENTO DE PROXIMIDADE ELEITORAL: CONEXÕES POLÍTICAS (TSE)")
            connections = analyzer.get_political_connections()
            if not connections:
                print("Nenhum sócio ou empresa com doação declarada ao TSE no banco de dados.")
            else:
                headers = ["Fornecedor Contratado", "Sócio Doador", "Doação PF (TSE)", "Fornec. Campanha", "Político Beneficiário", "Prefeitura (Recebido)"]
                col_widths = [25, 20, 15, 15, 22, 16]
                alignments = ['L', 'L', 'R', 'R', 'L', 'R']
                rows = []
                for r in connections:
                    rows.append([
                        r["supplier_name"][:25],
                        r["partner_name"][:20],
                        fmt_currency(r["pf_donation"]),
                        fmt_currency(r["campaign_supplying"]),
                        r["politician_beneficiary"][:22],
                        fmt_currency(r["total_spent_prefeitura"])
                    ])
                print_table(headers, rows, col_widths, alignments)
                
        elif choice == '16':
            print_header("ESTRUTURA DE REDES RELACIONAIS (FORMATO GRAFO JSON)")
            graph = analyzer.get_network_graph_data()
            print(f"Total de Nós (Nodes) Identificados: {len(graph['nodes'])}")
            print(f"Total de Conexões (Edges) Mapeadas: {len(graph['edges'])}")
            
            # Print sample of nodes and edges
            print(f"\n{BOLD}{YELLOW}Amostra dos Nós (Nodos):{RESET}")
            for n in graph["nodes"][:5]:
                print(f"  - [{n['group']}] ID: {n['id']} | Rótulo: {n['label']}")
                
            print(f"\n{BOLD}{YELLOW}Amostra de Conexões (Arestas):{RESET}")
            for e in graph["edges"][:5]:
                print(f"  - {e['from']}  ──({e['label']})──>  {e['to']}")
                
            output_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/network_graph.json"))
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(graph, f, indent=4, ensure_ascii=False)
            print(f"\n💾 Grafo relacional exportado com sucesso para: {BOLD}{output_file}{RESET}")
            
        elif choice == '17':
            print_header("DASHBOARD CIVICO GERAL: PRINCIPAIS ANÁLISES INTEGRADAS")
            hl = analyzer.get_top_highlights()
            print(f"{BOLD}{BLUE}Faturamento e Governança Cívica de Campina Grande:{RESET}")
            print(f"  - Empresas catalogadas com Contratação Direta: {BOLD}{hl['procurement_totals']}{RESET}")
            print(f"  - Alertas de Fracionamento Suspeito de Despesa: {BOLD}{RED}{hl['fractioning_count']} alertas{RESET}")
            print(f"  - Fornecedores em atraso tributário (Dívida Ativa): {BOLD}{hl['active_debt_count']} devedores contratados{RESET}")
            print(f"  - Conexões Societárias e Políticas Diretas (TSE):  {BOLD}{hl['political_count']} cruzamentos ativos{RESET}")
            
            print(f"\n{BOLD}{YELLOW}Top 3 Fornecedores da Prefeitura por Faturamento (Empenhado):{RESET}")
            for idx, s in enumerate(hl["top_suppliers"]):
                print(f"  #{idx+1}: {s['supplier_name']} - Empenhado: {fmt_currency(s['total_empenhado'])} | Pago: {fmt_currency(s['total_pago'])}")
                
        elif choice == '18':
            print_header("RECORTE DE PESQUISA FORENSE E INVESTIGATIVA (CIDADE ABERTA)")
            summary = analyzer.get_forensic_research_summary()
            headers = ["Fornecedor Analisado", "Dívida Ativa", "Doador PF (TSE)", "Beneficiário Campanha", "Empenhado Prefeitura"]
            col_widths = [25, 14, 15, 22, 20]
            alignments = ['L', 'R', 'R', 'L', 'R']
            rows = []
            for r in summary:
                rows.append([
                    r["supplier_name"][:25],
                    fmt_currency(r["active_debt"]),
                    fmt_currency(r["campaign_donation"]),
                    r["politician"][:22],
                    fmt_currency(r["total_received"])
                ])
            print_table(headers, rows, col_widths, alignments)
            print(f"\n💡 {BOLD}Metodologia Cívica:{RESET} Este recorte aponta interseções de dados públicos eleitorais e fiscais.")
            print("  Não expressa conclusão de ilegalidades administrativas, servindo como bússola de governança.")
            
        elif choice == '19':
            print_header("LAYER DE INTELIGÊNCIA ARTIFICIAL E AUDITORIA FORENSE SEMÂNTICA (GEMINI)")
            data = get_anomaly_data()
            run_statistical_anomaly_detection(data)
            run_semantic_ai_audit()
            
            print("\n" + "="*80)
            print(f"🧠 {BOLD}{CYAN}LAYER 3: COGNITIVE ANOMALY WARNING BLOCKS (GEMINI AI){RESET}")
            print("="*80)
            api_key = os.environ.get("GEMINI_API_KEY")
            if not api_key:
                print(f"ℹ️ {YELLOW}Nota: Variável GEMINI_API_KEY não configurada. Executando em Modo de Simulação de IA.{RESET}")
            else:
                print(f"🔋 {GREEN}Variável GEMINI_API_KEY detectada! Gerando blocos cognitivos de alerta reais...{RESET}")
                
            warnings = generate_unusual_warning_blocks(api_key=api_key)
            if not warnings:
                print("✅ Nenhuma outra inconsistência cognitiva severa detectada pela Inteligência Artificial.")
            for w in warnings:
                print(f"\n[{BOLD}{YELLOW}Tópico: {w['topic']}{RESET}]")
                print(f"  🚨 {RED}{BOLD}{w['text']}{RESET}")
                print(f"  {BOLD}Dados brutos envolvidos:{RESET} {json.dumps(w['data'], ensure_ascii=False)}")
                print("-" * 80)
            
        elif choice == '20':
            print_header("AUDITORIA DE QUALIDADE DE DADOS (ERROS & INCONSISTÊNCIAS DO PORTAL)")
            err_summary = analyzer.get_scraper_errors_summary()
            
            print(f"Total de Registros Corrompidos/Incompletos Ingeridos: {BOLD}{RED}{err_summary['total_errors']}{RESET}")
            
            if err_summary['total_errors'] == 0:
                print(f"✅ {GREEN}Nenhum erro de ingestão registrado! Todos os dados coletados possuem conformidade estrutural.{RESET}")
            else:
                print(f"\n{BOLD}{YELLOW}A. Frequência de Erros de Ingestão por Nível Técnico:{RESET}")
                headers = ["Nível da Entidade", "Qtd Ocorrências"]
                col_widths = [25, 15]
                alignments = ['L', 'R']
                rows = []
                for lv in err_summary['by_level']:
                    rows.append([lv['level'], str(lv['count'])])
                print_table(headers, rows, col_widths, alignments)
                
                print(f"\n{BOLD}{YELLOW}B. Últimos 10 Erros Registrados (Amostra Forense):{RESET}")
                headers = ["Data/Hora UTC", "Nível", "Mensagem de Erro", "Contexto de Ingestão"]
                col_widths = [20, 15, 25, 25]
                alignments = ['L', 'L', 'L', 'L']
                rows = []
                for sample in err_summary['recent_samples']:
                    rows.append([
                        sample['timestamp'],
                        sample['level'],
                        sample['error_message'][:25],
                        (sample['context_info'] or 'N/A')[:25]
                    ])
                print_table(headers, rows, col_widths, alignments)
                
                print(f"\n📢 {BOLD}Auditoria de Dados:{RESET} Inconsistências técnicas do portal público podem denotar instabilidade tecnológica")
                print("  ou intencionalidade em dificultar a análise e controle social por meio de payloads corrompidos.")
                
        else:
            print(f"{RED}Opção inválida! Digite um número de 0 a 20.{RESET}")

            
        input(f"\nPressione {BOLD}[Enter]{RESET} para voltar ao menu principal...")

if __name__ == "__main__":
    main()
