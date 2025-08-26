import os
import shutil
from flask import Flask, render_template_string, request, redirect, send_from_directory, abort, url_for

# --- Configurações do Servidor ---
# Altere estas variáveis para configurar seu servidor
HOST_ = 'localhost'
PORT_ = 8082
# O diretório que o Flask irá servir.
# Por segurança, o servidor só permitirá acesso a arquivos dentro deste diretório.
ROOT_DIRECTORY = os.path.abspath(os.path.join(os.getcwd(), "src", "server"))

app = Flask(__name__)

# --- Template HTML com Jinja2 ---
# Usamos um template para gerar o HTML, o que é mais limpo e seguro.
# As variáveis entre {{ }} são preenchidas pelo Flask.
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="utf-8">
    <title>Flask File Server</title>
    <link rel='stylesheet' href='http://localhost:8082/_views/style.css'>
    
</head>
<body>
    <header>
        <a href="{{ url_for('browse_path', path='') }}"><span>FLASK SERVER</span></a>
        <nav>
            {% if parent_dir %}
            <a href="{{ parent_dir }}">voltar</a>
            {% endif %}
            <a href="#new_folder">nova pasta</a>
            <a href="#upload">upload</a>
        </nav>
    </header>
    <section>
        <h1>Itens em: /{{ current_path }}</h1>
        <ul>
        {% for item in items %}
            <li>
                <a href="{{ url_for('browse_path', path=item.path) }}">{{ item.name }}</a>
                <form method="POST" action="{{ url_for('handle_post', path=current_path) }}" style="display:inline;">
                    <input type="hidden" name="delete" value="{{ item.name }}">
                    <button type="submit">Remover</button>
                </form>
            </li>
        {% endfor %}
        </ul>

        <div class="form-section" id="upload">
            <h2>Upload de Arquivo</h2>
            <form method="POST" action="{{ url_for('handle_post', path=current_path) }}" enctype="multipart/form-data">
                <input type="file" name="file" required>
                <input type="submit" value="Upload Arquivo">
            </form>
        </div>

        <div class="form-section" id="new_folder">
            <h2>Criar Nova Pasta</h2>
            <form method="POST" action="{{ url_for('handle_post', path=current_path) }}">
                <input type="text" name="dirname" placeholder="Nome do novo diretório" required>
                <input type="submit" value="Criar Diretório">
            </form>
        </div>
    </section>
</body>
</html>
"""

def get_items(path):
    """Retorna uma lista de arquivos e diretórios para um determinado caminho."""
    items = []
    full_path = os.path.join(ROOT_DIRECTORY, path)
    
    for name in sorted(os.listdir(full_path), key=str.lower):
        if name.startswith('_') or name.startswith('.'):
            continue # Ignora arquivos e pastas ocultos

        item_path = os.path.join(path, name)
        item_full_path = os.path.join(full_path, name)
        
        if os.path.isdir(item_full_path):
            items.append({'name': name + '/', 'path': item_path, 'type': 'dir'})
        else:
            items.append({'name': name, 'path': item_path, 'type': 'file'})
            
    return items

def get_parent_directory(path):
    """Calcula o link para o diretório pai."""
    if not path:
        return None
    parent = os.path.dirname(path)
    return url_for('browse_path', path=parent)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>', methods=['GET'])
def browse_path(path):
    """Lida com requisições GET para navegar e listar arquivos/diretórios."""
    
    # Medida de segurança: garante que o caminho solicitado está dentro do diretório raiz
    full_path = os.path.join(ROOT_DIRECTORY, path)
    if not os.path.abspath(full_path).startswith(os.path.abspath(ROOT_DIRECTORY)):
        abort(403) # Proibido

    if not os.path.exists(full_path):
        abort(404) # Não encontrado

    if os.path.isfile(full_path):
        # Se for um arquivo, serve o arquivo diretamente
        directory = os.path.dirname(path)
        filename = os.path.basename(path)
        return send_from_directory(os.path.join(ROOT_DIRECTORY, directory), filename)
    
    # Se for um diretório, lista seu conteúdo
    items = get_items(path)
    parent_dir = get_parent_directory(path)
    return render_template_string(HTML_TEMPLATE, items=items, current_path=path, parent_dir=parent_dir)

@app.route('/<path:path>', methods=['POST'])
def handle_post(path):
    """Lida com requisições POST para criar, deletar e fazer upload."""
    
    full_path = os.path.join(ROOT_DIRECTORY, path)
    if not os.path.abspath(full_path).startswith(os.path.abspath(ROOT_DIRECTORY)):
        abort(403)

    # --- Lógica de Remoção ---
    if 'delete' in request.form:
        item_name = request.form['delete'].rstrip('/')
        item_path = os.path.join(full_path, item_name)
        
        try:
            if os.path.isdir(item_path):
                shutil.rmtree(item_path) # Remove diretórios e todo seu conteúdo
            elif os.path.isfile(item_path):
                os.remove(item_path)
        except OSError as e:
            # Poderia retornar uma página de erro aqui
            print(f"Erro ao remover {item_path}: {e}")

    # --- Lógica de Criação de Diretório ---
    elif 'dirname' in request.form:
        dirname = request.form['dirname']
        if '/' not in dirname and '\\' not in dirname and not dirname.startswith('_'):
            new_dir_path = os.path.join(full_path, dirname)
            os.makedirs(new_dir_path, exist_ok=True) # Cria o diretório
            
    # --- Lógica de Upload ---
    elif 'file' in request.files:
        file = request.files['file']
        if file and file.filename:
            filename = file.filename # Cuidado: use uma função para sanitizar o nome do arquivo em produção
            file.save(os.path.join(full_path, filename))

    # Redireciona de volta para o diretório após a ação
    return redirect(url_for('browse_path', path=path))


if __name__ == "__main__":
    print(f"\nServidor Flask iniciado em http://{HOST_}:{PORT_}")
    print(f"Servindo o diretório: {ROOT_DIRECTORY}")
    app.run(host=HOST_, port=PORT_, debug=True) # Inicia o servidor flask com host e porta definidos