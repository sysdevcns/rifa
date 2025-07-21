import streamlit as st
import time
from datetime import datetime
from controllers.evento_controller import EventoController

class EventoView:
    @staticmethod
    def show_form():
        """Exibe o formulário principal de eventos"""
        st.header("🗓️ Gerenciamento de Eventos")
        
        opcao = st.radio(
            "Selecione a operação:",
            ("Cadastrar", "Consultar", "Atualizar", "Alterar Status"),
            horizontal=True
        )

        if opcao == "Cadastrar":
            EventoView._show_create_form()
        elif opcao == "Consultar":
            EventoView._show_search_form()
        elif opcao == "Atualizar":
            EventoView._show_update_form()
        elif opcao == "Alterar Status":
            EventoView._show_status_form()

    @staticmethod
    def _show_create_form():
        """Formulário de criação de evento"""
        with st.form("form_cadastrar_evento", clear_on_submit=True):
            st.subheader("Cadastrar Novo Evento")
            
            col1, col2 = st.columns(2)
            nome = col1.text_input("Nome do Evento*", key="evento_nome")
            tipo = col2.selectbox("Tipo*", ["Esportivo", "Cultural", "Sorteio", "Outro"], key="evento_tipo")

            divulgacao = st.date_input("Data de Divulgação*", min_value=datetime.today(), key="evento_divulgacao")
            
            col1, col2, col3 = st.columns(3)
            ticket = col1.number_input("Valor do Ticket (R$)*", min_value=0.0, format="%.2f", key="evento_ticket")
            premio = col2.number_input("Prêmio (R$)*", min_value=0.0, format="%.2f", key="evento_premio")
            trave = col3.number_input("Trave (R$)*", min_value=0.0, format="%.2f", key="evento_trave")

            descricao = st.text_area("Descrição", key="evento_descricao")
            concurso = st.text_input("Concurso", key="evento_concurso")
            
            submitted = st.form_submit_button("Cadastrar")
            
            if submitted:
                try:
                    if not nome or not tipo or not divulgacao or ticket <= 0 or premio <= 0:
                        st.error("Campos marcados com * são obrigatórios!")
                        return
                    
                    evento_id = EventoController.create(
                        nome=nome,
                        tipo=tipo,
                        divulgacao=divulgacao,
                        ticket=ticket,
                        premio=premio,
                        trave=trave,
                        descricao=descricao if descricao else None,
                        concurso=concurso if concurso else None
                    )
                    st.success(f"Evento cadastrado com sucesso! ID: {evento_id}")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao criar evento: {str(e)}")

    @staticmethod
    def _show_search_form():
        """Formulário de consulta de eventos"""
        st.subheader("Consultar Eventos")
        
        filtro = st.text_input("Filtrar por nome ou tipo:")
        
        try:
            eventos = EventoController.get_all(filtro if filtro else None)
            
            if eventos:
                st.dataframe(
                    eventos,
                    column_config={
                        "divulgacao": "Data Divulgação",
                        "ticket": st.column_config.NumberColumn("Ticket", format="R$ %.2f"),
                        "premio": st.column_config.NumberColumn("Prêmio", format="R$ %.2f"),
                        "trave": st.column_config.NumberColumn("Trave", format="R$ %.2f")
                    },
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("Nenhum evento encontrado.")
        except Exception as e:
            st.error(f"Erro ao buscar eventos: {str(e)}")
            
    @staticmethod
    def _show_update_form():
        """Formulário de atualização de eventos"""
        eventos = EventoController.get_all()
        if not eventos:
            st.warning("Nenhum evento cadastrado!")
            return

        # Seleção do evento
        evento_opcoes = {f"{e['nome']} (ID: {e['id']})": e['id'] for e in eventos}
        selected = st.selectbox("Selecione o evento para editar:", options=list(evento_opcoes.keys()))
        
        with st.form(key="form_atualizar_evento", clear_on_submit=False):
            evento = EventoController.get_by_id(evento_opcoes[selected])
            
            # Campos do formulário
            nome = st.text_input("Nome do Evento*", value=evento['nome'])
            tipo = st.selectbox("Tipo*", 
                            options=["Esportivo", "Cultural", "Sorteio", "Outro"],
                            index=["Esportivo", "Cultural", "Sorteio", "Outro"].index(evento['tipo']))
            
            divulgacao = st.date_input("Data de Divulgação*", 
                                    value=evento['data_divulgacao'] if 'data_divulgacao' in evento else datetime.now())
            
            col1, col2, col3 = st.columns(3)
            ticket = col1.number_input("Valor do Ticket (R$)*", 
                                    value=float(evento['valor_ticket']), 
                                    min_value=0.0, 
                                    format="%.2f")
            premio = col2.number_input("Valor do Prêmio (R$)*", 
                                    value=float(evento['valor_premio']), 
                                    min_value=0.0, 
                                    format="%.2f")
            trave = col3.number_input("Valor da Trave (R$)*", 
                                    value=float(evento.get('valor_trave', 0)), 
                                    min_value=0.0, 
                                    format="%.2f")
            
            descricao = st.text_area("Descrição", value=evento.get('descricao', ''))
            concurso = st.text_input("Concurso", value=evento.get('concurso', ''))
            
            submitted = st.form_submit_button("Atualizar Evento")
            
            if submitted:
                try:
                    if not nome or not divulgacao or ticket <= 0 or premio <= 0 or trave <= 0:
                        st.error("Preencha todos os campos obrigatórios!")
                    else:
                        EventoController.update(
                            evento_id=evento['id'],
                            nome=nome,
                            tipo=tipo,
                            divulgacao=divulgacao,
                            ticket=ticket,
                            premio=premio,
                            trave=trave,
                            descricao=descricao if descricao else None,
                            concurso=concurso if concurso else None
                        )
                        st.success("Evento atualizado com sucesso!")
                        time.sleep(1)
                        st.rerun()
                except Exception as e:
                    st.error(f"Erro ao atualizar evento: {str(e)}")


    @staticmethod
    def _show_status_form():
        """Formulário para alterar status do evento"""
        try:
            eventos = EventoController.get_all()
            
            if not eventos:
                st.warning("Nenhum evento cadastrado!")
                return
                
            evento_options = {f"{e['nome']} (Status: {e['status']})": e['id'] for e in eventos}
            evento_selecionado = st.selectbox("Selecione o evento:", list(evento_options.keys()))
            evento_id = evento_options[evento_selecionado]
            
            evento = EventoController.get_by_id(evento_id)
            
            with st.form("form_alterar_evento"):         
                if evento:
                    novo_status = st.selectbox(
                        "Novo status",
                        ["Ativo", "Cancelado", "Concluído"],
                        index=["Ativo", "Cancelado", "Concluído"].index(evento['status'])
                    )
                    
                    submitted = st.form_submit_button("Alterar Status")
                    
                    if submitted:
                        try:
                            EventoController.update_status(evento_id, novo_status)
                            st.success(f"Status atualizado para '{novo_status}'!")
                        except Exception as e:
                            st.error(f"Erro ao atualizar status: {str(e)}")
                else:
                    st.error("Evento não encontrado!")
        except Exception as e:
            st.error(f"Erro ao carregar eventos: {str(e)}")

@staticmethod
def show_evento_select(label="Selecione o evento:"):
    """Componente para selecionar evento (usado em outros formulários)"""
    try:
        eventos = EventoController.get_active_events()
        
        if not eventos:
            st.warning("Nenhum evento ativo disponível!")
            return None
            
        evento_options = {
                            f"{e['nome']} (ID: {e['id']}) - {e['data_divulgacao'].strftime('%d/%m/%Y')}": e['id'] 
                            for e in eventos
                         }
 
        evento_selecionado = st.selectbox(label, list(evento_options.keys()))
        return evento_options[evento_selecionado]
    except Exception as e:
        st.error(f"Erro ao carregar eventos: {str(e)}")
        return None