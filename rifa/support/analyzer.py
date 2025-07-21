import os
import re
from collections import defaultdict
import subprocess

def find_py_files(directory):
    """Encontra todos os arquivos .py no diretório especificado."""
    py_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                py_files.append(os.path.join(root, file))
    return py_files

def extract_imports(file_path):
    """Extrai os imports de um arquivo Python."""
    imports = set()
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Padrão para imports regulares
    patterns = [
        r'^\s*import\s+([a-zA-Z0-9_., ]+)',
        r'^\s*from\s+([a-zA-Z0-9_.]+)\s+import\s+',
    ]
    
    for line in content.split('\n'):
        for pattern in patterns:
            matches = re.findall(pattern, line)
            if matches:
                for match in matches:
                    for imp in match.split(','):
                        imp = imp.strip().split()[0]  # Remove 'as' aliases
                        imp = imp.split('.')[0]  # Pega o módulo principal
                        if imp and not imp.startswith('.'):  # Ignora relativos
                            imports.add(imp)
    return imports

def get_installed_version(package):
    """Tenta obter a versão instalada de um pacote usando pip."""
    try:
        result = subprocess.run(['pip', 'show', package], 
                               capture_output=True, text=True)
        if result.returncode == 0:
            for line in result.stdout.split('\n'):
                if line.startswith('Version:'):
                    return line.split(':')[1].strip()
    except:
        pass
    return None

def analyze_dependencies(directory):
    """Analisa todas as dependências nos arquivos Python do diretório."""
    py_files = find_py_files(directory)
    dependency_counter = defaultdict(int)
    all_dependencies = set()
    
    for file in py_files:
        imports = extract_imports(file)
        for imp in imports:
            dependency_counter[imp] += 1
            all_dependencies.add(imp)
    
    return dependency_counter, all_dependencies

def generate_requirements(dependencies, include_versions=True):
    """Gera o conteúdo do arquivo requirements.txt."""
    requirements = []
    for package in sorted(dependencies):
        if include_versions:
            version = get_installed_version(package)
            if version:
                requirements.append(f"{package}=={version}")
            else:
                requirements.append(package)
        else:
            requirements.append(package)
    return requirements

def save_requirements_file(directory, requirements):
    """Salva o arquivo requirements.txt no diretório especificado."""
    path = os.path.join(directory, 'requirements.txt')
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(requirements))
    print(f"\nArquivo requirements.txt gerado em: {path}")

if __name__ == "__main__":
    directory = input("Digite o caminho do diretório a ser analisado (ou . para diretório atual): ").strip()
    if not directory:
        directory = "."
    
    print(f"\nAnalisando arquivos Python em: {os.path.abspath(directory)}")
    
    dependency_counter, all_dependencies = analyze_dependencies(directory)
    
    print("\n=== Dependências encontradas ===")
    for dep in sorted(all_dependencies):
        print(f"- {dep}")
    
    include_versions = input("\nDeseja incluir versões dos pacotes? (s/n): ").strip().lower() == 's'
    requirements = generate_requirements(all_dependencies, include_versions)
    
    save_requirements_file(directory, requirements)
    
    print("\nProcesso concluído!")