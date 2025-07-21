import subprocess
import sys
import os
from pathlib import Path

pasta = 'rifa'
aplicacao = 'app'

def run_streamlit_app():
    # Define o caminho para o arquivo app.py
    app_path = Path(f"{pasta}/{aplicacao}.py")
    app_path = Path(f"{aplicacao}.py")
    
    # Verifica se o arquivo existe
    if not app_path.exists():
        print(f"Erro: O arquivo {app_path} não foi encontrado!")
        print("Certifique-se que:")
        print(f"1. A pasta {pasta} existe no diretório atual")
        print(f"2. O arquivo '{aplicacao}.py' está dentro da pasta {pasta}")
        return
    
    # Comando para executar o Streamlit
    command = ["streamlit", "run", str(app_path)]
    
    try:
        print(f"Iniciando aplicação Streamlit: {' '.join(command)}")
        print("Pressione Ctrl+C para encerrar o servidor")
        
        # Executa o comando
        subprocess.run(command, check=True)
        
    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar o Streamlit: {e}")
    except KeyboardInterrupt:
        print("\nServidor Streamlit encerrado pelo usuário")
    except Exception as e:
        print(f"Erro inesperado: {e}")

if __name__ == "__main__":
    # Verifica se o Streamlit está instalado
    try:
        import streamlit
    except ImportError:
        print("Streamlit não está instalado. Instalando agora...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "streamlit"], check=True)
            print("Streamlit instalado com sucesso!")
        except subprocess.CalledProcessError:
            print("Erro ao instalar o Streamlit. Por favor instale manualmente com:")
            print("pip install streamlit")
            sys.exit(1)
    
    # Executa a aplicação
    run_streamlit_app()