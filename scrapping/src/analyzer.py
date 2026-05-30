import sqlite3
import os
import json

DATABASE_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/transparencia_cg.db"))

class CidadeAbertaAnalyzer:
    def __init__(self, db_path=None):
        self.db_path = db_path if db_path else DATABASE_FILE

    def get_connection(self):
        """Establishes connection to the SQLite database with dictionary rows."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    # 1. Ranking Geral de Fornecedores
    def get_supplier_ranking(self):
        """
        Calcula o ranking geral de fornecedores por valor total empenhado,
        valor total pago, número de contratos, secretarias atendidas, e crescimento anual.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        query = """
            SELECT 
                c.id AS creditor_id,
                c.name AS supplier_name,
                c.cpf_cnpj AS cpf_cnpj,
                COUNT(DISTINCT e.id) AS num_empenhos,
                COUNT(DISTINCT ct.numero_contrato) AS num_contratos,
                COUNT(DISTINCT e.organ_code) AS num_secretarias,
                SUM(e.amount_empenhado) AS total_empenhado,
                SUM(e.amount_pago) AS total_pago,
                CASE WHEN COUNT(DISTINCT ct.numero_contrato) > 0 
                     THEN SUM(ct.valor_contrato) / COUNT(DISTINCT ct.numero_contrato)
                     ELSE 0 END AS valor_medio_contrato,
                GROUP_CONCAT(DISTINCT e.exercicio) AS anos_ativos
            FROM creditors c
            LEFT JOIN empenhos e ON c.id = e.creditor_id
            LEFT JOIN contratos ct ON c.id = ct.contratado_creditor_id
            GROUP BY c.id
            HAVING total_empenhado > 0 OR total_pago > 0 OR num_contratos > 0
            ORDER BY total_empenhado DESC;
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    # 2. Padrões de Contratação Direta e Alertas de Fracionamento
    def get_procurement_patterns(self):
        """
        Analisa as modalidades de contratação cruzando com secretarias e fornecedores.
        Identifica concentrações de dispensas/inexigibilidades e possíveis fracionamentos.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # 2a. Ranking por Contratação Direta
        direct_ranking_query = """
            SELECT 
                cr.cpf_cnpj AS cnpj,
                cr.name AS supplier_name,
                SUM(CASE WHEN l.modalidade = 'DISPENSA DE LICITAÇÃO' THEN 1 ELSE 0 END) AS num_dispensas,
                SUM(CASE WHEN l.modalidade = 'INEXIGIBILIDADE' THEN 1 ELSE 0 END) AS num_inexigibilidades,
                SUM(e.amount_empenhado) AS total_valor,
                GROUP_CONCAT(DISTINCT org.name) AS secretarias,
                GROUP_CONCAT(DISTINCT l.objeto) AS objetos_frequentes
            FROM creditors cr
            JOIN empenhos e ON cr.id = e.creditor_id
            JOIN organs org ON e.organ_code = org.code AND e.institution_id = org.institution_id
            JOIN contratos ct ON cr.id = ct.contratado_creditor_id
            JOIN licitacoes l ON ct.licitacao_processo = l.processo
            WHERE l.modalidade IN ('DISPENSA DE LICITAÇÃO', 'INEXIGIBILIDADE')
            GROUP BY cr.id
            ORDER BY total_valor DESC;
        """
        
        # 2b. Alertas de Fracionamento de Despesa Suspeitos
        # Vários empenhos no mesmo dia/mês para o mesmo credor e elemento de despesa
        fractioning_query = """
            SELECT 
                cr.name AS supplier_name,
                e.date_emission,
                e.element_code,
                el.name AS element_name,
                COUNT(*) AS num_ocorrencias,
                SUM(e.amount_empenhado) AS total_valor,
                GROUP_CONCAT(e.id) AS empenho_ids,
                GROUP_CONCAT(e.project_name) AS objetos
            FROM empenhos e
            JOIN creditors cr ON e.creditor_id = cr.id
            JOIN expense_elements el ON e.element_code = el.code
            WHERE e.element_code IN ('339030', '339039') -- material de consumo e serviços PJ
            GROUP BY e.creditor_id, e.date_emission, e.element_code
            HAVING COUNT(*) > 1 AND total_valor > 10000
            ORDER BY num_ocorrencias DESC;
        """
        
        cursor.execute(direct_ranking_query)
        direct_ranking = [dict(r) for r in cursor.fetchall()]
        
        cursor.execute(fractioning_query)
        fractioning_alerts = [dict(r) for r in cursor.fetchall()]
        
        conn.close()
        return {
            "direct_ranking": direct_ranking,
            "fractioning_alerts": fractioning_alerts
        }

    # 3. Monopólios / Concentração por Categorias de Gasto
    def get_monopolies_by_category(self):
        """
        Classifica as contratações em 14 categorias e identifica fornecedores dominantes.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = """
            WITH categorized_expenses AS (
                SELECT 
                    e.id AS empenho_id,
                    e.amount_empenhado,
                    e.exercicio,
                    cr.name AS creditor_name,
                    cr.id AS creditor_id,
                    CASE 
                        WHEN e.project_name LIKE '%limpeza%' OR e.project_name LIKE '%lixo%' THEN 'Limpeza Urbana'
                        WHEN e.project_name LIKE '%alimenta%' OR e.project_name LIKE '%merenda%' OR e.project_name LIKE '%pão%' OR e.project_name LIKE '%panificadora%' THEN 'Alimentação'
                        WHEN e.project_name LIKE '%medicamento%' OR e.project_name LIKE '%remédio%' OR e.project_name LIKE '%farmácia%' OR e.element_code = '339030' AND e.project_name LIKE '%saúde%' THEN 'Medicamentos'
                        WHEN e.project_name LIKE '%transporte%' OR e.project_name LIKE '%escolar%' THEN 'Transporte Escolar'
                        WHEN e.project_name LIKE '%locação%' OR e.project_name LIKE '%aluguel%veículo%' THEN 'Locação de Veículos'
                        WHEN e.project_name LIKE '%tecnologia%' OR e.project_name LIKE '%sistema%' OR e.project_name LIKE '%software%' OR e.project_name LIKE '%licenciamento%' THEN 'Tecnologia'
                        WHEN e.project_name LIKE '%publicidade%' OR e.project_name LIKE '%propaganda%' OR e.project_name LIKE '%divulgação%' THEN 'Publicidade'
                        WHEN e.project_name LIKE '%evento%' OR e.project_name LIKE '%show%' OR e.project_name LIKE '%cultura%' OR e.project_name LIKE '%são joão%' OR e.project_name LIKE '%festa%' THEN 'Eventos e Cultura'
                        WHEN e.project_name LIKE '%obra%' OR e.project_name LIKE '%construção%' OR e.project_name LIKE '%canal%' THEN 'Obras'
                        WHEN e.project_name LIKE '%manutenção%' OR e.project_name LIKE '%reforma%' THEN 'Manutenção Predial'
                        WHEN e.project_name LIKE '%expediente%' OR e.project_name LIKE '%papelaria%' THEN 'Material de Expediente'
                        WHEN e.project_name LIKE '%vigilância%' OR e.project_name LIKE '%segurança%' THEN 'Vigilância'
                        WHEN e.project_name LIKE '%terceiriz%' OR e.project_name LIKE '%mão de obra%' THEN 'Serviços Terceirizados'
                        WHEN e.project_name LIKE '%combustível%' OR e.project_name LIKE '%gasolina%' OR e.project_name LIKE '%diesel%' THEN 'Combustíveis'
                        ELSE 'Outros'
                    END AS categoria
                FROM empenhos e
                JOIN creditors cr ON e.creditor_id = cr.id
            )
            SELECT 
                categoria,
                creditor_name,
                SUM(amount_empenhado) AS total_gasto,
                exercicio,
                COUNT(*) AS num_ocorrencias
            FROM categorized_expenses
            WHERE categoria != 'Outros'
            GROUP BY categoria, creditor_id, exercicio
            ORDER BY categoria ASC, total_gasto DESC;
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    # 4. Gastos com Saúde
    def get_health_spending_analysis(self):
        """
        Retorna detalhes dos gastos de saúde: fornecedores campeões,
        insumos caros, concentração e compras emergenciais.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT 
                cr.name AS supplier_name,
                e.project_name AS item_or_project,
                SUM(e.amount_empenhado) AS total_empenhado,
                SUM(e.amount_pago) AS total_pago,
                e.exercicio,
                SUM(CASE WHEN e.element_code = '339039' THEN e.amount_empenhado ELSE 0 END) AS valor_servicos,
                SUM(CASE WHEN e.element_code = '339030' THEN e.amount_empenhado ELSE 0 END) AS valor_insumos
            FROM empenhos e
            JOIN creditors cr ON e.creditor_id = cr.id
            WHERE e.organ_code IN ('10300', '20100') OR e.function_code = '10'
            GROUP BY cr.id, e.project_name, e.exercicio
            ORDER BY total_empenhado DESC;
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    # 5. Gastos com Educação
    def get_education_spending_analysis(self):
        """
        Retorna detalhes dos gastos com educação: merenda, transporte, didático, etc.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        query = """
            SELECT 
                cr.name AS supplier_name,
                e.project_name AS item_or_project,
                SUM(e.amount_empenhado) AS total_empenhado,
                SUM(e.amount_pago) AS total_pago,
                e.exercicio
            FROM empenhos e
            JOIN creditors cr ON e.creditor_id = cr.id
            WHERE e.organ_code = '10400' OR e.function_code = '12'
            GROUP BY cr.id, e.project_name, e.exercicio
            ORDER BY total_empenhado DESC;
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    # 6. Publicidade Institucional
    def get_publicity_spending(self):
        """
        Analisa a evolução dos gastos com publicidade e propaganda
        identificando aumentos em anos eleitorais (ex: 2024).
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        query = """
            SELECT 
                cr.name AS agency_name,
                p.veiculo_divulgacao AS vehicle,
                p.secretaria AS department,
                SUM(p.valor) AS total_pago,
                SUBSTR(p.date_ref, 1, 4) AS ano
            FROM publicidade p
            JOIN creditors cr ON p.agencia_creditor_id = cr.id
            GROUP BY p.agencia_creditor_id, p.veiculo_divulgacao, ano
            ORDER BY ano ASC, total_pago DESC;
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    # 7. Eventos, Cultura e São João
    def get_sao_joao_events_analysis(self):
        """
        Analisa gastos com eventos, palcos, som, cachês artísticos e logísticas
        envolvendo festejos juninos / cultura.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        query = """
            SELECT 
                cr.name AS supplier_name,
                l.modalidade AS procurement_mode,
                ct.valor_contrato AS contract_value,
                l.objeto AS object_description,
                l.data_abertura AS event_date
            FROM licitacoes l
            JOIN contratos ct ON l.processo = ct.licitacao_processo
            JOIN creditors cr ON ct.contratado_creditor_id = cr.id
            WHERE l.objeto LIKE '%são joão%' 
               OR l.objeto LIKE '%evento%' 
               OR l.objeto LIKE '%artístico%' 
               OR l.objeto LIKE '%show%' 
               OR l.objeto LIKE '%palco%' 
               OR l.objeto LIKE '%som%' 
               OR l.objeto LIKE '%cultura%'
            ORDER BY contract_value DESC;
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    # 8. Diárias e Passagens
    def get_travel_diarias_analysis(self):
        """
        Mapeia gastos administrativos com diárias e passagens de servidores.
        Identifica maiores beneficiários e destinos recorrentes.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        query = """
            SELECT 
                d.nome_beneficiario AS servant_name,
                d.cargo_servidor AS role,
                d.destino AS destination,
                d.periodo_viagem AS travel_period,
                d.justificativa AS justification,
                d.valor_pago AS amount_paid,
                pr.lotacao AS department
            FROM diarias d
            LEFT JOIN payroll_records pr ON d.beneficiario_matricula = pr.matricula
            ORDER BY amount_paid DESC;
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    # 9. Terceirizações, Temporários e Pessoal
    def get_payroll_staff_analysis(self):
        """
        Analisa a estrutura de pessoal da prefeitura por secretaria,
        comparando efetivos, temporários, comissionados e terceirizados.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # 9a. Proporção Folha por Secretaria
        staff_query = """
            SELECT 
                lotacao AS department,
                SUM(CASE WHEN tipo_vinculo = 'EFETIVO' THEN 1 ELSE 0 END) AS num_efetivos,
                SUM(CASE WHEN tipo_vinculo = 'COMISSIONADO' THEN 1 ELSE 0 END) AS num_comissionados,
                SUM(CASE WHEN tipo_vinculo = 'TEMPORARIO' THEN 1 ELSE 0 END) AS num_temporarios,
                SUM(salario_base) AS total_salario_base,
                SUM(salario_liquido) AS total_salario_liquido,
                mes,
                ano
            FROM payroll_records
            GROUP BY lotacao, mes, ano
            ORDER BY total_salario_liquido DESC;
        """
        
        # 9b. Contratos de Terceirizados Identificados
        outsourced_query = """
            SELECT 
                cr.name AS outsourced_company,
                org.name AS department,
                SUM(e.amount_empenhado) AS total_spent
            FROM empenhos e
            JOIN creditors cr ON e.creditor_id = cr.id
            JOIN organs org ON e.organ_code = org.code AND e.institution_id = org.institution_id
            WHERE e.element_code = '339039' AND (
                e.project_name LIKE '%vigilância%' 
                OR e.project_name LIKE '%segurança%' 
                OR e.project_name LIKE '%limpeza%' 
                OR e.project_name LIKE '%terceiriz%'
            )
            GROUP BY cr.id, e.organ_code
            ORDER BY total_spent DESC;
        """
        
        cursor.execute(staff_query)
        staff_structure = [dict(r) for r in cursor.fetchall()]
        
        cursor.execute(outsourced_query)
        outsourced_spent = [dict(r) for r in cursor.fetchall()]
        
        conn.close()
        return {
            "staff_structure": staff_structure,
            "outsourced_spent": outsourced_spent
        }

    # 10. Frota, Combustível, Manutenção e Locação de Veículos
    def get_fleet_fuel_efficiency(self):
        """
        Cruza informações da frota municipal com custos de abastecimento
        e reparos mecânicos.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        query = """
            SELECT 
                vf.placa AS plate,
                vf.modelo AS model,
                vf.marca AS brand,
                vf.secretaria_alocada AS department,
                vf.tipo_aquisicao AS acquisition_type,
                SUM(CASE WHEN df.tipo_despesa = 'COMBUSTIVEL' THEN df.valor ELSE 0 END) AS spent_fuel,
                SUM(CASE WHEN df.tipo_despesa = 'COMBUSTIVEL' THEN df.litros ELSE 0 END) AS total_liters,
                SUM(CASE WHEN df.tipo_despesa = 'MANUTENÇÃO' THEN df.valor ELSE 0 END) AS spent_maintenance,
                CASE WHEN SUM(CASE WHEN df.tipo_despesa = 'COMBUSTIVEL' THEN df.litros ELSE 0 END) > 0 
                     THEN SUM(CASE WHEN df.tipo_despesa = 'COMBUSTIVEL' THEN df.valor ELSE 0 END) / 
                          SUM(CASE WHEN df.tipo_despesa = 'COMBUSTIVEL' THEN df.litros ELSE 0 END)
                     ELSE 0 END AS price_per_liter
            FROM veiculos_frota vf
            LEFT JOIN despesas_frota df ON vf.placa = df.veiculo_placa
            GROUP BY vf.placa
            ORDER BY spent_fuel DESC, spent_maintenance DESC;
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    # 11. Convênios, Parcerias e ONGs
    def get_ngo_partnerships_analysis(self):
        """
        Analisa repasses para entidades sem fins lucrativos e organizações sociais.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        query = """
            SELECT 
                cr.name AS entity_name,
                cv.tipo_termo AS partnership_type,
                cv.objeto AS purpose,
                cv.valor AS total_value,
                cv.vigencia_inicio AS start_date,
                cv.vigencia_fim AS end_date,
                cv.secretaria AS department
            FROM convenios cv
            JOIN creditors cr ON cv.entidade_creditor_id = cr.id
            ORDER BY total_value DESC;
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    # 12. Emendas Parlamentares
    def get_amendment_pathway(self):
        """
        Rastreia o caminho do dinheiro: Parlamentar -> Emenda -> Empenho -> Credor Executor.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        query = """
            SELECT 
                em.parlamentar AS politician_name,
                em.valor AS amendment_value,
                em.projeto AS amendment_project,
                em.secretaria_destinataria AS department,
                emp.id AS empenho_id,
                cr.name AS executing_supplier,
                emp.amount_empenhado AS spent_empenhado,
                emp.amount_pago AS spent_pago
            FROM emendas em
            LEFT JOIN empenhos emp ON em.empenho_id = emp.id
            LEFT JOIN creditors cr ON emp.creditor_id = cr.id
            ORDER BY em.valor DESC;
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    # 13. Dívida Ativa vs Recebimentos
    def get_active_debt_crossings(self):
        """
        Identifica empresas contratadas pela prefeitura que simultaneamente
        aparecem na lista de devedores tributários do município.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        query = """
            SELECT 
                cr.name AS supplier_name,
                cr.cpf_cnpj AS cpf_cnpj,
                da.valor_devido AS active_debt_amount,
                da.origem_debito AS debt_origin,
                da.data_inscricao AS registry_date,
                COALESCE(SUM(e.amount_empenhado), 0) AS total_empenhado_prefeitura,
                COALESCE(SUM(e.amount_pago), 0) AS total_pago_prefeitura
            FROM divida_ativa da
            JOIN creditors cr ON da.creditor_id = cr.id
            LEFT JOIN empenhos e ON cr.id = e.creditor_id
            GROUP BY cr.id
            ORDER BY active_debt_amount DESC;
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    # 14. Licitantes Sancionados
    def get_sanctioned_supplier_crossings(self):
        """
        Cruza a base de licitantes sancionados com contratos ativos ou empenhos vigentes.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        query = """
            SELECT 
                cr.name AS supplier_name,
                sa.tipo_sancao AS sanction_type,
                sa.orgao_sancionador AS sanctioning_body,
                sa.data_inicio AS start_date,
                sa.data_fim AS end_date,
                ct.numero_contrato AS contract_number,
                ct.valor_contrato AS contract_value,
                ct.vigencia_inicio AS contract_start,
                ct.vigencia_fim AS contract_end
            FROM sancoes sa
            JOIN creditors cr ON sa.creditor_id = cr.id
            LEFT JOIN contratos ct ON cr.id = ct.contratado_creditor_id
            ORDER BY sa.data_inicio DESC;
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    # 15. Relações Políticas (TSE / Doadores)
    def get_political_connections(self):
        """
        Mapeia conexões políticas públicas documentadas:
        Sócios de empresas doadoras de campanha eleitoral que receberam contratos públicos.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        query = """
            SELECT 
                cr.name AS supplier_name,
                rp.nome_socio AS partner_name,
                rp.doador_pf AS pf_donation,
                rp.fornecedor_campanha AS campaign_supplying,
                rp.candidato_beneficiario AS politician_beneficiary,
                rp.partido AS party,
                COALESCE(SUM(e.amount_empenhado), 0) AS total_spent_prefeitura
            FROM relacoes_politicas rp
            JOIN creditors cr ON rp.creditor_id = cr.id
            LEFT JOIN empenhos e ON cr.id = e.creditor_id
            GROUP BY cr.id, rp.nome_socio
            ORDER BY total_spent_prefeitura DESC;
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    # 16. Análise de Redes (Nodes & Edges para Grafos)
    def get_network_graph_data(self):
        """
        Gera uma estrutura complexa de nós (nodes) e conexões (edges) no formato
        JSON para visualização de grafos de relacionamentos públicos.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        nodes = []
        edges = []
        node_ids = set()

        def add_node(nid, label, group):
            if nid not in node_ids:
                nodes.append({"id": nid, "label": label, "group": group})
                node_ids.add(nid)

        # 16a. Empresas e Empenhos / Secretarias
        cursor.execute("""
            SELECT 
                e.id AS empenho_id,
                e.code AS empenho_code,
                e.amount_empenhado AS valor,
                cr.id AS creditor_id,
                cr.name AS supplier_name,
                org.code AS organ_code,
                org.name AS organ_name
            FROM empenhos e
            JOIN creditors cr ON e.creditor_id = cr.id
            JOIN organs org ON e.organ_code = org.code AND e.institution_id = org.institution_id
            LIMIT 50; -- limit representation size to keep it clean
        """)
        for r in cursor.fetchall():
            add_node(r["creditor_id"], r["supplier_name"], "Empresa")
            add_node(r["organ_code"], r["organ_name"], "Secretaria")
            add_node(r["empenho_id"], f"Empenho {r['empenho_code']}\n(R$ {r['valor']:,.2f})", "Empenho")
            
            edges.append({"from": r["organ_code"], "to": r["empenho_id"], "label": "emitiu"})
            edges.append({"from": r["empenho_id"], "to": r["creditor_id"], "label": "pagou"})

        # 16b. Relações Políticas e Sócios
        cursor.execute("""
            SELECT 
                rp.nome_socio,
                rp.creditor_id,
                rp.candidato_beneficiario,
                rp.partido,
                rp.doador_pf
            FROM relacoes_politicas rp;
        """)
        for r in cursor.fetchall():
            partner_node_id = f"socio_{r['nome_socio'].replace(' ', '_')}"
            politician_node_id = f"pol_{r['candidato_beneficiario'].replace(' ', '_')}"
            
            add_node(partner_node_id, r["nome_socio"], "Sócio")
            add_node(politician_node_id, f"{r['candidato_beneficiario']} ({r['partido']})", "Político")
            add_node(r["creditor_id"], "", "Empresa") # ensure creditor is added
            
            edges.append({"from": partner_node_id, "to": r["creditor_id"], "label": "sócio-proprietário"})
            if r["doador_pf"] > 0:
                edges.append({"from": partner_node_id, "to": politician_node_id, "label": f"doou R$ {r['doador_pf']:,.2f}"})

        # 16c. Emendas Parlamentares
        cursor.execute("""
            SELECT 
                em.parlamentar,
                em.empenho_id,
                em.valor
            FROM emendas em
            WHERE em.empenho_id IS NOT NULL;
        """)
        for r in cursor.fetchall():
            parlamentar_node_id = f"parl_{r['parlamentar'].replace(' ', '_')}"
            add_node(parlamentar_node_id, r["parlamentar"], "Parlamentar")
            
            if r["empenho_id"] in node_ids:
                edges.append({"from": parlamentar_node_id, "to": r["empenho_id"], "label": f"financiou R$ {r['valor']:,.2f}"})

        conn.close()
        return {"nodes": nodes, "edges": edges}

    # 17. Principais Destaques / Sugestões
    def get_top_highlights(self):
        """
        Retorna um resumo executivo dos 7 melhores cruzamentos analíticos sugeridos.
        """
        supplier_ranking = self.get_supplier_ranking()[:3]
        proc = self.get_procurement_patterns()
        active_debt = self.get_active_debt_crossings()[:3]
        political = self.get_political_connections()[:3]
        
        return {
            "top_suppliers": supplier_ranking,
            "procurement_totals": len(proc["direct_ranking"]),
            "fractioning_count": len(proc["fractioning_alerts"]),
            "active_debt_count": len(active_debt),
            "political_count": len(political)
        }

    # 18. Recorte de Pesquisa / Auditoria Forense Completa
    def get_forensic_research_summary(self):
        """
        Implementa a análise integrada e forense sem acusações diretas, 
        destacando conexões de governança, dívidas, doações e licitações.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Cruzamento principal: Empresa -> Dívida Ativa -> Doações TSE -> Contratos Totais
        query = """
            SELECT 
                cr.name AS supplier_name,
                cr.cpf_cnpj AS cpf_cnpj,
                COALESCE(da.valor_devido, 0) AS active_debt,
                COALESCE(rp.doador_pf, 0) AS campaign_donation,
                COALESCE(rp.candidato_beneficiario, 'N/A') AS politician,
                COALESCE(SUM(e.amount_empenhado), 0) AS total_received,
                COUNT(DISTINCT e.id) AS num_empenhos
            FROM creditors cr
            LEFT JOIN divida_ativa da ON cr.id = da.creditor_id
            LEFT JOIN relacoes_politicas rp ON cr.id = rp.creditor_id
            LEFT JOIN empenhos e ON cr.id = e.creditor_id
            GROUP BY cr.id
            HAVING active_debt > 0 OR campaign_donation > 0
            ORDER BY total_received DESC;
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    # 19. Qualidade dos Dados / Erros e Lacunas Ingeridas
    def get_scraper_errors_summary(self):
        """
        Retorna um sumário estruturado de inconsistências e lacunas de dados 
        encontrados na API do Portal da Transparência de Campina Grande.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # 1. Total count of errors
            cursor.execute("SELECT COUNT(*) FROM scraper_errors")
            total_errors = cursor.fetchone()[0]
            
            # 2. Count by level
            cursor.execute("""
                SELECT level, COUNT(*) AS count 
                FROM scraper_errors 
                GROUP BY level 
                ORDER BY count DESC
            """)
            by_level = [dict(r) for r in cursor.fetchall()]
            
            # 3. Recent errors sample
            cursor.execute("""
                SELECT timestamp, level, error_message, context_info 
                FROM scraper_errors 
                ORDER BY id DESC 
                LIMIT 10
            """)
            recent_samples = [dict(r) for r in cursor.fetchall()]
        except sqlite3.OperationalError:
            total_errors = 0
            by_level = []
            recent_samples = []
            
        conn.close()
        return {
            "total_errors": total_errors,
            "by_level": by_level,
            "recent_samples": recent_samples
        }

