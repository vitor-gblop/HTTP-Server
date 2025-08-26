import http.server
import socketserver
import urllib.parse
import os

# Configurações do servidor
HOST_ = 'localhost'
PORT_ = 8082
DIRECTORY = os.getcwd() + "/src/server"
CSS_PATH = "http://localhost:8082/_views/style.css"


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
            <meta http-equiv="refresh" content="5">
            <title>Lista de Arquivos e Diretórios</title>
            <link rel='stylesheet' href='{CSS_PATH}'>
        </head>
        <body>
            <header>
                <a href="/" ><span>FAST SERVER</span></a>
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
            
            # evita que arquivos e pastas iniciados com _ sejam mostrados
            if display_name.startswith('_'):
                continue
            
            if os.path.isdir(fullname):
                display_name = nome + "/"
                linkname = nome + "/"
            
            
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

        # Verifica se a requisição é para criar um novo diretório
        if 'dirname' in params:
            dirname = params['dirname'][0]
            
            # Evita nomes de diretório maliciosos
            if '/' in dirname or '\\' in dirname or dirname.startswith('_'):
                self.send_response(400, "Bad Request")
                self.end_headers()
                self.wfile.write("Nome de diretório inválido".encode('utf-8'))
                return
            
            # Cria o caminho completo do novo diretório
            new_dir_path = os.path.join(DIRECTORY, self.path.lstrip('/'), dirname)
            
            try:
                os.makedirs(new_dir_path)
                mensagem = (f"Diretório '{dirname}' criado com sucesso.")
                
                self.send_response(200, "OK")
                self.send_header("Location", self.path)
                self.end_headers()
                self.wfile.write(mensagem.encode('utf-8'))
                
            except FileExistsError:
                self.send_response(409, "Conflict")
                self.end_headers()
                self.wfile.write(f"Erro: O diretório '{dirname}' já existe.".encode('utf-8'))
                
            except OSError as e:
                self.send_response(500, "Internal Server Error")
                self.end_headers()
                self.wfile.write(f"Erro ao criar diretório: {str(e)}".encode('utf-8'))
            return


# Método que configura o diretório e inicia o servidor
def startServer(host='localhost', port=8082, dir='.'):
    os.chdir(dir)  # Define o diretório raiz do servidor

    with socketserver.TCPServer((host, port), CustomHandler) as httpd:
        print(f"\nServidor HTTP iniciado na porta {port}, servindo o diretório {dir}")
        print(f"\nAcesse http://{host}:{port} para ver os arquivos.")
        
        httpd.serve_forever()


# Evita chamamentos acidentais
if __name__ == "__main__":
    
    print(f"\nEndereço ip do servidor(padrão:localhost): ")
    HOST_ = input("Especifique o endereço do servidor ou clique enter para o padrão: ") or HOST_
    
    print(f"\nPorta para o servidor(padrão:8082): ")
    PORT_= int(input("Especifique o endereço do servidor ou clique enter para o padrão: ") or PORT_)
    
    print(f"\nCaminho do diretório a ser servido(padrão:{DIRECTORY}): ")
    DIRECTORY_ = input(f"Especifique o diretorio ou clique enter para o padrão: ") or DIRECTORY
    
    startServer(HOST_, PORT_, DIRECTORY_)
