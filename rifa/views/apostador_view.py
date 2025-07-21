import streamlit as st
import time
from services.auth_service import AuthService
from controllers.apostador_controller import ApostadorController

class ApostadorView:
    @staticmethod
    def show_form():
        if not AuthService.check_permission('ASSISTENTE'):
            st.error("Acesso não autorizado!")
            return

        opcao = st.radio("Operação:", ("Cadastrar", "Consultar", "Atualizar", "Desativar"), horizontal=True)
        
        if opcao == "Cadastrar":
            ApostadorView._show_create_form()
        elif opcao == "Consultar":
            ApostadorView._show_search_form()
        elif opcao == "Atualizar":
            ApostadorView._show_update_form()
        elif opcao == "Desativar":
            ApostadorView._show_deactivate_form()

   
    @staticmethod
    def _show_create_form():
        form = st.form(key="form_cadastrar_apostador", clear_on_submit=True)  # Novo parâmetro aqui
        with form:
            st.subheader("Cadastrar Novo Apostador")
            
            col1, col2 = st.columns(2)
            nome = col1.text_input("Nome Completo*", max_chars=100, key="nome")
            apelido = col2.text_input("Apelido*", max_chars=50, key="apelido")
            
            col1, col2 = st.columns(2)
            ddd = col1.text_input("DDD", max_chars=2, key="ddd")
            telefone = col2.text_input("Telefone", max_chars=15, key="telefone")
            
            email = st.text_input("E-mail", max_chars=100, key="email")
            endereco = st.text_area("Endereço", max_chars=200, key="endereco")
            
            submitted = form.form_submit_button("Cadastrar")
            
            if submitted:
                try:
                    if not nome or not apelido:
                        st.error("Nome e apelido são obrigatórios!")
                        st.stop()  # Impede a execução do resto do código
                    
                    # Cria um container para mensagens
                    message_container = st.empty()
                    
                    ApostadorController.create(
                        nome=nome,
                        apelido=apelido,
                        ddd=ddd if ddd else None,
                        telefone=telefone if telefone else None,
                        email=email if email else None,
                        endereco=endereco if endereco else None
                    )
                    
                    # Exibe mensagem de sucesso
                    message_container.success("Apostador cadastrado com sucesso!")
                    
                    # Força atualização da página após 2 segundos
                    time.sleep(2)
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Erro ao cadastrar apostador: {str(e)}")
    

    @staticmethod
    def _show_search_form():
        with st.form("form_consultar_apostador"):
            st.subheader("Consultar Apostadores")
            
            col1, col2 = st.columns(2)
            nome_filter = col1.text_input("Filtrar por nome")
            apelido_filter = col2.text_input("Filtrar por apelido")
            
            status_filter = st.selectbox("Status", ["Todos", "Ativo", "Inativo"])
            
            if st.form_submit_button("Buscar"):
                try:
                    apostadores = ApostadorController.search(
                        nome=nome_filter if nome_filter else None,
                        apelido=apelido_filter if apelido_filter else None,
                        status=status_filter if status_filter != "Todos" else None
                    )
                    
                    if apostadores:
                        st.dataframe(
                            apostadores,
                            column_config={
                                "Nome": "Nome",
                                "Apelido": "Apelido",
                                "Telefone": "Telefone",
                                "Status": "Status"
                            },
                            use_container_width=True,
                            hide_index=True
                        )
                    else:
                        st.info("Nenhum apostador encontrado com os filtros selecionados.")
                except Exception as e:
                    st.error(f"Erro ao buscar apostadores: {str(e)}")


    @staticmethod
    def _show_update_form():
        try:
            st.subheader("Atualizar Apostador")
            
            # Buscar apostadores ativos (agora em minúsculo)
            apostadores = ApostadorController.search(status='Ativo')
            if not apostadores:
                st.warning("Nenhum apostador ativo encontrado!")
                return
                
            # Criar opções para o selectbox
            opcoes = {f"{a['apelido']} ({a['nome']})": a for a in apostadores}
            
            selecao = st.selectbox(
                "Selecione o apostador para editar:",
                options=list(opcoes.keys())
            )
            
            apostador = opcoes[selecao]
            
            with st.form("form_atualizar_apostador"):
                col1, col2 = st.columns(2)
                nome = col1.text_input("Nome Completo*", 
                                    value=apostador['nome'])
                apelido = col2.text_input("Apelido*", 
                                        value=apostador['apelido'],
                                        disabled=True)
                
                col1, col2 = st.columns(2)
                ddd = col1.text_input("DDD", 
                                    value=apostador.get('ddd', ''))
                telefone = col2.text_input("Telefone", 
                                        value=apostador.get('telefone', ''))
                
                email = st.text_input("E-mail", 
                                    value=apostador.get('email', ''))
                endereco = st.text_area("Endereço", 
                                    value=apostador.get('endereco', ''))
                
                if st.form_submit_button("Atualizar"):
                    try:
                        if not nome:
                            st.error("Nome é obrigatório!")
                            return
                        
                        ApostadorController.update(
                            apelido=apostador['apelido'],
                            nome=nome,
                            ddd=ddd if ddd else None,
                            telefone=telefone if telefone else None,
                            email=email if email else None,
                            endereco=endereco if endereco else None
                        )
                        st.success("Apostador atualizado com sucesso!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao atualizar: {str(e)}")
                        
        except Exception as e:
            st.error(f"Erro ao carregar formulário: {str(e)}")
      

    @staticmethod
    def _show_deactivate_form():
        try:
            with st.form(key="show_deactivate_form"):
                st.subheader("Desativar Apostador")
            
                # Buscar apenas apostadores ativos
                apostadores = ApostadorController.search(status='Ativo')
                if not apostadores:
                    st.warning("Nenhum apostador ativo disponível!")
                    return
                    
                # Criar opções para o selectbox no formato "Apelido (Nome)"
                opcoes = {f"{a['apelido']} ({a['nome']})": a['apelido'] for a in apostadores}
                
                selecao = st.selectbox(
                    "Selecione o apostador para desativar:",
                    options=list(opcoes.keys())
                )
                
                # Obter o apelido real sem o nome entre parênteses
                apelido_desativar = opcoes[selecao]
                
                submitted = st.form_submit_button("Confirmar Desativação", type="primary")
                
                if submitted:
                    try:
                        resultado = ApostadorController.deactivate(apelido_desativar)
                        if resultado > 0:
                            st.success(f"Apostador {apelido_desativar} desativado com sucesso!")
                            st.rerun()
                        else:
                            st.error("Nenhum apostador foi desativado. Verifique se o apelido existe.")
                    except Exception as e:
                        st.error(f"Erro ao desativar apostador: {str(e)}")
                    
        except Exception as e:
            st.error(f"Erro ao carregar formulário: {str(e)}")