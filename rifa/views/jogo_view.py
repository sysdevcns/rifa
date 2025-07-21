import streamlit as st
import pandas as pd
import time
from services.db_service import DatabaseService
from controllers.apostador_controller import ApostadorController
from controllers.evento_controller import EventoController
from controllers.jogo_controller import JogoController
from views.evento_view import EventoView

class JogoView:
    @staticmethod
    def show_form():
        """Exibe o formulário principal de jogos"""
        st.header("🎫 Controle de Jogos")
        
        # Verificar se usuário está logado
        user = st.session_state.get('user')
        if not user or not user.get('apelido'):
            st.error("Você precisa estar logado para acessar esta página!")
            return
            
        tab1, tab2 = st.tabs(["Selecionar Números", "Meus Jogos"])
        
        with tab1:
            JogoView._show_number_selection(user['apelido'])
        with tab2:
            JogoView._show_user_games(user['apelido'])


    @staticmethod
    def _show_update_form():
        """Formulário de atualização de jogos"""
        with st.form(key="form_atualizar_jogo", clear_on_submit=True):
            st.subheader("Atualizar Jogo")
            
            # 1. Seleção do evento
            evento_id = EventoView.show_evento_select("Selecione o evento:")
            if not evento_id:
                return
                
            # 2. Seleção do número
            numero = st.text_input("Número do Jogo (000-999)*", max_length=3)
            
            # 3. Novo status
            novo_status = st.selectbox(
                "Novo Status",
                ["DISPONIVEL", "RESERVADO", "VENDIDO"],
                index=0
            )
            
            # 4. Apostador (se for reserva/venda)
            apelido = None
            if novo_status in ["RESERVADO", "VENDIDO"]:
                apostadores = ApostadorController.get_all_active()
                apelido = st.selectbox(
                    "Apostador*",
                    options=[a['apelido'] for a in apostadores]
                )
            
            submitted = st.form_submit_button("Atualizar Status")
            
            if submitted:
                try:
                    if not numero:
                        st.error("Número do jogo é obrigatório!")
                        return
                        
                    if novo_status in ["RESERVADO", "VENDIDO"] and not apelido:
                        st.error("Apostador é obrigatório para este status!")
                        return
                    
                    # Lógica de atualização
                    JogoController.update_status(
                        evento_id=evento_id,
                        numero=numero.zfill(3),  # Garante 3 dígitos
                        status=novo_status,
                        apelido=apelido
                    )
                    
                    st.success(f"Jogo {numero} atualizado para {novo_status}!")
                    time.sleep(1)
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Erro ao atualizar jogo: {str(e)}")


    @staticmethod
    def _show_number_selection(user_apelido):
        """Interface para seleção de números"""
        try:
            evento_id = EventoController.get_active_event_id()
            if not evento_id:
                st.warning("Nenhum evento ativo disponível no momento!")
                return
            
            evento = EventoController.get_by_id(evento_id)
            st.subheader(f"Evento: {evento['nome']}")
            st.markdown("🟦 Disponível | 🟨 Reservado (por você) | 🟥 Vendido/Reservado por outros")
            
            # Grid 25x40 (1000 números)
            cols = st.columns(25)
            for i in range(1000):
                num_str = f"{i:03d}"
                with cols[i % 25]:
                    JogoView._render_number_cell(num_str, evento_id, user_apelido)
                
                # Nova linha a cada 25 números
                if (i + 1) % 25 == 0 and i < 999:
                    cols = st.columns(25)
                    
        except Exception as e:
            st.error(f"Erro ao carregar números: {str(e)}")


    @staticmethod
    def _show_user_games(user_apelido):
        """Mostra os jogos do usuário logado"""
        try:
            with st.form("form_jogos_selecionados"):
                st.subheader("Meus Jogos Reservados")
                
                # Obter eventos ativos primeiro
                eventos_ativos = EventoController.get_all(status='Ativo')
                if not eventos_ativos:
                    st.info("Nenhum evento ativo no momento")
                    return
                    
                # Obter jogos do usuário
                jogos = []
                for evento in eventos_ativos:
                    jogos_evento = JogoController.get_user_games(evento['id'], user_apelido)
                    for jogo in jogos_evento:
                        jogo['evento_nome'] = evento['nome']
                        jogos.append(jogo)
                
                if jogos:
                    df = pd.DataFrame(jogos)
                    st.dataframe(
                        df[['evento_nome', 'numero', 'status', 'data_reserva']],
                        column_config={
                            "evento_nome": "Evento",
                            "numero": "Número",
                            "status": "Status",
                            "data_reserva": "Data Reserva"
                        },
                        use_container_width=True,
                        hide_index=True
                    )
                    
                    # Opção para cancelar reservas
                    numeros = [f"{j['numero']} ({j['evento_nome']})" for j in jogos if j['status'] == 'RESERVADO']
                    if numeros:
                        selecao = st.selectbox(
                            "Selecione uma reserva para cancelar:",
                            options=numeros
                        )
                        
                        submitted = st.form_submit_button("Cancelar Reserva", type="primary")

                        if submitted:
                            numero = selecao.split()[0]
                            evento_nome = selecao.split('(')[1][:-1]
                            evento_id = next(e['id'] for e in eventos_ativos if e['nome'] == evento_nome)
                            
                            try:
                                JogoController.cancel_reservation(evento_id, numero)
                                st.success(f"Reserva do número {numero} cancelada!")
                                time.sleep(1)
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erro ao cancelar: {str(e)}")
                else:
                    st.info("Você não tem nenhum jogo reservado ou comprado")
                                    
        except Exception as e:
            st.error(f"Erro ao carregar seus jogos: {str(e)}")


    @staticmethod
    def get_reserved_by_user(apelido):
        """Obtém todos os jogos reservados por um usuário, com nome do evento"""
        conn = DatabaseService.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """SELECT j.id, j.numero, j.status, j.data_reserva, 
                       e.nome as evento_nome
                    FROM Jogos j
                    JOIN Eventos e ON j.evento_id = e.id
                    WHERE j.apelido = %s AND j.status = 'RESERVADO'
                    ORDER BY e.nome, j.numero""",
                    (apelido,)
                )
                columns = [desc[0] for desc in cur.description]
                return [dict(zip(columns, row)) for row in cur.fetchall()]
        finally:
            conn.close()


    @staticmethod
    def _render_number_cell(num_str, evento_id, user_apelido):
        """Renderiza uma célula de número individual"""
        try:
            jogo = JogoController.get_game_info(evento_id, num_str)
            status = jogo.get('status', 'DISPONIVEL')
            
            # Definir cores e interação
            if status == 'DISPONIVEL':
                bg_color = '#1E90FF'  # Azul
                text_color = '#FFFFFF'
                can_interact = True
            elif status == 'RESERVADO' and jogo.get('apelido') == user_apelido:
                bg_color = '#FFD700'  # Amarelo (seu)
                text_color = '#000000'
                can_interact = True
            else:
                bg_color = '#FF4500'  # Vermelho (outros/vendido)
                text_color = '#FFFFFF'
                can_interact = False
            
            if can_interact:

                submitted = st.form_submit_button(
                    num_str,
                    key=f"btn_{evento_id}_{num_str}",
                    help=f"Status: {status}",
                    type='primary' 
                    if status == 'DISPONIVEL' else 'secondary'
                   )
            
                if submitted:
                    try:
                        if status == 'DISPONIVEL':
                            JogoController.reserve_number(evento_id, num_str, user_apelido)
                            st.success(f"Número {num_str} reservado!")
                        else:
                            JogoController.cancel_reservation(evento_id, num_str)
                            st.success(f"Reserva do número {num_str} cancelada!")
                        time.sleep(1)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro: {str(e)}")
            else:
                st.markdown(
                    f"""<div style='background-color:{bg_color}; color:{text_color};
                              border-radius:0.25rem; padding:0.25rem; text-align:center;
                              font-weight:bold;' title='Número: {num_str}\nStatus: {status}'>
                        {num_str}
                    </div>""",
                    unsafe_allow_html=True
                )
                
        except Exception as e:
            st.error(f"Erro no número {num_str}: {str(e)}")


    @staticmethod
    def _render_number_grid(evento_id, page, numbers_per_page, user_apelido):
        """Renderiza a grade de números"""
        start_num = (page - 1) * numbers_per_page
        end_num = start_num + numbers_per_page
        
        # 25 colunas
        cols_per_row = 25
        rows_per_page = numbers_per_page // cols_per_row
        
        for row in range(rows_per_page):
            cols = st.columns(cols_per_row)
            for col in range(cols_per_row):
                num = start_num + (row * cols_per_row) + col
                if num >= end_num:
                    break
                
                num_str = f"{num:03d}"
                with cols[col]:
                    JogoView._render_number_cell(num_str, evento_id, user_apelido)
