from flask import Flask, render_template, request
from dados import carregar_dados, tratar_dados, analisar_dados

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/results', methods=['POST'])
def results():

    # Recebe o arquivo CSV enviado pelo usuário
    csv_file = request.files['csv-file']

    try:
        # Carrega e valida os dados do arquivo CSV
        dados = carregar_dados(csv_file)

        # Trata os dados carregados
        dados_tratados = tratar_dados(dados)

        # Realiza a análise dos dados tratados
        analisar_dados(dados_tratados)

    except Exception as e:
        return f"Erro: {e}"

    return "Arquivo recebido e tratado com sucesso!"

app.run(debug=True, port=5000)