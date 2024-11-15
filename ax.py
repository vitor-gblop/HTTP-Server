import http.server
import socketserver
import urllib.parse
import os

# em pt-br

# Configurações do servidor
HOST = 'localhost'
PORT = 8000
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
        """Gera uma página HTML customizada com a lista de arquivos."""

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
            <title>Lista de Arquivos</title>

            <link rel="stylesheet" href="">
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
                    width: 30%;
                }}
                header nav a{{
                    background: #fff;
                    border: 1px solid #ddd;
                }}
                section{{
                    width: 85%;
                    margin: auto;
                }}
                div{{
                    height: 4rem;
                    padding: 20px;
                    background: #fff;
                    border: 1px solid #ddd;
                    margin-bottom: 5px;
                }}
                div form {{
                    height: 100%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
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
                    font-size: 1.8rem;
                    padding: 20px;
                    background: #fff;
                    border: 1px solid #ddd;
                    margin-bottom: 5px;
                }}
                a {{
                    display: block;
                    width: 100%;
                    color: #007bff;
                    text-decoration: none;
                }}
                a:hover {{
                    text-decoration: underline;
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
                <h1>Arquivos no diretório: {get_directory_last_name(remove_trailing_slash(self.path))}</h1>
                <ul>
        """

        # Adiciona os itens da lista de arquivos
        for nome in lista:
            fullname = os.path.join(path, nome)
            display_name = nome
            linkname = nome

            # Adiciona links para os arquivos
            response_content += f'''
            <li> 
                <a href="{linkname}">{display_name}</a>
                <form method="POST" action="{self.path}" style="display:inline;">
                    <input type="hidden" name="delete" value="{display_name}">
                    <button type="submit">Remover</button>
                </form>
            </li>'''

        # Fecha a lista e o HTML
        response_content += f"""
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
        """Lida com requisições POST para criação de diretórios e upload de arquivos."""
        content_type = self.headers['Content-Type']
        if content_type.startswith('multipart/form-data'):
            # Lida com upload de arquivos
            boundary = content_type.split("boundary=")[-1].encode()
            remaining_bytes = int(self.headers['Content-Length'])
            line = self.rfile.readline()
            remaining_bytes -= len(line)

            if boundary not in line:
                self.send_response(400, "Bad Request")
                self.end_headers()
                self.wfile.write("Erro: Formato de upload inválido.".encode('utf-8'))
                return

            line = self.rfile.readline()
            remaining_bytes -= len(line)
            filename = line.decode().split("filename=")[-1].strip().strip('"')
            line = self.rfile.readline()  # Content-Type header
            remaining_bytes -= len(line)
            line = self.rfile.readline()  # Blank line
            remaining_bytes -= len(line)

            last_name = remove_trailing_slash(self.path)
            file_path = self.directory + last_name + "/" + os.path.basename(filename)

            print(get_directory_last_name(self.path))
            print(self.path)
            try:
                with open(file_path, 'wb') as output_file:
                    while remaining_bytes > 0:
                        line = self.rfile.readline()
                        remaining_bytes -= len(line)
                        if boundary in line:
                            break
                        output_file.write(line)

                self.send_response(201, "Created")
                self.send_header("Location", "/")
                self.end_headers()
                self.wfile.write(f"Arquivo '{filename}' enviado com sucesso.".encode('utf-8'))
            except Exception as e:
                self.send_response(500, "Internal Server Error")
                self.end_headers()
                self.wfile.write(f"Erro ao enviar o arquivo: {str(e)}".encode('utf-8'))
        else:
            # Lida com a criação de diretórios
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            params = urllib.parse.parse_qs(post_data.decode('utf-8'))

            dirname = params.get('dirname', [None])[0]
            if dirname:

                last_name = remove_trailing_slash(self.path)
                new_dir_path = self.directory + last_name + "/" + dirname

                try:
                    os.makedirs(new_dir_path)
                    self.send_response(201, "Created")
                    self.send_header("Location", "/")
                    self.end_headers()
                    self.wfile.write(f"Diretório '{dirname}' criado com sucesso.".encode('utf-8'))
                except FileExistsError:
                    self.send_response(409, "Conflict")
                    self.end_headers()
                    self.wfile.write(f"Erro: O diretório '{dirname}' já existe.".encode('utf-8'))
                except Exception as e:
                    self.send_response(500, "Internal Server Error")
                    self.end_headers()
                    self.wfile.write(f"Erro ao criar o diretório: {str(e)}".encode('utf-8'))
            else:
                self.send_response(400, "Bad Request")
                self.end_headers()
                self.wfile.write("Erro: Nome do diretório não informado.".encode('utf-8'))


# metodo que configura o diretorio e inicia o servidor
def startServer(host='localhost', port=8082, dir='.'):
    os.chdir(dir)  # Define o diretório raiz do servidor

    with socketserver.TCPServer((host, port), CustomHandler) as httpd:
        print(f"Servidor HTTP iniciado na porta {port}, servindo o diretório {dir}")
        print(f"Acesse http://{host}:{port} para ver os arquivos.")
        httpd.serve_forever()


# evita chamamentos acidentais
if __name__ == "__main__":
    HOST = input("endereço do server: ") or 'localhost'
    PORT = int(input("Porta que roda o server: ") or 8082)
    startServer(HOST, PORT, DIRECTORY)
