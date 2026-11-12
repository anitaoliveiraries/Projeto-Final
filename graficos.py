import pandas as pd
import matplotlib.pyplot as plt
import os

# Garante que a pasta static/graficos existe
os.makedirs("static/graficos", exist_ok=True)

# Carrega os dados tratados
dados = pd.read_csv("data/Customer Churn tratado.csv")

# Grafico de distribuição(histograma)
plt.figure()
dados["Subscription Length"].plot(kind="hist", bins=20, edgecolor="black")
plt.title("Distribuição do Tempo de Contrato")
plt.xlabel("Meses de Contrato")

plt.ylabel("Quantidade de Clientes")
plt.savefig("static/graficos/distribuicao.png")

plt.close()

# Gráfico de comparação(barras)
plt.figure()
(dados.groupby("Complains")["Churn"].mean() * 100).plot(kind="bar")
plt.title("Comparação: Cancelamento por Reclamação")
plt.xlabel("Fez Reclamação? (0 = Não, 1 = Sim)")
plt.ylabel("Cancelamento (%)")
plt.xticks(rotation=0)
plt.savefig("static/graficos/comparacao.png")

plt.close()

# Gráfico de relação
plt.figure()
plt.scatter(dados["Seconds of Use"], dados["Customer Value"], alpha=0.5)
plt.title("Relação: Tempo de Uso vs Valor do Cliente")
plt.xlabel("Segundos de Uso")
plt.ylabel("Valor do Cliente")
plt.savefig("static/graficos/relacao.png")
plt.close()

print("Os 3 gráficos foram gerados com sucesso")