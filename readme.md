# Servidor de Arquivos Simples

Este é um servidor de arquivos simples, construído com Python e o micro-framework Flask. Ele fornece uma interface web para navegar, fazer upload, criar e deletar arquivos e diretórios em um servidor local.

## Funcionalidades

-   **Navegação de Diretórios:** Navegue facilmente pela estrutura de pastas.
-   **Visualização e Download:** Clique em um arquivo para visualizá-lo no navegador ou para fazer o download.
-   **Upload de Arquivos:** Envie arquivos para o diretório atual através de um formulário simples.
-   **Criação de Pastas:** Crie novas pastas no diretório atual.
-   **Remoção:** Exclua arquivos ou pastas (incluindo todo o seu conteúdo) de forma recursiva.
-   **Segurança:** Impede o acesso a arquivos e pastas fora do diretório raiz definido (proteção contra *Directory Traversal*).

## Requisitos

-   Python 3.x
-   Flask
-   Flask-Cors

## Instalação e Configuração

1.  **Clone ou baixe os arquivos** para o seu computador.

2.  **Instale as dependências.** É altamente recomendado usar um ambiente virtual (`venv`).
    ```bash
    # Crie um ambiente virtual (opcional, mas recomendado)
    python -m venv venv
    
    # Ative o ambiente virtual
    # No Windows:
    .\venv\Scripts\activate
    # No macOS/Linux:
    # source venv/bin/activate

    # Instale as bibliotecas necessárias
    pip install Flask Flask-Cors
    ```

3.  **Estrutura de Diretórios:** O servidor foi projetado para servir arquivos de uma pasta específica. Certifique-se de que a seguinte estrutura exista a partir da raiz do projeto:
    ```
    .
    ├── public/
    │   ├── server.py       # O script principal do Flask
    │   ├── static/
    │   │   └── style.css   # A folha de estilos
    │   └── src/
    │       └── server/     # <-- Este é o diretório raiz onde seus arquivos ficarão
    └── ...
    ```
    - Todos os arquivos que você deseja gerenciar devem estar dentro de `public/src/server/`.

4.  **Configuração (Opcional):** Você pode alterar o host, a porta e o diretório raiz editando as variáveis no topo do arquivo `server.py`:
    ```python
    # --- Configurações do Servidor ---
    HOST_ = '0.0.0.0'
    PORT_ = 8082
    ROOT_DIRECTORY = os.path.abspath(os.path.join(os.getcwd(), "public", "src", "server"))
    ```

## Como Executar

1.  Certifique-se de que seu terminal está no diretório `public`.
2.  Execute o script Python:
    ```bash
    python server.py
    ```
3.  O terminal mostrará uma mensagem indicando que o servidor foi iniciado:
    ```
    Servidor Flask iniciado em http://0.0.0.0:8082
    Servindo o diretório: C:\...\HTTP-server\public\src\server
    ```
4.  Abra seu navegador e acesse `http://127.0.0.1:8082` ou `http://localhost:8082` para começar a usar.


