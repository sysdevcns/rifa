import hashlib
import streamlit as st
from services.db_service import DatabaseService

class AuthService:
    @staticmethod
    def make_hash(password):
        return hashlib.sha256(password.encode()).hexdigest()

    @staticmethod
    def authenticate(username, password):
        conn = DatabaseService.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """SELECT id, username, password, perfil, apelido 
                    FROM Usuarios 
                    WHERE username = %s AND ativo = TRUE""",
                    (username,)
                )
                user = cur.fetchone()
                if user and user[2] == AuthService.make_hash(password):
                    return {
                        'id': user[0],
                        'username': user[1],
                        'perfil': user[3],
                        'apelido': user[4]
                    }
                return None
        except Exception as e:
            st.error(f"Erro de autenticação: {str(e)}")
            return None
        finally:
            conn.close()

    @staticmethod
    def check_permission(required_perfil):
        user = st.session_state.get('user')
        if not user:
            return False
        
        hierarchy = {
            'DESENVOLVEDOR': 4,
            'ADMINISTRADOR': 3,
            'ASSISTENTE': 2,
            'APOSTADOR': 1
        }
        
        return hierarchy[user['perfil']] >= hierarchy[required_perfil]

    @staticmethod
    def show_login_form():
        with st.form("login_form"):
            st.subheader("Acesso ao Sistema")
            username = st.text_input("Usuário", key="login_username")
            password = st.text_input("Senha", type="password", key="login_password")
            
            if st.form_submit_button("Entrar", type="primary"):
                user = AuthService.authenticate(username, password)
                if user:
                    st.session_state.user = user
                    st.session_state.logged_in = True
                    st.rerun()  # Força a atualização da página
                else:
                    st.error("Usuário ou senha inválidos")
                    st.session_state.logged_in = False