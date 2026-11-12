from flask import Flask, render_template, request
from dados import carregar_dados, tratar_dados, analisar_dados
import joblib
import pandas as pd
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/results', methods=['POST'])
def results():
    csv_file = request.files['csv-file']
    try:
        dados = carregar_dados(csv_file)
        dados_tratados = tratar_dados(dados)
        analisar_dados(dados_tratados)
    except Exception as e:
        return f"Erro: {e}"
    
    return render_template('analise.html')

# --- rota de previsão  ---
@app.route('/prever', methods=['GET', 'POST'])
def prever():
    # Se, o utilizador apenas entrar na página, mostra o formulário vazio
    if request.method == 'GET':
        return render_template('previsao.html')

    # Se o utilizador clicar no botão "Prever Cancelamento", processa os dados
    if request.method == 'POST':
        try:
            # Pega tudo o que foi digitado no HTML e transforma em formato de tabela (DataFrame)
            dados_digitados = {
                "Call Failure": [int(request.form['Call Failure'])],
                "Complains": [int(request.form['Complains'])],
                "Subscription Length": [int(request.form['Subscription Length'])],
                "Charge Amount": [int(request.form['Charge Amount'])],
                "Seconds of Use": [int(request.form['Seconds of Use'])],
                "Frequency of use": [int(request.form['Frequency of use'])],
                "Frequency of SMS": [int(request.form['Frequency of SMS'])],
                "Distinct Called Numbers": [int(request.form['Distinct Called Numbers'])],
                "Age Group": [int(request.form['Age Group'])],
                "Tariff Plan": [int(request.form['Tariff Plan'])],
                "Status": [int(request.form['Status'])],
                "Age": [int(request.form['Age'])],
                "Customer Value": [float(request.form['Customer Value'])]
            }
            df_cliente = pd.DataFrame(dados_digitados)

            # Carrega o modelo de IA que salvámos antes com o joblib
            caminho_modelo = os.path.join(os.path.dirname(__file__), "models", "modelo_vencedor.pkl")
            modelo = joblib.load(caminho_modelo)

            # Faz a previsão
            resultado = modelo.predict(df_cliente)[0]

            # Traduz a resposta da máquina (0 ou 1) para um texto
            if resultado == 1:
                mensagem_final = "ALERTA: Este cliente tem alto risco de CANCELAR o plano."
            else:
                mensagem_final = "SEGURO: Este cliente provavelmente VAI PERMANECER na empresa."

            return render_template('previsao.html', mensagem=mensagem_final)

        except Exception as erro:
            # Tratamento de erro caso o utilizador digite letras onde devia ser número
            return render_template('previsao.html', erro=f"Erro ao processar: {erro}. Verifique se digitou apenas números.")

if __name__ == '__main__':
    app.run(debug=True, port=5000)