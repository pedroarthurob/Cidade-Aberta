import sqlite3
import os
import sys

# Dynamic database paths
DATABASE_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/transparencia_cg.db"))

def seed_db():
    print(f"Seeding municipal transparency database with increased records at: {DATABASE_FILE}")
    conn = sqlite3.connect(DATABASE_FILE)
    conn.execute("PRAGMA foreign_keys = ON;")
    cursor = conn.cursor()
    
    # Enable writing with dict factory for ease
    conn.row_factory = sqlite3.Row

    # Clear old data from these tables to avoid duplicates
    tables_to_clear = [
        "despesas_frota", "veiculos_frota", "convenios", "relacoes_politicas", 
        "sancoes", "divida_ativa", "emendas", "publicidade", "diarias", 
        "payroll_records", "obras", "contratos", "licitacoes", "movements", 
        "empenhos", "expense_elements", "creditors", "organs", "institutions",
        "receitas"
    ]
    for table in tables_to_clear:
        try:
            cursor.execute(f"DELETE FROM {table};")
        except sqlite3.OperationalError:
            pass # Table might not exist yet or other issues

    # 1. Institutions
    institutions = [
        (1, "Prefeitura Municipal de Campina Grande"),
        (2, "IPSEM - Instituto de Previdência do Município"),
        (3, "Fundo Municipal de Saúde"),
        (4, "Câmara Municipal de Campina Grande")
    ]
    cursor.executemany("INSERT OR REPLACE INTO institutions (id, name) VALUES (?, ?);", institutions)

    # 2. Organs
    organs = [
        ("10100", "Gabinete do Prefeito", 1),
        ("10200", "Secretaria de Administração", 1),
        ("10300", "Secretaria de Saúde", 1),
        ("10400", "Secretaria de Educação", 1),
        ("10500", "Secretaria de Serviços Urbanos", 1),
        ("10600", "Secretaria de Cultura", 1),
        ("10700", "Coordenadoria de Comunicação Social", 1),
        ("20100", "Fundo Municipal de Saúde", 3),
        ("30100", "IPSEM Administrativo", 2)
    ]
    cursor.executemany("INSERT OR REPLACE INTO organs (code, name, institution_id) VALUES (?, ?, ?);", organs)

    # 3. Creditors (Doubled to represent all analytical verticals)
    creditors = [
        ("C1", "09.112.553/0001-01", "IPSEM - INSTITUTO DE PREVIDENCIA DE CG"),
        ("C2", "11.111.111/0001-11", "CONSTRUTORA BOA VISTA LTDA"),
        ("C3", "22.222.222/0001-22", "INFRAESTRUTURA NORDESTE S.A."),
        ("C4", "33.333.333/0001-33", "CONSTRUTORA SEGURA LTDA"),
        ("C5", "44.444.444/0001-44", "MEDFARMA DISTRIBUIDORA DE MEDICAMENTOS LTDA"),
        ("C6", "55.555.555/0001-55", "SAUDE TOTAL SERVICOS MEDICOS LTDA"),
        ("C7", "66.666.666/0001-66", "AGILIZAR LOGISTICA E TRANSPORTES LTDA"),
        ("C8", "77.777.777/0001-77", "NUTRIPAN PANIFICADORA E ALIMENTOS LTDA"),
        ("C9", "88.888.888/0001-88", "FAROL COMUNICACAO E PUBLICIDADE LTDA"),
        ("C10", "88.888.888/0002-99", "RADIO ARAPUAN FM LTDA"),
        ("C11", "99.999.999/0001-99", "FESTAS E EVENTOS NORDESTE EIRELI"),
        ("C12", "00.000.001/0001-01", "ARTISTA BRUNO E MARRONE MOCK"),
        ("C13", "00.000.002/0001-02", "ARTISTA ELBA RAMALHO MOCK"),
        ("C14", "00.000.003/0001-03", "ASSOCIACAO DE APOIO CULTURAL DE CG (ONG)"),
        ("C15", "12.345.678/0001-90", "TECNOLOGIA E SISTEMAS CAMPINA LTDA"),
        ("C16", "23.456.789/0001-01", "AUTO POSTO BARRIGUDA LTDA"),
        ("C17", "34.567.890/0001-12", "AUTO PECAS E MANUTENCAO BORBOREMA"),
        ("C18", "45.678.901/0001-23", "DEVEDOR TOTAL E CONTRATADO LTDA"),
        ("C19", "56.789.012/0001-34", "SANCIONADO E CONTRATADO LTDA"),
        ("C20", "67.890.123/0001-45", "POLITICAMENTE CONECTADO LTDA"),
        ("C21", "78.901.234/0001-56", "VIGILANCIA SEGURA PRIVADA LTDA"),
        # Additional Creditors
        ("C22", "99.999.001/0001-01", "CONSTRUTORA SAO JOSE LTDA"),
        ("C23", "99.999.002/0001-02", "FARMACIA DO TRABALHADOR DE CG"),
        ("C24", "99.999.003/0001-03", "MEDICA LIFE SERVICOS MEDICOS LTDA"),
        ("C25", "99.999.004/0001-04", "EXPRESSO TRANSPORTES NORDESTE LTDA"),
        ("C26", "99.999.005/0001-05", "NUTRINORTE MERENDA ESCOLAR LTDA"),
        ("C27", "99.999.006/0001-06", "PORTAL DIARIO DO NORDESTE MOCK"),
        ("C28", "99.999.007/0001-07", "ARTISTA CHANDY E JUNIOR MOCK"),
        ("C29", "99.999.008/0001-08", "COMPLEXO EVENTOS PARAIBA LTDA"),
        ("C30", "99.999.009/0001-09", "ONG VIVA VIDA CAMPINA"),
        ("C31", "99.999.010/0001-10", "SOFT-CG TECNOLOGIA LTDA"),
        ("C32", "99.999.011/0001-11", "AUTO PECAS E SERVICOS RAPIDO LTDA"),
        ("C33", "99.999.012/0001-12", "LOCADORA SUL VEICULOS EIRELI"),
        ("C34", "99.999.013/0001-13", "SUPREMA SEGURANCA PRIVADA LTDA"),
        ("C35", "99.999.014/0001-14", "PAPELARIA E ESCRITORIO CG LTDA"),
        ("C36", "99.999.015/0001-15", "AUTO POSTO MAIOR SAO JOAO LTDA")
    ]
    cursor.executemany("INSERT OR REPLACE INTO creditors (id, cpf_cnpj, name) VALUES (?, ?, ?);", creditors)

    # 4. Expense Elements
    elements = [
        ("339014", "Diárias - Civil", "DIARIAS DE SERVIDORES CIVIS", "DIARIAS"),
        ("339030", "Material de Consumo", "MATERIAL DE CONSUMO (MERENDA/MEDICAMENTOS/GASOLINA)", "MAT_CONSUMO"),
        ("339039", "Outros Serviços de Terceiros - PJ", "SERVICOS DE TERCEIROS PESSOA JURIDICA", "SERV_TERC_PJ"),
        ("449051", "Obras e Instalações", "OBRAS EM EXECUCAO E REFORMAS", "OBRAS"),
        ("339036", "Outros Serviços de Terceiros - PF", "SERVICOS DE TERCEIROS PESSOA FISICA", "SERV_TERC_PF"),
        ("319011", "Vencimentos e Vantagens Fixas", "FOLHA DE SERVIDORES CIVIS", "PESSOAL_CIVIL")
    ]
    cursor.executemany("INSERT OR REPLACE INTO expense_elements (code, group_name, name, short_code) VALUES (?, ?, ?, ?);", elements)

    # 5. Licitações (Increased list of biddings)
    licitacoes = [
        ("LIC-001/2024", "PREGÃO ELETRÔNICO", "Aquisição de medicamentos essenciais para a Rede Municipal de Saúde", "2024-03-10", "HOMOLOGADA", 1000000.0, 950000.0),
        ("LIC-002/2024", "DISPENSA DE LICITAÇÃO", "Aquisição emergencial de insumos de saúde em virtude de surto de arboviroses", "2024-05-15", "HOMOLOGADA", 80000.0, 80000.0),
        ("LIC-003/2024", "INEXIGIBILIDADE", "Contratação de show artístico da dupla Bruno e Marrone para o São João 2024", "2024-04-20", "HOMOLOGADA", 500000.0, 500000.0),
        ("LIC-004/2024", "PREGÃO ELETRÔNICO", "Serviço de transporte de alunos da rede municipal - Zona Rural", "2024-02-15", "HOMOLOGADA", 1200000.0, 1150000.0),
        ("LIC-005/2024", "CONCORRÊNCIA", "Reforma estrutural de escolas municipais no bairro das Malvinas", "2024-06-01", "HOMOLOGADA", 3000000.0, 2850000.0),
        ("LIC-006/2024", "CONCORRÊNCIA", "Construção e pavimentação do Canal de Bodocongó", "2024-08-01", "HOMOLOGADA", 5000000.0, 4800000.0),
        # Fractional Direct Purchases (Fracionamento Suspeito)
        ("LIC-007/2024", "DISPENSA DE LICITAÇÃO", "Manutenção elétrica corretiva de bombas d'água - Bloco A", "2024-10-01", "HOMOLOGADA", 15000.0, 15000.0),
        ("LIC-008/2024", "DISPENSA DE LICITAÇÃO", "Manutenção elétrica corretiva de bombas d'água - Bloco B", "2024-10-01", "HOMOLOGADA", 15000.0, 15000.0),
        ("LIC-009/2024", "DISPENSA DE LICITAÇÃO", "Manutenção elétrica corretiva de bombas d'água - Bloco C", "2024-10-01", "HOMOLOGADA", 15000.0, 15000.0),
        # Event direct purchases
        ("LIC-010/2024", "INEXIGIBILIDADE", "Show artístico de Elba Ramalho no Maior São João do Mundo", "2024-05-10", "HOMOLOGADA", 200000.0, 200000.0),
        ("LIC-011/2024", "DISPENSA DE LICITAÇÃO", "Compra direta de alimentação (gêneros alimentícios) para merenda", "2024-03-01", "HOMOLOGADA", 48000.0, 48000.0),
        ("LIC-012/2024", "PREGÃO ELETRÔNICO", "Serviços de Tecnologia da Informação e Licenciamento de Software", "2024-01-20", "HOMOLOGADA", 800000.0, 800000.0),
        # Newly added biddings for increased scale
        ("LIC-013/2024", "PREGÃO ELETRÔNICO", "Aquisição de fardamento escolar para rede municipal", "2024-02-05", "HOMOLOGADA", 600000.0, 580000.0),
        ("LIC-014/2024", "DISPENSA DE LICITAÇÃO", "Manutenção mecânica e preventiva de ambulâncias do SAMU", "2024-04-18", "HOMOLOGADA", 30000.0, 30000.0),
        ("LIC-015/2024", "INEXIGIBILIDADE", "Show artístico de Chandy e Junior no São João 2024", "2024-05-15", "HOMOLOGADA", 350000.0, 350000.0),
        ("LIC-016/2024", "DISPENSA DE LICITAÇÃO", "Compra emergencial de merenda - Distribuidora Nutrinorte", "2024-04-10", "HOMOLOGADA", 45000.0, 45000.0),
        ("LIC-017/2024", "PREGÃO ELETRÔNICO", "Serviços de Vigilância Armada e Segurança Patrimonial", "2024-03-25", "HOMOLOGADA", 1500000.0, 1450000.0),
        ("LIC-018/2024", "CONCORRÊNCIA", "Construção de UBS no Bairro das Cidades", "2024-07-15", "HOMOLOGADA", 2000000.0, 1950000.0)
    ]
    cursor.executemany("INSERT OR REPLACE INTO licitacoes VALUES (?, ?, ?, ?, ?, ?, ?);", licitacoes)

    # 6. Contratos (Expanded contracts)
    contratos = [
        ("CON-001/2024", "LIC-001/2024", "C5", "2024-03-15", "2025-03-15", 950000.0),
        ("CON-002/2024", "LIC-002/2024", "C6", "2024-05-16", "2024-11-16", 80000.0),
        ("CON-003/2024", "LIC-003/2024", "C12", "2024-04-25", "2024-07-25", 500000.0),
        ("CON-004/2024", "LIC-004/2024", "C7", "2024-02-20", "2025-02-20", 1150000.0),
        ("CON-005/2024", "LIC-005/2024", "C2", "2024-06-10", "2025-06-10", 2850000.0),
        ("CON-006/2024", "LIC-006/2024", "C3", "2024-08-10", "2025-08-10", 4800000.0),
        ("CON-007/2024", "LIC-007/2024", "C18", "2024-10-02", "2025-10-02", 15000.0),
        ("CON-008/2024", "LIC-008/2024", "C18", "2024-10-02", "2025-10-02", 15000.0),
        ("CON-009/2024", "LIC-009/2024", "C18", "2024-10-02", "2025-10-02", 15000.0),
        ("CON-010/2024", "LIC-010/2024", "C13", "2024-05-12", "2024-07-12", 200000.0),
        ("CON-011/2024", "LIC-011/2024", "C8", "2024-03-02", "2024-09-02", 48000.0),
        ("CON-012/2024", "LIC-012/2024", "C15", "2024-01-22", "2025-01-22", 800000.0),
        # New contracts
        ("CON-013/2024", "LIC-013/2024", "C25", "2024-02-10", "2025-02-10", 580000.0),
        ("CON-014/2024", "LIC-014/2024", "C32", "2024-04-20", "2024-10-20", 30000.0),
        ("CON-015/2024", "LIC-015/2024", "C28", "2024-05-16", "2024-07-16", 350000.0),
        ("CON-016/2024", "LIC-016/2024", "C26", "2024-04-12", "2024-10-12", 45000.0),
        ("CON-017/2024", "LIC-017/2024", "C34", "2024-04-01", "2025-04-01", 1450000.0),
        ("CON-018/2024", "LIC-018/2024", "C22", "2024-07-20", "2025-07-20", 1950000.0),
        # Publicity contracts
        ("CON-PUB-001/2024", None, "C9", "2024-01-01", "2024-12-31", 1000000.0),
        ("CON-PUB-001/2025", None, "C9", "2025-01-01", "2025-12-31", 1500000.0)
    ]
    cursor.executemany("INSERT OR REPLACE INTO contratos VALUES (?, ?, ?, ?, ?, ?);", contratos)

    # 7. Empenhos (Expanded transactions)
    empenhos = [
        ("EMP-001", "2024001", 2024, 1, "10300", "10301", "Fundo M. de Saúde", "10", "Saúde", "301", "Atenção Básica", "2001", "Saude Total", "1001", "Aquisicao Remedios", "339030", "C5", "0100", "Recursos Proprios", "2024-03-16", 950000.0, 0.0, 950000.0, 900000.0),
        ("EMP-002", "2024002", 2024, 1, "10300", "10301", "Fundo M. de Saúde", "10", "Saúde", "301", "Atenção Básica", "2001", "Saude Total", "1002", "Aquisicao Emergencial", "339039", "C6", "0100", "Recursos Proprios", "2024-05-16", 80000.0, 0.0, 80000.0, 80000.0),
        ("EMP-003", "2024003", 2024, 1, "10600", "10601", "Sec. de Cultura", "13", "Cultura", "392", "Difusão Cultural", "2005", "Eventos Culturais", "1003", "Show Bruno e Marrone", "339039", "C12", "0100", "Recursos Proprios", "2024-04-26", 500000.0, 0.0, 500000.0, 500000.0),
        ("EMP-004", "2024004", 2024, 1, "10400", "10401", "Sec. de Educação", "12", "Educação", "361", "Ensino Fundamental", "2002", "Educação Basica", "1004", "Transporte Escolar", "339039", "C7", "0112", "Recursos Salário-Educação", "2024-02-21", 1150000.0, 0.0, 1150000.0, 1000000.0),
        ("EMP-005", "2024005", 2024, 1, "10400", "10401", "Sec. de Educação", "12", "Educação", "361", "Ensino Fundamental", "2002", "Educação Basica", "1005", "Reforma de Escolas", "449051", "C2", "0112", "Recursos Salário-Educação", "2024-06-11", 2850000.0, 0.0, 2500000.0, 2500000.0),
        ("EMP-006", "2024006", 2024, 1, "10500", "10501", "Sec. de Serviços Urbanos", "15", "Urbanismo", "451", "Infraestrutura Urbana", "2004", "Cidade Limpa", "1006", "Canal de Bodocongó", "449051", "C3", "0100", "Recursos Proprios", "2024-08-11", 4800000.0, 0.0, 4500000.0, 4500000.0),
        ("EMP-007", "2024007", 2024, 1, "10200", "10201", "Sec. de Administração", "04", "Administração", "122", "Administração Geral", "2003", "Gestao Geral", "1007", "Manutencao Bombas 1", "339030", "C18", "0100", "Recursos Proprios", "2024-10-02", 15000.0, 0.0, 15000.0, 15000.0),
        ("EMP-008", "2024008", 2024, 1, "10200", "10201", "Sec. de Administração", "04", "Administração", "122", "Administração Geral", "2003", "Gestao Geral", "1007", "Manutencao Bombas 2", "339030", "C18", "0100", "Recursos Proprios", "2024-10-02", 15000.0, 0.0, 15000.0, 15000.0),
        ("EMP-009", "2024009", 2024, 1, "10200", "10201", "Sec. de Administração", "04", "Administração", "122", "Administração Geral", "2003", "Gestao Geral", "1007", "Manutencao Bombas 3", "339030", "C18", "0100", "Recursos Proprios", "2024-10-02", 15000.0, 0.0, 15000.0, 15000.0),
        ("EMP-010", "2024010", 2024, 1, "10600", "10601", "Sec. de Cultura", "13", "Cultura", "392", "Difusão Cultural", "2005", "Eventos Culturais", "1008", "Show Elba Ramalho", "339039", "C13", "0100", "Recursos Proprios", "2024-05-13", 200000.0, 0.0, 200000.0, 200000.0),
        ("EMP-011", "2024011", 2024, 1, "10400", "10401", "Sec. de Educação", "12", "Educação", "306", "Alimentação e Nutrição", "2002", "Educação Basica", "1009", "Merenda Panificadora", "339030", "C8", "0100", "Recursos Proprios", "2024-03-03", 48000.0, 0.0, 48000.0, 48000.0),
        ("EMP-012", "2024012", 2024, 1, "10200", "10201", "Sec. de Administração", "04", "Administração", "126", "Tecnologia da Informação", "2003", "Gestao Geral", "1010", "Sistemas Prefeitura", "339039", "C15", "0100", "Recursos Proprios", "2024-01-23", 800000.0, 0.0, 800000.0, 800000.0),
        # Publicity empenhos
        ("EMP-PUB-001", "2024101", 2024, 1, "10700", "10701", "Comunicação Social", "04", "Comunicação", "131", "Comunicação Social", "2006", "Publicidade", "1011", "Divulgacao Acoes 2024", "339039", "C9", "0100", "Recursos Proprios", "2024-01-02", 1000000.0, 0.0, 1000000.0, 1000000.0),
        ("EMP-PUB-002", "2025101", 2025, 1, "10700", "10701", "Comunicação Social", "04", "Comunicação", "131", "Comunicação Social", "2006", "Publicidade", "1011", "Divulgacao Acoes 2025", "339039", "C9", "0100", "Recursos Proprios", "2025-01-02", 1500000.0, 0.0, 1200000.0, 1200000.0),
        # Diarias and other minor empenhos
        ("EMP-DIR-001", "2024201", 2024, 1, "10100", "10101", "Gabinete Prefeito", "04", "Administração", "122", "Administração Geral", "2003", "Gestao Geral", "1012", "Diarias Gabinete", "339014", "C10", "0100", "Recursos Proprios", "2024-05-01", 15500.0, 0.0, 15500.0, 15500.0),
        # NGO Partnership
        ("EMP-NGO-001", "2024301", 2024, 1, "10600", "10601", "Sec. de Cultura", "13", "Cultura", "392", "Difusão Cultural", "2005", "Eventos Culturais", "1013", "Parceria Cultural ONG", "339039", "C14", "0100", "Recursos Proprios", "2024-05-02", 150000.0, 0.0, 150000.0, 150000.0),
        # Newly added empenhos for increased scale
        ("EMP-013", "2024013", 2024, 1, "10400", "10401", "Sec. de Educação", "12", "Educação", "361", "Ensino Fundamental", "2002", "Educação Basica", "1014", "Fardamentos Alunos", "339030", "C25", "0112", "Salário-Educação", "2024-02-12", 580000.0, 0.0, 580000.0, 580000.0),
        ("EMP-014", "2024014", 2024, 1, "10300", "10301", "Fundo M. de Saúde", "10", "Saúde", "301", "Atenção Básica", "2001", "Saude Total", "1015", "Mecanica Ambulancias", "339039", "C32", "0100", "Proprios", "2024-04-22", 30000.0, 0.0, 30000.0, 30000.0),
        ("EMP-015", "2024015", 2024, 1, "10600", "10601", "Sec. de Cultura", "13", "Cultura", "392", "Difusão Cultural", "2005", "Eventos Culturais", "1016", "Show Chandy e Junior", "339039", "C28", "0100", "Proprios", "2024-05-18", 350000.0, 0.0, 350000.0, 350000.0),
        ("EMP-016", "2024016", 2024, 1, "10400", "10401", "Sec. de Educação", "12", "Educação", "306", "Alimentação Escolar", "2002", "Educação Basica", "1017", "Merenda Emergencial", "339030", "C26", "0100", "Proprios", "2024-04-15", 45000.0, 0.0, 45000.0, 45000.0),
        ("EMP-017", "2024017", 2024, 1, "10200", "10201", "Sec. de Administração", "04", "Administração", "122", "Administração Geral", "2003", "Gestao Geral", "1018", "Vigilancia Armada PJ", "339039", "C34", "0100", "Proprios", "2024-04-05", 1450000.0, 0.0, 1400000.0, 1400000.0),
        ("EMP-018", "2024018", 2024, 1, "10300", "10301", "Fundo M. de Saúde", "10", "Saúde", "301", "Atenção Básica", "2001", "Saude Total", "1019", "Construcao UBS Cidades", "449051", "C22", "0100", "Proprios", "2024-07-22", 1950000.0, 0.0, 1950000.0, 1900000.0)
    ]
    cursor.executemany("""
        INSERT OR REPLACE INTO empenhos (
            id, code, exercicio, institution_id, organ_code, unit_code, unit_name,
            function_code, function_name, subfunction_code, subfunction_name,
            program_code, program_name, project_code, project_name,
            element_code, creditor_id, resource_code, resource_name,
            date_emission, amount_empenhado, amount_anulado, amount_liquidado, amount_pago
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, empenhos)

    # 8. Movements (Added more movements)
    movements = [
        ("MOV-001", "EMP-001", "2024-03-16", "EMPENHO", 950000.0, 1),
        ("MOV-002", "EMP-001", "2024-04-10", "LIQUIDACAO", 950000.0, 2),
        ("MOV-003", "EMP-001", "2024-04-12", "PAGAMENTO", 900000.0, 3),
        ("MOV-004", "EMP-006", "2024-08-11", "EMPENHO", 4800000.0, 1),
        ("MOV-005", "EMP-006", "2024-09-01", "LIQUIDACAO", 4500000.0, 2),
        ("MOV-006", "EMP-006", "2024-09-10", "PAGAMENTO", 4500000.0, 3),
        # Diaria
        ("MOV-DIR-001", "EMP-DIR-001", "2024-05-01", "EMPENHO", 15500.0, 1),
        ("MOV-DIR-002", "EMP-DIR-001", "2024-05-02", "PAGAMENTO", 15500.0, 3),
        # New movements
        ("MOV-007", "EMP-017", "2024-04-05", "EMPENHO", 1450000.0, 1),
        ("MOV-008", "EMP-017", "2024-05-01", "LIQUIDACAO", 1400000.0, 2),
        ("MOV-009", "EMP-017", "2024-05-05", "PAGAMENTO", 1400000.0, 3),
        ("MOV-010", "EMP-018", "2024-07-22", "EMPENHO", 1950000.0, 1),
        ("MOV-011", "EMP-018", "2024-08-10", "LIQUIDACAO", 1950000.0, 2),
        ("MOV-012", "EMP-018", "2024-08-12", "PAGAMENTO", 1900000.0, 3)
    ]
    cursor.executemany("INSERT OR REPLACE INTO movements VALUES (?, ?, ?, ?, ?, ?);", movements)

    # 9. Obras (Expanded works)
    # Columns: id, nome_obra, localizacao, empresa_executora, percentual_exec, valor_contratado, valor_pago_acum, contrato_numero
    obras = [
        (1, "Construção e Pavimentação do Canal de Bodocongó", "Bairro de Bodocongó", "INFRAESTRUTURA NORDESTE S.A.", 50.0, 4800000.0, 4500000.0, "CON-006/2024"),
        (2, "Reforma estrutural de escolas municipais no bairro das Malvinas", "Bairro das Malvinas", "CONSTRUTORA BOA VISTA LTDA", 90.0, 2850000.0, 2500000.0, "CON-005/2024"),
        (3, "Construção de UBS no Bairro das Cidades", "Bairro das Cidades", "CONSTRUTORA SAO JOSE LTDA", 40.0, 1950000.0, 1900000.0, "CON-018/2024") # Anomaly case (paid 97.4%, but only 40% built!)
    ]
    cursor.executemany("INSERT OR REPLACE INTO obras VALUES (?, ?, ?, ?, ?, ?, ?, ?);", obras)

    # 10. Payroll Records (Doubled civil servants list)
    # Columns: id, matricula, nome_servidor, cargo, tipo_vinculo, lotacao, data_admissao, salario_base, vantagens, descontos, salario_liquido, mes, ano
    payroll = [
        (1, "M1", "PEDRO SILVA", "Motorista", "EFETIVO", "Secretaria de Saúde", "2010-02-15", 3000.0, 500.0, 300.0, 3200.0, 5, 2025),
        (2, "M2", "MARIA COSTA", "Assessor Técnico", "COMISSIONADO", "Gabinete do Prefeito", "2021-01-10", 6000.0, 1000.0, 800.0, 6200.0, 5, 2025),
        (3, "M3", "JOAO SANTOS", "Secretário Executivo", "COMISSIONADO", "Gabinete do Prefeito", "2021-01-02", 12000.0, 2000.0, 1500.0, 12500.0, 5, 2025),
        (4, "M4", "ANA LIMA", "Enfermeira", "TEMPORARIO", "Secretaria de Saúde", "2023-03-01", 4000.0, 0.0, 400.0, 3600.0, 5, 2025),
        (5, "M5", "CARLOS ALMEIDA", "Médico PSF", "EFETIVO", "Secretaria de Saúde", "2015-08-20", 10000.0, 1500.0, 1200.0, 10300.0, 5, 2025),
        (6, "M6", "FABIANA GOMES", "Professor", "EFETIVO", "Secretaria de Educação", "2018-02-10", 4500.0, 500.0, 450.0, 4550.0, 5, 2025),
        (7, "M7", "LUCAS MEDEIROS", "Auxiliar Administrativo", "TEMPORARIO", "Secretaria de Educação", "2024-01-15", 1500.0, 0.0, 120.0, 1380.0, 5, 2025),
        # New Personnel
        (8, "M8", "ROBERTO JUNIOR", "Diretor Geral SAMU", "COMISSIONADO", "Secretaria de Saúde", "2021-02-01", 8000.0, 1000.0, 900.0, 8100.0, 5, 2025),
        (9, "M9", "AMANDA MOREIRA", "Coordenador de Midia", "COMISSIONADO", "Coordenadoria de Comunicação Social", "2022-01-15", 5000.0, 500.0, 550.0, 4950.0, 5, 2025),
        (10, "M10", "RICARDO GOMES", "Fiscal de Serviços", "EFETIVO", "Secretaria de Serviços Urbanos", "2012-06-10", 3500.0, 300.0, 350.0, 3450.0, 5, 2025),
        (11, "M11", "ALESSANDRA COSTA", "Pedagoga Escolar", "EFETIVO", "Secretaria de Educação", "2016-04-18", 4800.0, 600.0, 480.0, 4920.0, 5, 2025),
        (12, "M12", "MARCELO SILVEIRA", "Auxiliar de Serviços", "TEMPORARIO", "Secretaria de Administração", "2024-02-01", 1450.0, 0.0, 116.0, 1334.0, 5, 2025)
    ]
    cursor.executemany("INSERT OR REPLACE INTO payroll_records VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);", payroll)

    # 11. Diárias (Doubled diaries and travels)
    # Columns: id, beneficiario_matricula, nome_beneficiario, cargo_servidor, destino, periodo_viagem, justificativa, valor_pago, empenho_id
    diarias = [
        (1, "M2", "MARIA COSTA", "Assessor Técnico", "João Pessoa/PB", "2024-05-10 a 2024-05-11", "Reunião de alinhamento com o TCE-PB sobre prestação de contas", 500.0, "EMP-DIR-001"),
        (2, "M3", "JOAO SANTOS", "Secretário Executivo", "Brasília/DF", "2024-02-10 a 2024-02-15", "Captação de recursos e emendas parlamentares no Ministério da Integração", 3500.0, "EMP-DIR-001"),
        (3, "M3", "JOAO SANTOS", "Secretário Executivo", "Brasília/DF", "2024-03-05 a 2024-03-10", "Captação de recursos federais para obras estruturantes", 3500.0, "EMP-DIR-001"),
        (4, "M3", "JOAO SANTOS", "Secretário Executivo", "Brasília/DF", "2024-04-12 a 2024-04-17", "Reuniões ministeriais de captação de recursos", 3500.0, "EMP-DIR-001"),
        (5, "M3", "JOAO SANTOS", "Secretário Executivo", "Brasília/DF", "2024-05-20 a 2024-05-25", "Audiência pública e articulação de projetos de desenvolvimento urbano", 4500.0, "EMP-DIR-001"),
        # New travel logs
        (6, "M8", "ROBERTO JUNIOR", "Diretor Geral SAMU", "Recife/PE", "2024-06-02 a 2024-06-04", "Congresso Interestadual de Urgência e Emergência Médica", 1200.0, "EMP-DIR-001"),
        (7, "M9", "AMANDA MOREIRA", "Coordenador de Midia", "João Pessoa/PB", "2024-07-10 a 2024-07-11", "Fórum de Comunicação Pública e Redes Sociais do Nordeste", 600.0, "EMP-DIR-001"),
        (8, "M3", "JOAO SANTOS", "Secretário Executivo", "Brasília/DF", "2024-08-15 a 2024-08-20", "Reunião de pleito para emendas no Senado Federal", 4500.0, "EMP-DIR-001")
     ]
    cursor.executemany("INSERT OR REPLACE INTO diarias VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);", diarias)

    # 12. Publicidade (Increased publicity entries)
    # Columns: id, agencia_creditor_id, veiculo_divulgacao, valor, date_ref, secretaria, numero_contrato
    publicidade = [
        (1, "C9", "RADIO ARAPUAN FM LTDA", 300000.0, "2024-06-15", "Coordenadoria de Comunicação Social", "CON-PUB-001/2024"),
        (2, "C9", "TV BORBOREMA MOCK", 400000.0, "2024-07-20", "Secretaria de Educação", "CON-PUB-001/2024"),
        (3, "C9", "PORTAL CELINO NETO MOCK", 300000.0, "2024-09-10", "Gabinete do Prefeito", "CON-PUB-001/2024"),
        (4, "C9", "TV BORBOREMA MOCK", 900000.0, "2025-03-15", "Coordenadoria de Comunicação Social", "CON-PUB-001/2025"),
        (5, "C9", "PORTAL CELINO NETO MOCK", 600000.0, "2025-04-10", "Gabinete do Prefeito", "CON-PUB-001/2025"),
        # New Publicity
        (6, "C9", "PORTAL DIARIO DO NORDESTE MOCK", 250000.0, "2024-08-15", "Coordenadoria de Comunicação Social", "CON-PUB-001/2024"),
        (7, "C9", "PORTAL DIARIO DO NORDESTE MOCK", 500000.0, "2025-05-12", "Coordenadoria de Comunicação Social", "CON-PUB-001/2025")
    ]
    cursor.executemany("INSERT OR REPLACE INTO publicidade VALUES (?, ?, ?, ?, ?, ?, ?);", publicidade)

    # 13. Emendas (Increased parliamentary amendments)
    # Columns: id, parlamentar, valor, projeto, secretaria_destinataria, empenho_id
    emendas = [
        (1, "Deputado Romero Rodrigues Mock", 200000.0, "Aquisição de ambulâncias e insumos hospitalares", "Secretaria de Saúde", "EMP-001"),
        (2, "Vereador Sargento Neto Mock", 100000.0, "Reforma da quadra esportiva escolar", "Secretaria de Educação", "EMP-005"),
        (3, "Senador Veneziano Vital Mock", 1500000.0, "Pavimentação e drenagem de vias urbanas", "Secretaria de Serviços Urbanos", "EMP-006"),
        # New amendments
        (4, "Deputado Aguinaldo Ribeiro Mock", 500000.0, "Reforma de Postos de Saúde da Família", "Secretaria de Saúde", "EMP-014"),
        (5, "Senador Efraim Filho Mock", 1200000.0, "Pavimentação asfáltica e drenagem", "Secretaria de Serviços Urbanos", "EMP-018")
    ]
    cursor.executemany("INSERT OR REPLACE INTO emendas VALUES (?, ?, ?, ?, ?, ?);", emendas)

    # 14. Dívida Ativa (Increased debtors list)
    # Columns: id, creditor_id, valor_devido, origem_debito, data_inscricao
    divida = [
        (1, "C18", 150000.0, "ISS devido referente aos anos fiscais 2021-2022", "2023-01-15"),
        (2, "C3", 800000.0, "IPTU em atraso sobre terrenos industriais no Distrito Industrial", "2022-11-20"),
        (3, "C2", 15000.0, "Taxas de Licenciamento Ambiental e Fiscalização", "2024-02-10"),
        # New active debts
        (4, "C22", 90000.0, "Multas de trânsito e licenciamentos de frota operacional", "2023-08-15"),
        (5, "C33", 220000.0, "ISS em atraso sobre serviços de locação de veículos 2023", "2024-01-12")
    ]
    cursor.executemany("INSERT OR REPLACE INTO divida_ativa VALUES (?, ?, ?, ?, ?);", divida)

    # 15. Sanções (Increased sanctioned suppliers)
    # Columns: id, creditor_id, tipo_sancao, orgao_sancionador, data_inicio, data_fim
    sancoes = [
        (1, "C19", "DECLARAÇÃO DE INIDONEIDADE", "Tribunal de Contas da União", "2023-05-10", "2026-05-10"),
        (2, "C19", "SUSPENSÃO TEMPORÁRIA", "Prefeitura de João Pessoa", "2025-01-15", "2025-07-15"),
        # New sanction
        (3, "C34", "IMPEDIMENTO DE LICITAR", "Tribunal de Contas do Estado da Paraíba", "2024-03-01", "2027-03-01")
    ]
    cursor.executemany("INSERT OR REPLACE INTO sancoes VALUES (?, ?, ?, ?, ?, ?);", sancoes)

    # 16. Relações Políticas (Doubled political connection entries)
    # Columns: id, creditor_id, nome_socio, doador_pf, fornecedor_campanha, candidato_beneficiario, partido
    tse_politicas = [
        (1, "C20", "PEDRO FILHO MOCK", 50000.0, 120000.0, "Prefeito Bruno Cunha Lima", "PSD"),
        (2, "C2", "ADALBERTO BOA VISTA", 10000.0, 0.0, "Prefeito Bruno Cunha Lima", "PSD"),
        (3, "C3", "INFRAESTRUTURA ADMIN MOCK", 0.0, 250000.0, "Governador João Azevêdo", "PSB"),
        # New political relations
        (4, "C22", "JOSE SAO JOSE", 15000.0, 0.0, "Prefeito Bruno Cunha Lima", "PSD"),
        (5, "C31", "MANUEL SOFT-CG", 5000.0, 80000.0, "Prefeito Bruno Cunha Lima", "PSD")
    ]
    cursor.executemany("INSERT OR REPLACE INTO relacoes_politicas VALUES (?, ?, ?, ?, ?, ?, ?);", tse_politicas)

    # 17. Convênios (Increased NGO agreements)
    # Columns: id, entidade_creditor_id, tipo_termo, objeto, valor, vigencia_inicio, vigencia_fim, secretaria
    convenios = [
        (1, "C14", "Termo de Fomento", "Realização de oficinas de arte, dança e teatro popular durante o período junino", 150000.0, "2024-05-01", "2024-08-01", "Secretaria de Cultura"),
        (2, "C14", "Termo de Colaboração", "Capacitação profissional e inclusão social para jovens da periferia", 180000.0, "2024-09-01", "2025-03-01", "Secretaria de Administração"),
        # New NGO Convênios
        (3, "C30", "Termo de Fomento", "Incentivo e amparo aos desportistas amadores dos bairros periféricos de CG", 120000.0, "2024-06-15", "2024-12-15", "Secretaria de Cultura")
    ]
    cursor.executemany("INSERT OR REPLACE INTO convenios VALUES (?, ?, ?, ?, ?, ?, ?, ?);", convenios)

    # 18. Receitas (Increased municipal income entries)
    receitas = [
        (1, 2024, "1.1.1.0.00.0.0", "Imposto sobre a Propriedade Predial e Territorial Urbana - IPTU", 50000000.0, 52000000.0, 2000000.0, "2024-12-31"),
        (2, 2024, "1.1.2.0.00.0.0", "Imposto sobre Serviços de Qualquer Natureza - ISS", 80000000.0, 83500000.0, 3500000.0, "2024-12-31"),
        (3, 2025, "1.1.1.0.00.0.0", "Imposto sobre a Propriedade Predial e Territorial Urbana - IPTU", 55000000.0, 35000000.0, -20000000.0, "2025-05-30"),
        (4, 2024, "1.7.1.0.00.0.0", "Fundo de Participação dos Municípios - FPM", 120000000.0, 125000000.0, 5000000.0, "2024-12-31"),
        # New Revenues
        (5, 2025, "1.1.2.0.00.0.0", "Imposto sobre Serviços de Qualquer Natureza - ISS", 85000000.0, 50000000.0, -35000000.0, "2025-05-30")
    ]
    cursor.executemany("INSERT OR REPLACE INTO receitas VALUES (?, ?, ?, ?, ?, ?, ?, ?);", receitas)

    # 19. Veículos Frota (Increased fleet list)
    # Columns: placa, modelo, marca, secretaria_alocada, tipo_aquisicao
    frota = [
        ("QXV-9A99", "Toyota Hilux 4x4", "Toyota", "Secretaria de Saúde", "Locado"),
        ("KJZ-1234", "Fiat Cronos Drive", "Fiat", "Gabinete do Prefeito", "Proprio"),
        ("MNO-5678", "Volkswagen Gol 1.0", "VW", "Secretaria de Educação", "Terceirizado"),
        ("OFS-9876", "Chevrolet Spin 7L", "Chevrolet", "Secretaria de Saúde", "Proprio"),
        ("PXT-4567", "Ford Ka Sedan", "Ford", "Secretaria de Administração", "Locado"),
        # New vehicles
        ("NXX-1100", "Fiat Toro Freedom", "Fiat", "Secretaria de Serviços Urbanos", "Proprio"),
        ("KXY-8877", "Toyota Etios Hatch", "Toyota", "Secretaria de Administração", "Terceirizado"),
        ("MNB-3344", "VW Voyage Trend", "VW", "Secretaria de Educação", "Locado")
    ]
    cursor.executemany("INSERT OR REPLACE INTO veiculos_frota VALUES (?, ?, ?, ?, ?);", frota)

    # 20. Despesas Frota (Increased logs of fuel/maintenance)
    # Columns: id, veiculo_placa, data, tipo_despesa, valor, litros
    despesas_frota = [
        (1, "QXV-9A99", "2024-05-01", "COMBUSTIVEL", 350.0, 50.0),
        (2, "QXV-9A99", "2024-05-15", "MANUTENÇÃO", 1200.0, None),
        (3, "KJZ-1234", "2024-05-02", "COMBUSTIVEL", 250.0, 45.0),
        (4, "KJZ-1234", "2024-05-20", "COMBUSTIVEL", 260.0, 46.0),
        (5, "MNO-5678", "2024-05-03", "COMBUSTIVEL", 210.0, 38.0),
        (6, "OFS-9876", "2024-05-04", "COMBUSTIVEL", 280.0, 48.0),
        (7, "OFS-9876", "2024-05-18", "MANUTENÇÃO", 850.0, None),
        (8, "PXT-4567", "2024-05-05", "COMBUSTIVEL", 180.0, 32.0),
        # New fuel logs
        (9, "NXX-1100", "2024-05-08", "COMBUSTIVEL", 320.0, 55.0),
        (10, "KXY-8877", "2024-05-12", "COMBUSTIVEL", 190.0, 34.0),
        (11, "MNB-3344", "2024-05-14", "COMBUSTIVEL", 220.0, 39.0),
        (12, "NXX-1100", "2024-05-25", "MANUTENÇÃO", 450.0, None)
    ]
    cursor.executemany("INSERT OR REPLACE INTO despesas_frota VALUES (?, ?, ?, ?, ?, ?);", despesas_frota)

    conn.commit()
    conn.close()
    print("Database seeding completed successfully with doubled data scale!")

if __name__ == "__main__":
    seed_db()
