from flask import Flask, request, render_template_string
import os

# Configurações do servidor
HOST_ = 'localhost'
PORT_ = 8082
UPLOAD_FOLDER = os.getcwd() + "/src/server/uploads" # Diretório onde os arquivos serão salvos
CSS_PATH = "http://localhost:8082/_views/style.css"


app = Flask(__name__)
os.makedirs(UPLOAD_FOLDER, exist_ok=True) # Cria o diretório se não existir

@app.route('/')
def index():
    return render_template_string(
        '''
            <form action="/upload" method="post" enctype="multipart/form-data">
                <input type="file" name="file">
                <input type="submit" value="Upload">
            </form>
        ''' 
    )

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'Nenhum arquivo presente'
    file = request.files['file']
    if not file.filename:
        return 'Nenhum arquivo selecionado'
    
    # Salva o arquivo
    filename = file.filename or "uploaded_file"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)
    return f'Arquivo "{filename}" salvo em {filepath}'

if __name__ == '__main__':
    app.run(debug=True)