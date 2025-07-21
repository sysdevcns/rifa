import streamlit as st

from services.auth_service import AuthService
from services.db_service import DatabaseService
from services.watermark import show as show_watermark
from views.apostador_view import ApostadorView
from views.bilhete_view import BilheteView
from views.evento_view import EventoView
from views.fixo_view import FixoView
from views.jogo_view import JogoView
from views.pagamento_view import PagamentoView
from views.relatorio_view import RelatorioView

class App:
    def __init__(self):
        self._init_session()
        self._init_db()
        show_watermark()

    def _init_session(self):
        if 'user' not in st.session_state:
            st.session_state.user = None
        if 'logged_in' not in st.session_state:
            st.session_state.logged_in = False


    def _init_db(self):
        DatabaseService.create_tables()
        

    def show_login(self):
        # Configura a página para esconder o menu lateral durante o login
        st.set_page_config(
            page_title="Login",
            layout="centered",
            initial_sidebar_state="collapsed"
        )
        
        # Esconde o menu lateral usando CSS
        hide_menu_style = """
        <style>
            #MainMenu {visibility: hidden;}
            header {visibility: hidden;}
            footer {visibility: hidden;}
        </style>
        """
        st.markdown(hide_menu_style, unsafe_allow_html=True)
    
        AuthService.show_login_form()
        

    def show_authorized_content(self):
        # Restaura a configuração padrão da página para conteúdo autorizado
        st.set_page_config(
            page_title="RIFA",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        user = st.session_state.user
        
        st.sidebar.title(f"RIFA | {user['perfil']}")
        st.sidebar.markdown(f"Usuário: {user['username']}")
        
        # Menu baseado no perfil
        menu_items = []
        
        # Apostadores - disponível para todos os perfis
        menu_items.append(("Apostadores", ApostadorView.show_form))
        
        # Jogos - disponível para todos os perfis
        menu_items.append(("Jogos", JogoView.show_form))
        
        if user['perfil'] in ['ASSISTENTE', 'ADMINISTRADOR', 'DESENVOLVEDOR']:
            menu_items.append(("Eventos", EventoView.show_form))
            menu_items.append(("Pagamentos", PagamentoView.show_form))
        
        if user['perfil'] in ['ADMINISTRADOR', 'DESENVOLVEDOR']:
            menu_items.append(("Jogos Fixos", FixoView.show_form))
            menu_items.append(("Bilhetes", BilheteView.show_form))
        
        if user['perfil'] == 'DESENVOLVEDOR':
            menu_items.append(("Relatórios", RelatorioView.show_form))
        
        # Adicionar logout
        if st.sidebar.button("Sair"):
            st.session_state.user = None
            st.session_state.logged_in = False
            st.rerun()
        
        menu = st.sidebar.radio("Menu", [item[0] for item in menu_items])
        
        for item in menu_items:
            if menu == item[0]:
                item[1]()
                break
            

    def run(self):
        if not st.session_state.logged_in:
            self.show_login()
        else:
            self.show_authorized_content()
            

if __name__ == "__main__":
    app = App()
    app.run()