import streamlit as st
import pandas as pd
import time
from datetime import datetime
from controllers.apostador_controller import ApostadorController
from controllers.jogo_controller import JogoController
from controllers.pagamento_controller import PagamentoController

class PagamentoView:
    @staticmethod
    def show_form():
        """Exibe o formulário principal de pagamentos"""
        st.header("💰 Registrar Pagamento")
        
        if not st.session_state.get('user'):
            st.error("Você precisa estar logado para acessar esta página!")
            return
            
        PagamentoView._show_register_form()


    @staticmethod
    def _show_register_form():
        """Formulário de registro de pagamento"""
        with st.form(key="form_registrar_pagamento", clear_on_submit=True):
            st.subheader("Registrar Novo Pagamento")
            
            # 1. Seleção do apostador
            apostadores = ApostadorController.get_all_active()
            if not apostadores:
                st.warning("Nenhum apostador cadastrado!")
                return
                
            apelido = st.selectbox(
                "Apostador*",
                options=[a['apelido'] for a in apostadores],
                format_func=lambda x: f"{x} ({next(a['nome'] for a in apostadores if a['apelido'] == x)})"
            )
            
            # 2. Buscar jogos reservados
            try:
                jogos_reservados = JogoController.get_reserved_games(apelido)
                
                if not jogos_reservados:
                    st.warning("Nenhum jogo reservado para este apostador!")
                    return
                    
                # 3. Seleção de jogos
                jogo_options = {
                    f"{j['numero']} (Evento: {j['evento_nome']}) - R$ {j['valor']:.2f}": j['numero']
                    for j in jogos_reservados
                }
                
                selected = st.multiselect(
                    "Jogos para pagamento*",
                    options=list(jogo_options.keys()),
                    default=list(jogo_options.keys())
                )
                
                # 4. Dados do pagamento
                col1, col2 = st.columns(2)
                numero_pagamento = col1.text_input("Número do Pagamento*", max_chars=20)
                valor_total = col2.number_input(
                    "Valor Total (R$)*",
                    min_value=0.0,
                    value=sum(j['valor'] for j in jogos_reservados if f"{j['numero']} (Evento:" in selected),
                    format="%.2f"
                )
                
                metodo = st.selectbox(
                    "Método de Pagamento*",
                    ["PIX", "Dinheiro", "Cartão Débito", "Cartão Crédito", "Transferência"]
                )
                
                observacoes = st.text_area("Observações")
                
                # BOTÃO DE SUBMIT CORRETO
                submitted = st.form_submit_button("Registrar Pagamento")
                
                if submitted:
                    if not numero_pagamento or not selected:
                        st.error("Campos obrigatórios não preenchidos!")
                        return
                    
                    numeros_jogos = [jogo_options[j] for j in selected]
                    
                    try:
                        PagamentoController.create(
                            numero=numero_pagamento,
                            apelido=apelido,
                            valor=valor_total,
                            metodo=metodo,
                            observacoes=observacoes,
                            jogos=numeros_jogos
                        )
                        st.success("Pagamento registrado com sucesso!")
                        time.sleep(1)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao registrar pagamento: {str(e)}")
                        
            except Exception as e:
                st.error(f"Erro ao buscar jogos reservados: {str(e)}")
                            
            
    @staticmethod
    def _show_search_form():
        """Formulário de consulta de pagamentos"""
        st.subheader("Consultar Pagamentos")
        
        with st.expander("🔍 Filtros Avançados", expanded=False):
            col1, col2 = st.columns(2)
            apelido_filter = col1.selectbox(
                "Filtrar por apostador",
                ["Todos"] + [a['apelido'] for a in ApostadorController.get_all_active()],
                index=0
            )
            status_filter = col2.selectbox(
                "Filtrar por status",
                ["Todos", "Pendente", "Confirmado", "Cancelado"],
                index=0
            )
            
            col1, col2 = st.columns(2)
            data_inicio = col1.date_input("Data inicial", value=datetime.now().replace(day=1))
            data_fim = col2.date_input("Data final", value=datetime.now())
            
            metodo_filter = st.selectbox(
                "Filtrar por método",
                ["Todos", "PIX", "Dinheiro", "Cartão Débito", "Cartão Crédito", "Transferência"],
                index=0
            )
        
        try:
            pagamentos = PagamentoController.search(
                apelido=apelido_filter if apelido_filter != "Todos" else None,
                status=status_filter if status_filter != "Todos" else None,
                metodo=metodo_filter if metodo_filter != "Todos" else None,
                data_inicio=data_inicio,
                data_fim=data_fim
            )
            
            if pagamentos:
                # Transforma em DataFrame para melhor visualização
                df = pd.DataFrame(pagamentos)
                df['data'] = pd.to_datetime(df['data']).dt.strftime('%d/%m/%Y %H:%M')
                
                # Formatação condicional
                def color_status(status):
                    if status == 'Confirmado':
                        return 'color: green; font-weight: bold'
                    elif status == 'Cancelado':
                        return 'color: red'
                    else:
                        return 'color: orange'
                
                styled_df = df.style.applymap(
                    lambda x: color_status(x) if x in ['Confirmado', 'Pendente', 'Cancelado'] else '',
                    subset=['status']
                )
                
                st.dataframe(
                    styled_df,
                    column_config={
                        "numero": "Número",
                        "apelido": "Apostador",
                        "valor": st.column_config.NumberColumn("Valor", format="R$ %.2f"),
                        "metodo": "Método",
                        "status": "Status",
                        "data": "Data",
                        "observacoes": "Observações"
                    },
                    use_container_width=True,
                    hide_index=True
                )
                
                # Opções de exportação
                csv = df.to_csv(index=False, sep=';').encode('utf-8')
                st.download_button(
                    label="📥 Exportar para CSV",
                    data=csv,
                    file_name=f"pagamentos_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
                
                # Resumo financeiro
                st.markdown("### Resumo Financeiro")
                total = df['valor'].sum()
                confirmados = df[df['status'] == 'Confirmado']['valor'].sum()
                pendentes = df[df['status'] == 'Pendente']['valor'].sum()
                
                col1, col2, col3 = st.columns(3)
                col1.metric("Total Geral", f"R$ {total:,.2f}")
                col2.metric("Confirmados", f"R$ {confirmados:,.2f}")
                col3.metric("Pendentes", f"R$ {pendentes:,.2f}")
                
            else:
                st.info("Nenhum pagamento encontrado com os filtros selecionados.")
                
        except Exception as e:
            st.error(f"Erro ao buscar pagamentos: {str(e)}")

    @staticmethod
    def _show_reports():
        """Exibe relatórios financeiros"""
        if not st.session_state.get('user', {}).get('perfil') in ['ADMINISTRADOR', 'DESENVOLVEDOR']:
            st.error("Acesso restrito a administradores!")
            return
        
        st.subheader("Relatórios Financeiros")
        
        tab1, tab2, tab3 = st.tabs(["Consolidado", "Por Método", "Por Apostador"])
        
        with tab1:
            PagamentoView._show_consolidated_report()
        with tab2:
            PagamentoView._show_method_report()
        with tab3:
            PagamentoView._show_user_report()

    @staticmethod
    def _show_consolidated_report():
        """Relatório consolidado de pagamentos"""
        try:
            col1, col2 = st.columns(2)
            ano = col1.selectbox(
                "Ano",
                options=range(datetime.now().year, datetime.now().year - 5, -1),
                index=0,
                key="report_ano"
            )
            mes = col2.selectbox(
                "Mês",
                options=range(1, 13),
                format_func=lambda x: datetime(1900, x, 1).strftime('%B'),
                index=datetime.now().month - 1,
                key="report_mes"
            )
            
            report = PagamentoController.get_consolidated_report(ano, mes)
            
            if report:
                df = pd.DataFrame(report)
                df['dia'] = df['dia'].astype(str)
                
                st.markdown(f"### Total do Mês: R$ {df['valor'].sum():,.2f}")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.dataframe(
                        df,
                        column_config={
                            "dia": "Dia",
                            "quantidade": "Qtd Pagamentos",
                            "valor": st.column_config.NumberColumn("Valor Total", format="R$ %.2f")
                        },
                        use_container_width=True,
                        hide_index=True
                    )
                
                with col2:
                    st.bar_chart(df.set_index('dia')['valor'])
                
                # Exportação
                st.download_button(
                    label="📊 Exportar Relatório",
                    data=df.to_csv(index=False, sep=';').encode('utf-8'),
                    file_name=f"relatorio_consolidado_{ano}_{mes:02d}.csv",
                    mime="text/csv"
                )
            else:
                st.info("Nenhum dado disponível para o período selecionado.")
                
        except Exception as e:
            st.error(f"Erro ao gerar relatório: {str(e)}")

    @staticmethod
    def _show_method_report():
        """Relatório por método de pagamento"""
        try:
            col1, col2 = st.columns(2)
            ano = col1.selectbox(
                "Ano",
                options=range(datetime.now().year, datetime.now().year - 5, -1),
                index=0,
                key="method_ano"
            )
            mes = col2.selectbox(
                "Mês",
                options=range(1, 13),
                format_func=lambda x: datetime(1900, x, 1).strftime('%B'),
                index=datetime.now().month - 1,
                key="method_mes"
            )
            
            report = PagamentoController.get_method_report(ano, mes)
            
            if report:
                df = pd.DataFrame(report)
                
                st.markdown(f"### Total por Método: R$ {df['valor'].sum():,.2f}")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.dataframe(
                        df,
                        column_config={
                            "metodo": "Método",
                            "quantidade": "Qtd Pagamentos",
                            "valor": st.column_config.NumberColumn("Valor Total", format="R$ %.2f"),
                            "percentual": st.column_config.NumberColumn("Participação", format="%.1f%%")
                        },
                        use_container_width=True,
                        hide_index=True
                    )
                
                with col2:
                    st.bar_chart(df.set_index('metodo')['valor'])
                
                # Exportação
                st.download_button(
                    label="📊 Exportar Relatório",
                    data=df.to_csv(index=False, sep=';').encode('utf-8'),
                    file_name=f"relatorio_metodos_{ano}_{mes:02d}.csv",
                    mime="text/csv"
                )
            else:
                st.info("Nenhum dado disponível para o período selecionado.")
                
        except Exception as e:
            st.error(f"Erro ao gerar relatório: {str(e)}")

    @staticmethod
    def _show_user_report():
        """Relatório por apostador"""
        try:
            col1, col2 = st.columns(2)
            ano = col1.selectbox(
                "Ano",
                options=range(datetime.now().year, datetime.now().year - 5, -1),
                index=0,
                key="user_ano"
            )
            mes = col2.selectbox(
                "Mês",
                options=range(1, 13),
                format_func=lambda x: datetime(1900, x, 1).strftime('%B'),
                index=datetime.now().month - 1,
                key="user_mes"
            )
            
            report = PagamentoController.get_user_report(ano, mes)
            
            if report:
                df = pd.DataFrame(report)
                
                st.markdown(f"### Total por Apostador: R$ {df['valor'].sum():,.2f}")
                
                st.dataframe(
                    df,
                    column_config={
                        "apelido": "Apostador",
                        "quantidade": "Qtd Pagamentos",
                        "valor": st.column_config.NumberColumn("Valor Total", format="R$ %.2f"),
                        "percentual": st.column_config.NumberColumn("Participação", format="%.1f%%")
                    },
                    use_container_width=True,
                    hide_index=True
                )
                
                # Exportação
                st.download_button(
                    label="📊 Exportar Relatório",
                    data=df.to_csv(index=False, sep=';').encode('utf-8'),
                    file_name=f"relatorio_apostadores_{ano}_{mes:02d}.csv",
                    mime="text/csv"
                )
            else:
                st.info("Nenhum dado disponível para o período selecionado.")
                
        except Exception as e:
            st.error(f"Erro ao gerar relatório: {str(e)}")

    @staticmethod
    def show_payment_status_update(payment_id):
        """Componente para atualização de status de pagamento"""
        try:
            payment = PagamentoController.get_by_id(payment_id)
            if not payment:
                st.error("Pagamento não encontrado!")
                return False
            
            current_status = payment['status']
            new_status = st.selectbox(
                "Novo status",
                ["Confirmado", "Pendente", "Cancelado"],
                index=["Confirmado", "Pendente", "Cancelado"].index(current_status)
            ) 
                       
            submitted = st.form_submit_button("🔄 Atualizar Status")

            if submitted:
                if new_status != current_status:
                    PagamentoController.update_status(payment_id, new_status)
                    st.success(f"Status atualizado para '{new_status}'!")
                    return True
                else:
                    st.warning("O status não foi alterado.")
            return False
        except Exception as e:
            st.error(f"Erro ao atualizar status: {str(e)}")
            return False