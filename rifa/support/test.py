import streamlit as st

def show_advanced_watermark():
    st.markdown("""
    <style>
        .watermark {
            position: fixed;
            bottom: 10px;
            right: 10px;
            color: rgba(128, 128, 128, 0.3);
            font-size: 14px;
            font-family: 'Arial', sans-serif;
            transform: rotate(-15deg);
            z-index: 1000;
            pointer-events: none;
            user-select: none;
        }
    </style>
    <div class="watermark">by Sidney Moraes ®</div>
    """, unsafe_allow_html=True)



def verificar_senha():
    import hashlib

    # Substitua com os valores do seu banco de dados
    senha_testada = "senha123"  # A senha que você acredita ser a correta
    hash_armazenado = "55a5e9e78207b4df8699d60886fa070079463547b095d1a05bc719bb4e6cd251"  # Hash do banco

    # Gerar hash da senha testada
    hash_gerado = hashlib.sha256(senha_testada.encode()).hexdigest()

    print(f"Hash armazenado: {hash_armazenado}")
    print(f"Hash gerado:    {hash_gerado}")
    print(f"Corresponde?    {hash_armazenado == hash_gerado}")


show_advanced_watermark()