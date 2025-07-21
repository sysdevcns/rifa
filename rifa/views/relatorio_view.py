
from services.whatsapp_service import WhatsAppService
from controllers.apostador_controller import ApostadorController
from controllers.evento_controller import EventoController
from controllers.jogo_controller import JogoController
from controllers.relatorio_controller import RelatorioController

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

class RelatorioView:
    @staticmethod
    def show_form():
        """Exibe o formulário principal de relatórios"""
        st.header("📊 Relatórios Consolidados")
        
        tab1, tab2, tab3 = st.tabs([
            "Resumo Geral", 
            "Por Evento", 
            "Por Apostador"
        ])
        
        with tab1:
            RelatorioView._show_general_report()
        with tab2:
            RelatorioView._show_event_report()
        with tab3:
            RelatorioView._show_user_report()

    @staticmethod
    def _show_general_report():
        """Exibe relatório geral consolidado"""
        with st.form(key="form_relatorio_geral"):
            st.subheader("📈 Filtros do Relatório")
            
            col1, col2 = st.columns(2)
            start_date = col1.date_input("Data Inicial", 
                                    value=datetime.now() - timedelta(days=30))
            end_date = col2.date_input("Data Final", 
                                    value=datetime.now())
            
            nivel_detalhe = st.selectbox(
                "Nível de Detalhe",
                ["Resumido", "Detalhado", "Completo"]
            )
            
            # BOTÃO CORRETO dentro do formulário
            submitted = st.form_submit_button("Gerar Relatório")
        
        # Processamento fora do formulário
        if submitted:
            try:
                with st.spinner("Processando dados..."):
                    report = RelatorioController.get_general_summary(
                        start_date=start_date,
                        end_date=end_date,
                        detail_level=nivel_detalhe
                    )
                
                st.success("Relatório gerado com sucesso!")
                
                # Exibição dos resultados
                st.metric("Total de Eventos", report['total_eventos'])
                st.metric("Arrecadação Total", f"R$ {report['total_pagamentos']:,.2f}")
                
                # Gráfico de eventos por status
                st.subheader("Eventos por Status")
                status_df = pd.DataFrame.from_dict(
                    report['eventos_por_status'], 
                    orient='index',
                    columns=['Quantidade']
                )
                st.bar_chart(status_df)
                
                # Botão de exportação FORA do formulário
                if st.button("📤 Exportar Relatório"):
                    # Lógica de exportação aqui
                    pass
                    
            except Exception as e:
                st.error(f"Erro ao gerar relatório: {str(e)}")
            

    @staticmethod
    def _show_event_report():
        """Exibe relatório por evento específico"""
        try:
            st.subheader("🎯 Relatório por Evento")
            
            # Obter lista de eventos
            eventos = RelatorioController.get_events_list()
            evento_selecionado = st.selectbox(
                "Selecione o evento:",
                options=[e['nome'] for e in eventos],
                format_func=lambda x: x
            )

            submitted = st.form_submit_button("Gerar Relatório do Evento")
            
            if submitted:
                with st.spinner("Gerando relatório..."):
                    report = RelatorioController.get_event_report(
                        evento_id=next(e['id'] for e in eventos if e['nome'] == evento_selecionado)
                    )
                
                # Exibir dados do evento
                st.write(f"**Evento:** {report['evento']['nome']}")
                st.write(f"**Tipo:** {report['evento']['tipo']}")
                st.write(f"**Data:** {report['evento']['data_divulgacao'].strftime('%d/%m/%Y')}")
                
                # Métricas
                col1, col2, col3 = st.columns(3)
                col1.metric("Jogos Disponíveis", report['jogos_disponiveis'])
                col2.metric("Jogos Reservados", report['jogos_reservados'])
                col3.metric("Jogos Vendidos", report['jogos_vendidos'])
                
                # Distribuição
                st.subheader("Distribuição de Jogos")
                dist_df = pd.DataFrame.from_dict(
                    report['distribuicao_jogos'],
                    orient='index',
                    columns=['Quantidade']
                )
                st.bar_chart(dist_df)
                
        except Exception as e:
            st.error(f"Erro ao gerar relatório: {str(e)}")

    @staticmethod
    def _show_user_report():
        """Exibe relatório por apostador"""
        try:
            st.subheader("👤 Relatório por Apostador")
            
            # Obter lista de apostadores
            apostadores = RelatorioController.get_users_list()
            apostador_selecionado = st.selectbox(
                "Selecione o apostador:",
                options=[a['apelido'] for a in apostadores],
                format_func=lambda x: x
            )

            submitted = st.form_submit_button("Gerar Relatório do Apostador")
            
            if submitted:
                with st.spinner("Gerando relatório..."):
                    report = RelatorioController.get_user_report(
                        apelido=apostador_selecionado
                    )
                
                # Exibir dados
                st.write(f"**Apostador:** {report['apostador']['apelido']}")
                st.write(f"**Total de Jogos:** {report['total_jogos']}")
                st.write(f"**Total Gasto:** R$ {report['total_gasto']:,.2f}")
                
                # Últimos jogos
                st.subheader("Últimos Jogos")
                st.dataframe(
                    pd.DataFrame(report['ultimos_jogos']),
                    hide_index=True,
                    use_container_width=True
                )
                
        except Exception as e:
            st.error(f"Erro ao gerar relatório: {str(e)}")


    @staticmethod
    def show_jogos_realizados(evento_id):
        evento = EventoController.get_by_id(evento_id)
        if not evento:
            st.error("Evento não encontrado")
            return

        st.header(f"JOGOS REALIZADOS - {evento['Nome']}")
        
        # Cabeçalho
        col1, col2 = st.columns([4, 1])
        col1.markdown(f"**LOTERIA**")
        col2.markdown(f"**Data:** {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        
        # Informações do evento
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        col1.markdown(f"**Evento:** {evento['Nome']}")
        col2.markdown(f"**Tipo:** {evento['Tipo']}")
        col3.markdown(f"**Data:** {evento['Divulgacao'].strftime('%d/%m/%Y')}")
        
        col1, col2 = st.columns(3)
        col1.markdown(f"**Prêmio:** R$ {evento['valor_premio']:,.2f}")
        col2.markdown(f"**Trave:** R$ {evento['valor_trave']:,.2f}")
        col3.markdown(f"**Ticket:** R$ {evento['valor_ticket']:,.2f}")
        
        # Legenda
        st.markdown("---")
        st.markdown("**Legenda:** 🟦 DISPONÍVEL | 🟨 RESERVADO | 🟥 VENDIDO | ✅ PREMIADO | 🎯 TRAVE")
        
        # Grid de números 10x100
        st.markdown("---")
        st.subheader("Números Sorteados")
        
        # Obter todos os jogos do evento
        jogos = JogoController.get_all_by_event(evento_id)
        
        # Criar grid
        for row in range(0, 100, 10):
            cols = st.columns(10)
            for i in range(10):
                num = row + i
                num_str = f"{num:03d}"
                jogo = next((j for j in jogos if j['numero'] == num_str), None)
                
                with cols[i]:
                    RelatorioView._render_cell_jogo(num_str, jogo, evento)
        
    
    @staticmethod
    def _render_cell_jogo(num_str, jogo, evento):
        status = jogo['status'] if jogo else 'DISPONIVEL'
        
        # Definir cores e ícones
        bg_color = {
            'DISPONIVEL': '#1E90FF',
            'RESERVADO': '#FFD700',
            'VENDIDO': '#FF4500'
        }.get(status, '#CCCCCC')
        
        text_color = '#000000' if status == 'RESERVADO' else '#FFFFFF'
        
        # Verificar se foi premiado ou trave (exemplo)
        premiado = num_str == evento.get('Resultado', '')
        trave = num_str == evento.get('Trave', '')
        
        # Construir conteúdo da célula
        content = f"""
        <div style='background-color:{bg_color}; color:{text_color}; 
                    border-radius:0.5rem; padding:0.2rem; text-align:center;
                    font-weight:bold; min-height:60px; display:flex; 
                    flex-direction:column; justify-content:space-between;'>
            <div style='font-size:0.8rem;'>
                {jogo['apelido'] if jogo and jogo['apelido'] else ''}
                {"✅" if premiado else "🎯" if trave else ""}
            </div>
            <div style='font-size:1.2rem;'>
                {num_str}
                {"P" if premiado else "T" if trave else ""}
            </div>
        </div>
        """
        
        st.markdown(content, unsafe_allow_html=True)
        
        # Adicionar funcionalidade de WhatsApp
        if jogo and jogo['apelido']:
            apostador = ApostadorController.get_by_apelido(jogo['apelido'])
            if apostador and apostador['DDD'] and apostador['Telefone']:        
                submitted = st.form_submit_button("📱", key=f"whatsapp_{num_str}")
                if submitted:                
                    whatsapp_url = WhatsAppService.get_whatsapp_link(
                        jogo['apelido'],
                        num_str,
                        evento['Nome'],
                        status
                    )
                    st.markdown(f"[Enviar mensagem]({whatsapp_url})", unsafe_allow_html=True)