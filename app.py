from base64 import b64encode
from io import BytesIO
from pathlib import Path
from math import isfinite

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from flask import Flask, render_template, request
<<<<<<< HEAD

from dados import COLUNAS, COLUNAS_CATEGORICAS, COLUNAS_INTEIRAS, carregar_dados, tratar_dados, analisar_dados
from modelo import COLUNAS_X, carregar_base_padrao, treinar_e_avaliar
=======
from dados import carregar_dados, tratar_dados, analisar_dados
import joblib
import pandas as pd
import os
>>>>>>> b7c54732b83473e33fb0faa2d8c31152ac9d34f5

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024
app.config["TEMPLATES_AUTO_RELOAD"] = True

BASE_TREINO = carregar_base_padrao()
AVALIACAO = treinar_e_avaliar(BASE_TREINO)
MODELO = AVALIACAO["modelo_escolhido"]

<<<<<<< HEAD

def figura_base64(figura):
    arquivo = BytesIO()
    figura.tight_layout()
    figura.savefig(arquivo, format="png", dpi=130, bbox_inches="tight")
    plt.close(figura)
    return b64encode(arquivo.getvalue()).decode("ascii")


def criar_graficos(dados, analise):
    imagens = []
    fig, ax = plt.subplots(figsize=(6, 3.5))
    contagem = dados["Churn"].value_counts().reindex([0, 1], fill_value=0)
    ax.bar(["Permaneceu", "Cancelou"], contagem.values, color=["#536779", "#d27850"])
    ax.set(title="Clientes por situação", ylabel="Número de clientes")
    imagens.append(figura_base64(fig))

    fig, ax = plt.subplots(figsize=(6, 3.5))
    grupos = dados.groupby("Complains")["Churn"].mean().reindex([0, 1]) * 100
    ax.bar(["Sem reclamação", "Com reclamação"], grupos.fillna(0).values, color="#526d82")
    ax.set(title="Cancelamento por reclamação", ylabel="Clientes que cancelaram (%)", ylim=(0, 100))
    imagens.append(figura_base64(fig))

    fig, ax = plt.subplots(figsize=(6, 3.5))
    medias = dados.groupby("Churn")["Seconds of Use"].mean().reindex([0, 1]).fillna(0)
    ax.bar(["Permaneceu", "Cancelou"], medias.values, color=["#536779", "#d27850"])
    ax.set(title="Uso médio do serviço por situação", ylabel="Segundos de uso")
    imagens.append(figura_base64(fig))
    return imagens


def avaliar_formulario(form):
    linha = {}
    try:
        for coluna in COLUNAS_X:
            texto = form.get(coluna, "").strip().replace(",", ".")
            if not texto:
                raise ValueError(f"Preencha o campo {coluna}.")
            try:
                valor = float(texto)
            except ValueError as erro:
                raise ValueError(f"Informe um número válido para {coluna}.") from erro
            if not isfinite(valor):
                raise ValueError(f"Informe um número válido para {coluna}.")
            if coluna in COLUNAS_INTEIRAS and not valor.is_integer():
                raise ValueError(f"Informe um número inteiro para {coluna}.")
            linha[coluna] = valor
    except ValueError as erro:
        raise ValueError(str(erro)) from erro

    for coluna in COLUNAS_X:
        if coluna not in COLUNAS_CATEGORICAS and linha[coluna] < 0:
            raise ValueError(f"{coluna} não pode ser negativo.")
    if not 0 <= linha["Age"] <= 100:
        raise ValueError("Idade deve estar entre 0 e 100 anos.")
    dominios = {"Complains": [0, 1], "Age Group": [1, 2, 3, 4, 5], "Tariff Plan": [1, 2]}
    for coluna, opcoes in dominios.items():
        if int(linha[coluna]) not in opcoes:
            raise ValueError(f"Opção inválida para {coluna}.")
        linha[coluna] = int(linha[coluna])
    return pd.DataFrame([linha], columns=COLUNAS_X)


@app.route("/")
def index():
    return render_template("index.html", colunas=COLUNAS_X)


@app.route("/results", methods=["POST"])
def results():
    csv_file = request.files.get("csv-file")
    if csv_file is None or not csv_file.filename:
        return render_template("results.html", erro="Selecione um arquivo CSV para continuar."), 400
    if not csv_file.filename.lower().endswith(".csv"):
        return render_template("results.html", erro="O arquivo precisa ter a extensão .csv."), 400
    try:
        dados_brutos = carregar_dados(csv_file)
        dados, tratamento = tratar_dados(dados_brutos)
        analise = analisar_dados(dados)
        graficos = criar_graficos(dados, analise)
    except ValueError as erro:
        return render_template("results.html", erro=str(erro)), 400

    return render_template(
        "results.html", nome_arquivo=Path(csv_file.filename).name,
        tratamento=tratamento, analise=analise, graficos=graficos,
        avaliacao=AVALIACAO,
    )


@app.route("/prever", methods=["POST"])
def prever():
    try:
        linha = avaliar_formulario(request.form)
    except ValueError as erro:
        return render_template("index.html", colunas=COLUNAS_X, erro_previsao=str(erro)), 400
    predicao = int(MODELO.predict(linha)[0])
    chance = float(MODELO.predict_proba(linha)[0][1])
    return render_template(
        "index.html", colunas=COLUNAS_X,
        resultado_previsao="Risco de cancelamento identificado" if predicao == 1 else "Baixo risco de cancelamento identificado",
        probabilidade=chance * 100,
    )


@app.errorhandler(413)
def arquivo_grande(_erro):
    return render_template("results.html", erro="O arquivo ultrapassa o limite de 8 MB."), 413


if __name__ == "__main__":
    app.run(debug=False, port=5000)
=======
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
>>>>>>> b7c54732b83473e33fb0faa2d8c31152ac9d34f5
