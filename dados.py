"""Leitura, validação, limpeza e análise da base de churn."""
import re

import pandas as pd

COLUNAS = [
    "Call Failure", "Complains", "Subscription Length", "Charge Amount",
    "Seconds of Use", "Frequency of use", "Frequency of SMS",
    "Distinct Called Numbers", "Age Group", "Tariff Plan", "Status",
    "Age", "Customer Value", "Churn",
]
COLUNAS_CATEGORICAS = ["Complains", "Age Group", "Tariff Plan"]
COLUNAS_INTEIRAS = [
    "Call Failure", "Complains", "Subscription Length", "Charge Amount",
    "Seconds of Use", "Frequency of use", "Frequency of SMS",
    "Distinct Called Numbers", "Age Group", "Tariff Plan", "Status", "Age", "Churn",
]
COLUNAS_NAO_NEGATIVAS = [
    "Call Failure", "Subscription Length", "Charge Amount", "Seconds of Use",
    "Frequency of use", "Frequency of SMS", "Distinct Called Numbers",
    "Customer Value",
]


def normalizar_colunas(dataframe):
    dataframe = dataframe.copy()
    dataframe.columns = [re.sub(r"\s+", " ", str(coluna)).strip() for coluna in dataframe.columns]
    return dataframe


def carregar_dados(arquivo):
    """Lê CSV com vírgula ou ponto e vírgula e valida o esquema esperado."""
    if arquivo is None:
        raise ValueError("Selecione um arquivo CSV para continuar.")
    try:
        dados = pd.read_csv(arquivo, sep=None, engine="python", encoding="utf-8-sig")
    except (pd.errors.EmptyDataError, pd.errors.ParserError, UnicodeDecodeError, ValueError) as erro:
        raise ValueError("Não foi possível ler o arquivo. Envie um CSV válido em UTF-8.") from erro

    dados = normalizar_colunas(dados)
    if dados.empty:
        raise ValueError("O arquivo não possui registros.")
    ausentes = [coluna for coluna in COLUNAS if coluna not in dados.columns]
    if ausentes:
        raise ValueError("Colunas obrigatórias ausentes: " + ", ".join(ausentes))
    if len(dados) > 100_000:
        raise ValueError("O arquivo deve ter no máximo 100.000 registros.")

    for coluna in COLUNAS:
        dados[coluna] = pd.to_numeric(dados[coluna], errors="coerce")
    if dados[COLUNAS].isna().all(axis=1).any():
        raise ValueError("Há linhas sem nenhum valor numérico reconhecível.")
    return dados


def _tabela(dataframe):
    return {"colunas": [str(c) for c in dataframe.columns], "linhas": dataframe.to_dict(orient="records")}


def tratar_dados(dados):
    dados = normalizar_colunas(dados)
    total_inicial = len(dados)
    amostra = _tabela(dados[COLUNAS].head().fillna("—"))

    for coluna in COLUNAS:
        dados[coluna] = pd.to_numeric(dados[coluna], errors="coerce")

    ausentes = dados[COLUNAS].isna().sum()
    tipos = dados[COLUNAS].dtypes.astype(str)
    duplicatas = int(dados.duplicated(subset=COLUNAS).sum())
    invalidos = dados[COLUNAS].isna().any(axis=1)
    invalidos |= dados[COLUNAS_INTEIRAS].mod(1).ne(0).any(axis=1)
    invalidos |= (dados["Age"] < 0) | (dados["Age"] > 100)
    for coluna, valores in {"Complains": [0, 1], "Churn": [0, 1], "Age Group": [1, 2, 3, 4, 5], "Tariff Plan": [1, 2], "Status": [1, 2]}.items():
        invalidos |= ~dados[coluna].isin(valores)
    invalidos |= (dados[COLUNAS_NAO_NEGATIVAS] < 0).any(axis=1)
    invalidos_count = int(invalidos.sum())

    limpos = dados.loc[~invalidos, COLUNAS].drop_duplicates().copy()
    qualidade = pd.DataFrame({
        "Coluna": COLUNAS,
        "Tipo identificado": [tipos[c] for c in COLUNAS],
        "Valores ausentes": [int(ausentes[c]) for c in COLUNAS],
    })
    tratamento = {
        "amostra": amostra,
        "qualidade": _tabela(qualidade),
        "base_original": {"registros": total_inicial, "colunas": len(dados.columns)},
        "duplicatas": duplicatas,
        "registros_invalidos": invalidos_count,
        "base_final": {"registros": len(limpos), "colunas": len(limpos.columns)},
        "registros_removidos": total_inicial - len(limpos),
    }
    if limpos.empty:
        raise ValueError("Nenhum registro válido restou após a limpeza.")
    if limpos["Churn"].nunique() < 2:
        raise ValueError("A coluna Churn precisa conter as duas classes: 0 e 1.")
    return limpos, tratamento


def analisar_dados(dados):
    contagem = dados["Churn"].value_counts().reindex([0, 1], fill_value=0)
    por_reclamacao = (dados.groupby("Complains", observed=True)["Churn"].mean() * 100).round(1)
    por_plano = (dados.groupby("Tariff Plan", observed=True)["Churn"].mean() * 100).round(1)
    churn_pct = float(dados["Churn"].mean() * 100)
    taxa_reclamacao = {int(k): float(v) for k, v in por_reclamacao.items()}
    taxa_plano = {int(k): float(v) for k, v in por_plano.items()}
    media_uso = dados.groupby("Churn", observed=True)["Seconds of Use"].mean()
    situacao_uso = {int(k): float(v) for k, v in media_uso.items()}
    estatisticas = dados.describe().round(2).rename_axis("Métrica").reset_index()
    churn = pd.DataFrame({"Situação": ["Permaneceu (0)", "Cancelou (1)"], "Clientes": [int(contagem[0]), int(contagem[1])]})
    reclamacoes = pd.DataFrame({"Reclamação": ["Não (0)", "Sim (1)"], "Cancelamento (%)": [taxa_reclamacao.get(0, 0), taxa_reclamacao.get(1, 0)]})
    planos = pd.DataFrame({"Plano tarifário": [f"Plano {k}" for k in sorted(taxa_plano)], "Cancelamento (%)": [taxa_plano[k] for k in sorted(taxa_plano)]})
    uso = pd.DataFrame({"Situação": ["Permaneceu (0)", "Cancelou (1)"], "Uso médio (segundos)": [round(situacao_uso.get(0, 0), 2), round(situacao_uso.get(1, 0), 2)]})
    maior_grupo = "sem reclamação" if taxa_reclamacao.get(0, 0) >= taxa_reclamacao.get(1, 0) else "com reclamação"
    maior_taxa = max(taxa_reclamacao.values(), default=0)
    plano_top = max(taxa_plano, key=taxa_plano.get) if taxa_plano else None
    interpretacoes = [
        f"{contagem[1]} de {len(dados)} clientes ({churn_pct:.1f}%) cancelaram; a classe de cancelamento é menor que a de permanência.",
        f"A maior taxa de cancelamento por reclamação aparece entre clientes {maior_grupo} ({maior_taxa:.1f}%). Associação não significa causa.",
        f"O plano {plano_top} apresenta a maior taxa de cancelamento ({taxa_plano.get(plano_top, 0):.1f}%).",
        f"O uso médio foi de {situacao_uso.get(1, 0):.0f} segundos entre quem cancelou e {situacao_uso.get(0, 0):.0f} segundos entre quem permaneceu.",
    ]
    return {
        "estatisticas": _tabela(estatisticas),
        "churn": _tabela(churn),
        "cancelamento_reclamacao": _tabela(reclamacoes),
        "cancelamento_plano": _tabela(planos),
        "uso_por_situacao": _tabela(uso),
        "interpretacoes": interpretacoes,
        "churn_percentual": round(churn_pct, 1),
        "taxa_reclamacao": taxa_reclamacao,
        "taxa_plano": taxa_plano,
        "uso_por_situacao_dict": situacao_uso,
    }
