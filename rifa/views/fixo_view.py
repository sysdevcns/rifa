import streamlit as st
import pandas as pd
import time
from datetime import datetime
from controllers.apostador_controller import ApostadorController 
from controllers.evento_controller import EventoController
from controllers.fixo_controller import FixoController

class FixoView:
    @staticmethod
    def show_form():
        """Exibe o formulário principal de jogos fixos"""
        st.header("🎯 Jogos Fixos")
        
        opcao = st.radio(
            "Selecione a operação:",
            ("Cadastrar", "Consultar", "Atualizar", "Gerenciar"),
            horizontal=True,
            index=0
        )
        
        if opcao == "Cadastrar":
            FixoView._show_create_form()
        elif opcao == "Consultar":
            FixoView._show_search_form()
        elif opcao == "Atualizar":
            FixoView._show_update_form()
        elif opcao == "Gerenciar":
            FixoView._show_manage_form()


    @staticmethod
    def _show_create_form():
        """Formulário de cadastro de jogos fixos"""
        with st.form("form_cadastrar_fixo", clear_on_submit=True):  # Adicione clear_on_submit aqui
            st.subheader("Cadastrar Novo Jogo Fixo")
            
            # Selecionar apostador
            apostadores = ApostadorController.get_all_active()
            apelido = st.selectbox(
                "Apostador*",
                options=[a['apelido'] for a in apostadores],
                format_func=lambda x: f"{x} ({next(a['nome'] for a in apostadores if a['apelido'] == x)})"
            )
            
            # Selecionar números
            numeros = st.text_area(
                "Números* (separados por vírgula ou linha)",
                help="Digite os números de 0 a 999, separados por vírgula ou uma por linha"
            )
            
            # Informações adicionais
            col1, col2 = st.columns(2)
            grupo = col1.text_input("Grupo/Observação", max_chars=50)
            status = col2.selectbox("Status", ["Ativo", "Inativo"], index=0)
            
            if st.form_submit_button("Cadastrar Jogo Fixo"):
                try:
                    if not numeros or not apelido:
                        st.warning("Apostador e números são obrigatórios!")
                        return
                    
                    # Processa os números
                    numeros_list = FixoView._process_numbers(numeros)
                    if not numeros_list:
                        st.warning("Nenhum número válido encontrado!")
                        return
                    
                    # Cadastra cada número
                    resultados = []
                    for numero in numeros_list:
                        try:
                            fixo_id = FixoController.create(
                                apelido=apelido,
                                numero=numero,
                                grupo=grupo,
                                status=status
                            )
                            resultados.append(f"✅ {numero}: cadastrado (ID: {fixo_id})")
                        except Exception as e:
                            resultados.append(f"❌ {numero}: erro ({str(e)})")
                    
                    st.success("Processamento concluído:")
                    for resultado in resultados:
                        st.write(resultado)
                    
                    # Substituir st.experimental_rerun() por st.rerun()
                    time.sleep(2)  # Pequeno delay para o usuário ver a mensagem
                    st.rerun()  # Esta é a linha corrigida
                    
                except Exception as e:
                    st.error(f"Erro ao cadastrar jogos fixos: {str(e)}")



    @staticmethod
    def _show_search_form():
        """Formulário de consulta de jogos fixos"""
        st.subheader("Consultar Jogos Fixos")
        
        with st.expander("🔍 Filtros Avançados", expanded=False):
            col1, col2 = st.columns(2)
            apelido_filter = col1.selectbox(
                "Filtrar por apostador",
                ["Todos"] + [a['apelido'] for a in ApostadorController.get_all_active()],
                index=0
            )
            status_filter = col2.selectbox(
                "Filtrar por status",
                ["Todos", "Ativo", "Inativo"],
                index=0
            )
            
            col1, col2 = st.columns(2)
            grupo_filter = col1.text_input("Filtrar por grupo")
            numero_filter = col2.text_input("Filtrar por número")
        
        try:
            jogos = FixoController.search(
                apelido=apelido_filter if apelido_filter != "Todos" else None,
                status=status_filter if status_filter != "Todos" else None,
                grupo=grupo_filter if grupo_filter else None,
                numero=numero_filter if numero_filter else None
            )
            
            if jogos:
                # Transforma em DataFrame para melhor visualização
                df = pd.DataFrame(jogos)
                df['data_registro'] = pd.to_datetime(df['data_registro']).dt.strftime('%d/%m/%Y %H:%M')
                
                st.dataframe(
                    df[['id', 'apelido', 'numero', 'grupo', 'status', 'data_registro']],
                    column_config={
                        "id": "ID",
                        "apelido": "Apostador",
                        "numero": "Número",
                        "grupo": "Grupo",
                        "status": "Status",
                        "data_registro": "Data Registro"
                    },
                    use_container_width=True,
                    hide_index=True
                )
                
                # Opções de exportação
                csv = df.to_csv(index=False, sep=';').encode('utf-8')
                st.download_button(
                    label="📥 Exportar para CSV",
                    data=csv,
                    file_name=f"jogos_fixos_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
            else:
                st.info("Nenhum jogo fixo encontrado com os filtros selecionados.")
                
        except Exception as e:
            st.error(f"Erro ao buscar jogos fixos: {str(e)}")


    @staticmethod
    def _show_update_form():
        """Formulário de atualização de jogo fixo"""
        st.subheader("Atualizar Jogo Fixo")
        
        try:
            # Buscar todos os jogos fixos
            jogos = FixoController.search()
            
            if not jogos:
                st.warning("Nenhum jogo fixo cadastrado!")
                return
                
            # Criar opções para o selectbox
            jogo_options = {
                f"ID: {j['id']} - {j['apelido']} ({j['numero']})": j['id']
                for j in jogos
            }
            
            jogo_selecionado = st.selectbox(
                "Selecione o jogo para editar:",
                options=list(jogo_options.keys())
            )
            jogo_id = jogo_options[jogo_selecionado]
            
            # Carrega os dados do jogo selecionado
            jogo = FixoController.get_by_id(jogo_id)
            if not jogo:
                st.error("Jogo não encontrado!")
                return
            
            with st.form("form_atualizar_fixo"):
                # Selecionar apostador
                apostadores = ApostadorController.get_all_active()
                apelido = st.selectbox(
                    "Apostador*",
                    options=[a['apelido'] for a in apostadores],
                    index=[a['apelido'] for a in apostadores].index(jogo['apelido'])
                )
                
                # Número (não editável)
                st.text_input("Número", value=jogo['numero'], disabled=True)
                
                # Informações adicionais
                col1, col2 = st.columns(2)
                grupo = col1.text_input("Grupo/Observação", value=jogo.get('grupo', ''))
                status = col2.selectbox(
                    "Status",
                    ["Ativo", "Inativo"],
                    index=0 if jogo.get('status') == "Ativo" else 1
                )
                
                if st.form_submit_button("Atualizar Jogo"):
                    try:
                        # Corrigindo a chamada do método update
                        resultado = FixoController.update(
                            fixo_id=jogo_id,  # Adicionando o parâmetro fixo_id
                            apelido=apelido,
                            grupo=grupo,
                            status=status
                        )
                        
                        if resultado > 0:
                            st.success("Jogo fixo atualizado com sucesso!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.warning("Nenhum dado foi atualizado.")
                    except Exception as e:
                        st.error(f"Erro ao atualizar jogo: {str(e)}")
                        
        except Exception as e:
            st.error(f"Erro ao carregar jogos fixos: {str(e)}")



    @staticmethod
    def _show_manage_form():
        """Formulário para gerenciamento em lote"""
        st.subheader("Gerenciamento em Lote")
        
        tab1, tab2 = st.tabs(["Ativar/Desativar", "Aplicar a Evento"])
        
        with tab1:
            FixoView._show_batch_status_form()
        with tab2:
            FixoView._show_apply_to_event_form()


    @staticmethod
    def _show_apply_to_event_form():
        """Formulário para aplicar jogos fixos a eventos"""
        with st.form(key="form_aplicar_evento"):
            st.subheader("Aplicar Jogos Fixos a Evento")
            
            try:
                # Obter eventos ativos
                eventos = EventoController.get_active_events()
                if not eventos:
                    st.warning("Nenhum evento ativo disponível!")
                    return
                    
                # Seleção de evento
                evento_opcoes = {e['nome']: e['id'] for e in eventos}
                evento_selecionado = st.selectbox(
                    "Selecione o evento:",
                    options=list(evento_opcoes.keys())
                )
                evento_id = evento_opcoes[evento_selecionado]
                
                # Filtros
                col1, col2 = st.columns(2)
                with col1:
                    apostadores = ApostadorController.get_all_active()
                    apelido = st.selectbox(
                        "Filtrar por apostador:",
                        ["Todos"] + [a['apelido'] for a in apostadores]
                    )
                with col2:
                    grupo = st.text_input("Filtrar por grupo (opcional):")
                
                submitted = st.form_submit_button("Aplicar Jogos ao Evento")
                
                # Botão de envio
                if submitted:
                    try:
                        with st.spinner("Aplicando jogos..."):
                            result = FixoController.apply_to_event(
                                evento_id=evento_id,
                                apelido=apelido if apelido != "Todos" else None,
                                grupo=grupo if grupo else None
                            )
                        
                        st.success(f"""
                            Resultado:
                            ✅ {result['applied']} aplicados | 
                            ⏭️ {result['skipped']} já existiam | 
                            ❌ {result['failed']} falhas
                        """)
                        time.sleep(2)
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"Erro: {str(e)}")
            
            except Exception as e:
                st.error(f"Erro ao carregar dados: {str(e)}")


    @staticmethod
    def _show_batch_status_form():
        """Formulário para alterar status em lote"""
        with st.form("form_status_lote"):
            st.markdown("**Alterar status em lote**")
            
            # Filtros para seleção
            col1, col2 = st.columns(2)
            apelido_filter = col1.selectbox(
                "Apostador",
                ["Todos"] + [a['apelido'] for a in ApostadorController.get_all_active()],
                key="batch_apelido"
            )
            grupo_filter = col2.text_input("Grupo", key="batch_grupo")
            
            # Novo status
            novo_status = st.selectbox(
                "Novo status",
                ["Ativo", "Inativo"],
                index=0
            )
            
            submitted = st.form_submit_button("Aplicar Status em Lote")
            
            if submitted:
                try:
                    affected = FixoController.batch_update_status(
                        apelido=apelido_filter if apelido_filter != "Todos" else None,
                        grupo=grupo_filter if grupo_filter else None,
                        status=novo_status
                    )
                    st.success(f"Status de {affected} jogos atualizados para '{novo_status}'!")
                    time.sleep(1)  # Pequeno delay para o usuário ver a mensagem
                    st.rerun()  # Substituição do st.experimental_rerun()
                except Exception as e:
                    st.error(f"Erro ao atualizar status: {str(e)}")
                        
                    
    @staticmethod
    def _process_numbers(input_text):
        """Processa o texto de entrada para extrair números válidos"""
        numbers = []
        # Remove espaços e divide por vírgulas ou quebras de linha
        for part in input_text.replace('\n', ',').split(','):
            part = part.strip()
            if part:
                try:
                    num = int(part)
                    if 0 <= num <= 999:
                        numbers.append(f"{num:03d}")
                    else:
                        st.warning(f"Número {num} fora do intervalo (0-999), ignorado")
                except ValueError:
                    st.warning(f"Valor '{part}' não é um número válido, ignorado")
        return numbers