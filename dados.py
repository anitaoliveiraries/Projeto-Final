
import pandas as pd
import matplotlib.pyplot as plt

COLUNAS = [
    "Call Failure", "Complains", "Subscription Length",
    "Charge Amount", "Seconds of Use", "Frequency of use",
    "Frequency of SMS", "Distinct Called Numbers",
    "Age Group", "Tariff Plan", "Status", "Age",
    "Customer Value", "Churn"
]

# CARREGA E VALIDAR O ARQUIVO
def carregar_dados(arquivo):
    try:
        dados = pd.read_csv(arquivo)

        # Padroniza os espaços dos nomes das colunas
        dados.columns = [" ".join(c.split()) for c in dados.columns]

        if dados.empty:
            raise ValueError("Arquivo vazio.")

        if not set(COLUNAS).issubset(dados.columns):
            raise ValueError("Colunas obrigatórias ausentes.")

        print("Arquivo carregado com sucesso!")
        return dados

    except FileNotFoundError:
        raise FileNotFoundError("Erro: arquivo não encontrado.")
    except Exception as erro:
        raise ValueError("Erro ao abrir o arquivo:", erro)


# VERIFICA E TRATA OS DADOS
def tratar_dados(dados):
    total_inicial = len(dados)
    print("\n--- AMOSTRA DOS DADOS ---")
    print(dados.head())

    print("\nBase original:", dados.shape)

    # Converte as colunas para números
    for coluna in COLUNAS:
        dados[coluna] = pd.to_numeric(
            dados[coluna], errors="coerce"
        )

    print("\n--- QUALIDADE DOS DADOS ---")
    print("\nTipos:")
    print(dados[COLUNAS].dtypes)

    print("\nValores ausentes:")
    print(dados[COLUNAS].isnull().sum())

    print("\nDuplicatas:", dados.duplicated().sum())

    # Identifica valores impossíveis
    invalidos = (
        (dados["Age"] < 0) |
        (dados["Age"] > 100) |
        (dados["Complains"].isin([0, 1]) == False) |
        (dados["Churn"].isin([0, 1]) == False) |
        (dados["Age Group"].isin([1, 2, 3, 4, 5]) == False) |
        (dados["Tariff Plan"].isin([1, 2]) == False) |
        (dados["Status"].isin([1, 2]) == False) |
        (dados[[
            "Call Failure", "Subscription Length",
            "Charge Amount", "Seconds of Use",
            "Frequency of use", "Frequency of SMS",
            "Distinct Called Numbers", "Customer Value"
        ]] < 0).any(axis=1)
    )

    print("\nRegistros com valores impossíveis:", invalidos.sum())

    # Remove dados inválidos, ausentes e duplicados
    dados = dados[~invalidos]
    dados = dados.dropna(subset=COLUNAS)
    dados = dados.drop_duplicates()

    # Traz o novo resultado após tratamento (comparado ao estado inicial)
    print("\n--- RESULTADO DO TRATAMENTO ---")
    print("Base final:", dados.shape) 
    print("Registros removidos:", total_inicial - len(dados))

    return dados


# ANÁLISES ESTATÍSTICAS
def analisar_dados(dados):
    print("\n--- ESTATÍSTICAS ---")
    print(dados.describe().round(2))

    print("\nClientes que cancelaram e permaneceram:")
    print(dados["Churn"].value_counts())

    print("\nTaxa de cancelamento por reclamação (%):")
    print(
        (dados.groupby("Complains")["Churn"].mean() * 100).round(2)
    )

    print("\nTaxa de cancelamento por plano (%):")
    print(
        (dados.groupby("Tariff Plan")["Churn"].mean() * 100).round(2)
    )

    print("\nMédia de uso por situação do cliente:")
    print(
        dados.groupby("Churn")[
            ["Seconds of Use", "Frequency of use",
             "Frequency of SMS", "Customer Value"]
        ].mean().round(2)
    )
