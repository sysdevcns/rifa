import os
from pathlib import Path

def get_py_files_content(base_path):
    """
    Captura o conteúdo de todos os arquivos .py nas pastas informadas
    Retorna um dicionário com a estrutura: {pasta: {arquivo: conteúdo}}
    """
    mvc_folders = ['services','models', 'views', 'controllers']
    all_content = {}
    
    for folder in mvc_folders:
        folder_path = Path(base_path) / folder
        folder_content = {}
        
        if folder_path.exists() and folder_path.is_dir():
            for py_file in folder_path.glob('*.py'):
                try:
                    with open(py_file, 'r', encoding='utf-8') as file:
                        folder_content[py_file.name] = file.read()
                except Exception as e:
                    folder_content[py_file.name] = f"Erro ao ler arquivo: {str(e)}"
        
        all_content[folder] = folder_content
    
    return all_content

def save_combined_content(content_dict, output_file='services\\xScript.txt'):
    """
    Salva o conteúdo combinado em um arquivo de texto
    """
    with open(output_file, 'w', encoding='utf-8') as out_file:
        for folder, files in content_dict.items():
            out_file.write(f"=== {folder.upper()} ===\n\n")
            for filename, content in files.items():
                out_file.write(f"--- {filename} ---\n")
                out_file.write(content)
                out_file.write("\n\n")
    
    print(f"Conteúdo salvo em {output_file}")

if __name__ == "__main__":
    # Altere para o caminho base do seu projeto MVC
    project_path = os.path.dirname(os.path.abspath(__file__))
    
    # Obtém todo o conteúdo
    mvc_content = get_py_files_content(project_path)
    
    # Salva em um arquivo combinado
    save_combined_content(mvc_content)
    
    # Opcional: imprimir no console
    for folder, files in mvc_content.items():
        print(f"\n# {folder.upper()} ({len(files)} arquivos)")
        for filename, content in files.items():
            print(f"\n## {filename}\n")
            print(content[:200] + "..." if len(content) > 200 else content)