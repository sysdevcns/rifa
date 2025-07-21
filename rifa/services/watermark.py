import streamlit as st

def show():
    """Exibe marca d'água em todas as páginas"""
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    <style>
        .watermark {
            position: fixed;
            bottom: 10px;
            right: 10px;
            color: rgba(128, 128, 128, 0.5);
            font-size: 12px;
            z-index: 1000;
        }
    </style>
    <div class="watermark">by Sidney Moraes ®</div>
    """, unsafe_allow_html=True)