import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from controllers.bilhete_controller import BilheteController

class BilheteView:
    @staticmethod
    def show_form():
        """Exibe o formulário principal de bilhetes"""
        st.header("🎟️ Gerenciamento de Bilhetes")
        
        tab1, tab2, tab3 = st.tabs(["Cadastrar Bilhetes", "Consultar Bilhetes", "Relatório de Bilhetes"])
        
        with tab1:
            BilheteView._show_create_form()
        with tab2:
            BilheteView._show_search_form()
        with tab3:
            BilheteView._show_report()


    @staticmethod
    def _show_report():
        """Exibe o relatório de bilhetes"""
        try:
            st.subheader("Relatório de Bilhetes por Tipo")
            
            stats = BilheteController.get_stats_by_type()
            
            if not stats['detalhes']:
                st.warning("Nenhum dado disponível para gerar o relatório")
                return
            
            # Criar DataFrame com as colunas corretas
            df = pd.DataFrame(stats['detalhes'])
            
            # Verificar se as colunas esperadas existem
            required_columns = ['tipo', 'quantidade', 'percentual']
            if not all(col in df.columns for col in required_columns):
                missing = [col for col in required_columns if col not in df.columns]
                raise ValueError(f"Colunas faltando: {', '.join(missing)}")
            
            # Exibir métricas
            col1, col2, col3 = st.columns(3)
            col1.metric("Total de Bilhetes", stats['total'])
            col2.metric("Tipos Diferentes", len(stats['por_tipo']))
            col3.metric("Mais Comum", f"{max(stats['por_tipo'].items(), key=lambda x: x[1])[0]}")
            
            # Exibir tabela
            st.dataframe(
                df,
                column_config={
                    "tipo": "Tipo",
                    "quantidade": st.column_config.NumberColumn("Quantidade", format="%d"),
                    "percentual": st.column_config.NumberColumn("Percentual", format="%.2f%%")
                },
                hide_index=True,
                use_container_width=True
            )
            
            # Gráfico de pizza
            fig = px.pie(df, names='tipo', values='quantidade', title='Distribuição por Tipo')
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            st.error(f"Erro ao gerar relatório: {str(e)}")


    @staticmethod
    def _show_create_form():
        """Formulário de criação de bilhetes"""
        with st.form("form_cadastrar_bilhete"):
            st.subheader("Cadastrar Novo Bilhete")
            
            col1, col2 = st.columns(2)
            numero = col1.text_input("Número do Bilhete*", max_chars=20)
            tipo = col2.selectbox("Tipo", ["Físico", "Digital"], index=0)
            
            col1, col2 = st.columns(2)
            lote = col1.text_input("Lote/Sequência", max_chars=10)
            status = col2.selectbox("Status", ["Disponível", "Reservado", "Vendido", "Cancelado"], index=0)
            
            observacoes = st.text_area("Observações")
            
            if st.form_submit_button("Cadastrar Bilhete"):
                try:
                    if not numero:
                        st.warning("Número do bilhete é obrigatório!")
                        return
                    
                    bilhete_id = BilheteController.create(
                        numero=numero,
                        tipo=tipo,
                        lote=lote,
                        status=status,
                        observacoes=observacoes
                    )
                    st.success(f"Bilhete {numero} cadastrado com sucesso! ID: {bilhete_id}")
                except Exception as e:
                    st.error(f"Erro ao cadastrar bilhete: {str(e)}")

    @staticmethod
    def _show_search_form():
        """Formulário de consulta de bilhetes"""
        # Primeiro criamos o formulário de filtros
        with st.form(key="form_filtrar_bilhetes"):
            st.subheader("Filtrar Bilhetes")
            
            col1, col2, col3 = st.columns(3)
            numero_filter = col1.text_input("Número do Bilhete")
            tipo_filter = col2.selectbox("Tipo", ["Todos"] + ["Físico", "Digital"])
            status_filter = col3.selectbox("Status", ["Todos"] + ["Disponível", "Reservado", "Vendido"])
            
            col1, col2 = st.columns(2)
            lote_filter = col1.text_input("Filtrar por Lote")
            date_filter = col2.date_input("Filtrar por Data")
            
            # Botão de submit para aplicar filtros
            submitted = st.form_submit_button("Aplicar Filtros")
        
        # A lista de resultados e o download ficam FORA do formulário
        if submitted or 'bilhetes_filtrados' in st.session_state:
            try:
                # Busca os bilhetes com os filtros aplicados
                bilhetes = BilheteController.search(
                    numero=numero_filter if numero_filter else None,
                    tipo=tipo_filter if tipo_filter != "Todos" else None,
                    status=status_filter if status_filter != "Todos" else None,
                    lote=lote_filter if lote_filter else None,
                    data_inicio=date_filter if date_filter else None
                )
                
                if bilhetes:
                    # Armazena na sessão para o download
                    st.session_state.bilhetes_filtrados = bilhetes
                    
                    # Exibe a tabela
                    df = pd.DataFrame(bilhetes)
                    st.dataframe(
                        df,
                        column_config={
                            "numero": "Número",
                            "tipo": "Tipo",
                            "status": "Status",
                            "lote": "Lote",
                            "data_cadastro": "Data Cadastro"
                        },
                        use_container_width=True,
                        hide_index=True
                    )
                    
                    # Botão de download FORA do formulário
                    if st.button("📥 Exportar para CSV"):
                        csv = df.to_csv(index=False, sep=';').encode('utf-8')
                        st.download_button(
                            label="Download CSV",
                            data=csv,
                            file_name=f"bilhetes_{datetime.now().strftime('%Y%m%d')}.csv",
                            mime="text/csv"
                        )
                else:
                    st.info("Nenhum bilhete encontrado com os filtros selecionados.")
                    
            except Exception as e:
                st.error(f"Erro ao buscar bilhetes: {str(e)}")
        

    @staticmethod
    def show_bilhete_select(label="Selecione um bilhete:", filters=None):
        """Componente para seleção de bilhete (reutilizável)"""
        try:
            bilhetes = BilheteController.get_available(filters)
            
            if not bilhetes:
                st.warning("Nenhum bilhete disponível encontrado!")
                return None
                
            options = {f"{b['numero']} ({b['tipo']})": b['id'] for b in bilhetes}
            selected = st.selectbox(label, options.keys())
            return options[selected]
        except Exception as e:
            st.error(f"Erro ao carregar bilhetes: {str(e)}")
            return None