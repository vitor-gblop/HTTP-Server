import http.server
import socketserver
import urllib.parse
import os

# Configurações do servidor
HOST_ = 'localhost'
PORT_ = 8082
DIRECTORY = 'C:/Users/dayla/Documents/Arquivos/Python/httpServer/src'


def get_directory_last_name(caminho):
    return os.path.basename(caminho)


def remove_trailing_slash(path):
    return path.rstrip('/')


class CustomHandler(http.server.SimpleHTTPRequestHandler):
    # Sobrescreve o método para definir o diretório base
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def list_directory(self, path):
        """Gera uma página HTML customizada com a lista de arquivos e diretórios."""
        try:
            lista = os.listdir(path)
        except os.error:
            self.send_error(404, "Não foi possível listar o diretório")
            return None

        lista.sort(key=lambda a: a.lower())

        # Gera o conteúdo HTML
        response_content = f"""
        <!DOCTYPE html>
        <html lang="pt-br">
        <head>
            <meta charset="utf-8">
            <title>Lista de Arquivos e Diretórios</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #f0f0f0;
                    color: #333;
                    padding: 20px;
                }}
                header{{
                    font-size: 1.5rem;
                    display: flex;
                    justify-content: space-between;
                }}
                header nav{{
                    display: flex;
                    gap: 10px;
                    width: 40%;
                }}
                header nav a{{
                    font-size: 1.2rem;
                    padding:4px;
                    background: #fff;
                    border: 1px solid #ddd;
                }}
                h1 {{
                    font-size: larger;
                    color: #5a5a5a;
                }}
                ul {{
                    list-style-type: none;
                    padding: 0;
                }}
                li {{
                    display: flex;
                    justify-content: space-between;
                    font-size: 1.2rem;
                    padding: 10px;
                    background: #fff;
                    border: 1px solid #ddd;
                    margin-bottom: 5px;
                }}
                a {{
                    display: inline-block;
                    color: #007bff;
                    text-decoration: none;
                    margin-right: 10px;
                }}
                a:hover {{
                    text-decoration: underline;
                }}
                form {{
                    display: inline-block;
                }}
                button {{
                    background: #ff4d4d;
                    border: none;
                    color: white;
                    cursor: pointer;
                    padding: 5px 10px;
                    margin-left: 10px;
                }}
                .form-section{{
                    padding: 12px;
                    background: #fff;
                    border: 1px solid #ddd;
                    margin-bottom: 5px;
                }}
            </style>
        </head>
        <body>
            <header>
                <a href="/" ><span>SERVER</span></a>
                <nav>
                    <a href="../">voltar</a>
                    <a href="#new_folder">nova pasta</a>
                    <a href="#upload">upload</a>
                </nav>
            </header>
            <section>
                <h1>Arquivos e Diretórios em: {get_directory_last_name(remove_trailing_slash(self.path))}</h1>
                <ul>
        """

        # Adiciona os itens da lista de arquivos e diretórios
        for nome in lista:
            fullname = os.path.join(path, nome)
            display_name = nome
            linkname = nome

            # Adiciona links para os arquivos e diretórios com opção de remover
            response_content += f'''
            <li>
                <a href="{linkname}">{display_name}</a>
                <form method="POST" action="{self.path}" style="display:inline;">
                    <input type="hidden" name="delete" value="{display_name}">
                    <button type="submit">Remover</button>
                </form>
            </li>
            '''

        # Fecha a lista e o HTML
        response_content += """
                </ul>
                <div class="form-section" id="upload">
                    <form method="POST" action="{self.path}" enctype="multipart/form-data">
                        <input type="file" name="file" required>
                        <input type="submit" value="Upload Arquivo">
                    </form>
                </div>
                <div class="form-section" id="new_folder">
                    <form method="POST" action="{self.path}">
                        <input type="text" name="dirname" placeholder="Nome do novo diretório" required>
                        <input type="submit" value="Criar Diretório">
                    </form>
                </div>
            </section>
        </body>
        </html>
        """

        # Envia a resposta
        encoded = response_content.encode('utf-8', 'surrogateescape')
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)
        return None

    def do_POST(self):
        """Lida com requisições POST para criação de diretórios, upload e remoção de arquivos/diretórios."""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        params = urllib.parse.parse_qs(post_data.decode('utf-8'))

        # Verifica se a requisição é para remover um arquivo ou diretório
        if 'delete' in params:
            nome = params['delete'][0]
            item_path = os.path.join(DIRECTORY, self.path.lstrip('/'), nome)
            try:
                # Verifica se é um diretório ou arquivo e remove
                if os.path.isdir(item_path):
                    os.rmdir(item_path)  # Remove diretório vazio
                    mensagem = f"Diretório '{nome}' removido com sucesso."
                elif os.path.isfile(item_path):
                    os.remove(item_path)  # Remove arquivo
                    mensagem = f"Arquivo '{nome}' removido com sucesso."
                else:
                    self.send_response(404, "Not Found")
                    self.end_headers()
                    self.wfile.write(f"Erro: O item '{nome}' não foi encontrado.".encode('utf-8'))
                    return

                self.send_response(200, "OK")
                self.send_header("Location", "/")
                self.end_headers()
                self.wfile.write(mensagem.encode('utf-8'))
            except FileNotFoundError:
                self.send_response(404, "Not Found")
                self.end_headers()
                self.wfile.write(f"Erro: O item '{nome}' não foi encontrado.".encode('utf-8'))
            except OSError as e:
                self.send_response(500, "Internal Server Error")
                self.end_headers()
                self.wfile.write(f"Erro ao remover o item: {str(e)}. Verifique se o diretório está vazio.".encode('utf-8'))
            return

        # Código existente para upload e criação de diretórios permanece aqui

# Método que configura o diretório e inicia o servidor
def startServer(host='localhost', port=8082, dir='.'):
    os.chdir(dir)  # Define o diretório raiz do servidor

    with socketserver.TCPServer((host, port), CustomHandler) as httpd:
        print(f"Servidor HTTP iniciado na porta {port}, servindo o diretório {dir}")
        print(f"Acesse http://{host}:{port} para ver os arquivos.")
        httpd.serve_forever()

# Evita chamamentos acidentais
if __name__ == "__main__":
    HOST_ = input("Endereço do servidor: ") or HOST_
    PORT_= int(input("Porta para o servidor: ") or PORT_)
    startServer(HOST_, PORT_, DIRECTORY)
