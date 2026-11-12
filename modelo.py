import pandas as pd
import os
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix
import joblib

print("Iniciando o treinamento dos modelos de Machine Learning...")


#  pega o caminho exato da pasta onde este script modelo.py está rodando
diretorio_atual = os.path.dirname(os.path.abspath(__file__))

# adiciona a pasta data no caminho antes de chamar o arquivo CSV
caminho_csv = os.path.join(diretorio_atual, "data", "Customer Churn tratado.csv")

#  carrega os dados usando esse caminho correto
dados = pd.read_csv(caminho_csv)

#  separando as variáveis (Regra: O alvo 'Churn' não entra no X)
X = dados.drop("Churn", axis=1) # Todas as colunas, menos o Churn
y = dados["Churn"]              # Apenas a coluna Churn

#  separando em Treino (80%) e Teste (20%) com semente fixa (random_state)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=42
)

# treinando o PRIMEIRO modelo: Árvore de Decisão
print("\n-> Treinando a Árvore de Decisão...")
modelo_arvore = DecisionTreeClassifier(random_state=42)
modelo_arvore.fit(X_train, y_train)

# fazendo as previsões no conjunto de teste
previsao_arvore = modelo_arvore.predict(X_test)
acuracia_arvore = accuracy_score(y_test, previsao_arvore)
matriz_arvore = confusion_matrix(y_test, previsao_arvore)

#  treinando o segundo modelo: Random Forest
print("-> Treinando o Random Forest...")
modelo_rf = RandomForestClassifier(random_state=42)
modelo_rf.fit(X_train, y_train)

# fazendo as previsões no conjunto de teste
previsao_rf = modelo_rf.predict(X_test)
acuracia_rf = accuracy_score(y_test, previsao_rf)
matriz_rf = confusion_matrix(y_test, previsao_rf)

#  comparação final (que será colocada no reedme)
print("\n================ COMPARAÇÃO DOS MODELOS ================")
print(f"Acurácia da Árvore de Decisão : {acuracia_arvore:.2f}")
print("Matriz de Confusão (Árvore):\n", matriz_arvore)

print(f"\nAcurácia do Random Forest   : {acuracia_rf:.2f}")
print("Matriz de Confusão (RF):\n", matriz_rf)
print("========================================================")

# salvando o melhor modelo para o flask usar na aplicação
# cria a pasta models se ela não existir
os.makedirs("models", exist_ok=True)

# vamos salvar o Random Forest pois, em dados tabulares, ele costuma errar menos
joblib.dump(modelo_rf, "models/modelo_vencedor.pkl")
print("\nModelo vencedor salvo com sucesso em 'models/modelo_vencedor.pkl'!")