import pandas as pd
import matplotlib.pyplot as plt

# Carrega os dados tratados
dados = pd.read_csv("Customer Churn tratado.csv")

# Gráfico 1: clientes que cancelaram ou permaneceram
dados["Churn"].value_counts().sort_index().plot(kind="bar")

plt.title("Clientes que cancelaram e permaneceram")
plt.xlabel("Churn (0 = permaneceu, 1 = cancelou)")
plt.ylabel("Quantidade")
plt.savefig("graficos/cancelamentos.png")
plt.show()


# Gráfico 2: cancelamento por reclamação
(dados.groupby("Complains")["Churn"].mean() * 100).plot(kind="bar")

plt.title("Cancelamento por reclamação")
plt.xlabel("Reclamação")
plt.ylabel("Cancelamento (%)")
plt.savefig("graficos/reclamacoes.png")
plt.show()


# Gráfico 3: cancelamento por plano
(dados.groupby("Tariff Plan")["Churn"].mean() * 100).plot(kind="bar")

plt.title("Cancelamento por plano tarifário")
plt.xlabel("Plano")
plt.ylabel("Cancelamento (%)")
plt.savefig("graficos/planos.png")
plt.show()