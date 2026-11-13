from base64 import b64encode
from io import BytesIO
from pathlib import Path
from math import isfinite

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from flask import Flask, render_template, request

from dados import COLUNAS, COLUNAS_CATEGORICAS, COLUNAS_INTEIRAS, carregar_dados, tratar_dados, analisar_dados
from modelo import COLUNAS_X, carregar_base_padrao, treinar_e_avaliar

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024
app.config["TEMPLATES_AUTO_RELOAD"] = True

BASE_TREINO = carregar_base_padrao()
AVALIACAO = treinar_e_avaliar(BASE_TREINO)
MODELO = AVALIACAO["modelo_escolhido"]


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
