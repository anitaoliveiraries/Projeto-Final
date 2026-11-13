# Análise de churn de clientes

Aplicação web em Flask para analisar dados de clientes de telecomunicações e estimar a classe `Churn` (cancelou ou permaneceu).

## Pergunta do projeto

É possível identificar clientes com maior chance de cancelar usando informações de uso e de contrato disponíveis antes do encerramento do serviço?

## Dados e fonte

A base é o conjunto **Iranian Churn**, disponibilizado pelo UCI Machine Learning Repository. A coleta cobre 12 meses; os atributos de entrada representam os primeiros nove meses, e o rótulo de churn é observado ao final do período. O intervalo de três meses permite tratar a tarefa como previsão a partir de informações anteriores ao cancelamento.

- Fonte: [UCI Machine Learning Repository — Iranian Churn](https://archive.ics.uci.edu/dataset/563/iranian%2Bchurn%2Bdataset)
- DOI: [10.24432/C5JW3Z](https://doi.org/10.24432/C5JW3Z)
- Licença indicada pelo UCI: CC BY 4.0.
- `data/Customer Churn.csv`: arquivo original, com 3.150 linhas.
- `data/Customer Churn tratado.csv`: versão fornecida com duplicatas exatas removidas, com 2.850 linhas.

O upload aceita CSV com as 14 colunas do projeto. Os gráficos e tabelas são refeitos a partir do arquivo enviado. O modelo de previsão fica fixo e é treinado na base tratada incluída no repositório.

## Variáveis do modelo

- **Alvo (`y`):** `Churn` — 0 = permaneceu; 1 = cancelou.
- **Entradas (`X`):** `Call Failure`, `Complains`, `Subscription Length`, `Charge Amount`, `Seconds of Use`, `Frequency of use`, `Frequency of SMS`, `Distinct Called Numbers`, `Age Group`, `Tariff Plan`, `Age` e `Customer Value`.
- `Status` é recebido e conferido no CSV, mas foi excluído de `X` porque pode indicar uma condição muito próxima do próprio alvo e facilitar vazamento de informação.
- A codificação numérica das categorias foi preservada como aparece na base. `Complains`: 0/1; `Age Group`: 1 a 5; `Tariff Plan`: 1 ou 2. Não foi adicionada interpretação para códigos sem legenda no arquivo fornecido.

## Limpeza e análise

A aplicação converte as 14 colunas esperadas para valores numéricos e remove linhas com campos ausentes ou não numéricos, valores fracionários em campos inteiros, valores fora dos domínios de `Churn`, `Complains`, `Age Group`, `Tariff Plan` e `Status`, idades fora de 0–100, valores negativos em campos de contagem/uso/valor e duplicatas exatas. Não preenche valores ausentes; por isso a base original é preservada e a limpeza pode ser conferida na tela.

Na base tratada incluída, há 2.850 registros válidos e 300 duplicatas exatas foram removidas. Não foram encontrados valores ausentes ou inválidos. Os resultados da análise mostram:

1. 446 clientes (15,6%) cancelaram; 2.404 (84,4%) permaneceram.
2. A taxa de cancelamento é 82,6% entre os registros com reclamação e 9,8% entre os sem reclamação.
3. O plano tarifário 1 tem 16,8% de cancelamento e o plano 2 tem 2,6%.
4. O uso médio registrado é 1.649 segundos para quem cancelou e 5.070 para quem permaneceu.

Essas diferenças são associações observadas na base e não demonstram causa.

## Dicionário de dados

| Coluna | Uso | Descrição e codificação |
|---|---|---|
| `Call Failure` | Entrada | Número de falhas de chamadas. |
| `Complains` | Entrada | Reclamação registrada: 0 = não; 1 = sim. |
| `Subscription Length` | Entrada | Duração do contrato/assinatura; a base não informa unidade no CSV. |
| `Charge Amount` | Entrada | Indicador numérico de cobrança; a base fornecida não informa moeda ou unidade. |
| `Seconds of Use` | Entrada | Tempo de uso registrado em segundos. |
| `Frequency of use` | Entrada | Frequência de uso registrada como número. |
| `Frequency of SMS` | Entrada | Frequência de SMS registrada como número. |
| `Distinct Called Numbers` | Entrada | Quantidade de números distintos chamados. |
| `Age Group` | Entrada | Faixa etária codificada de 1 a 5; os limites das faixas não estão no CSV recebido. |
| `Tariff Plan` | Entrada | Plano tarifário codificado como 1 ou 2; a legenda dos códigos não está no CSV recebido. |
| `Status` | Recebida, excluída de X | Campo binário/categórico da base. Foi excluído para reduzir risco de vazamento do alvo. |
| `Age` | Entrada | Idade em anos, conforme o nome do campo; valores válidos de 0 a 100 no tratamento. |
| `Customer Value` | Entrada | Indicador numérico de valor do cliente; a unidade não está no CSV recebido. |
| `Churn` | Alvo | 0 = permaneceu; 1 = cancelou. |

## Modelos e avaliação

Foram comparados dois classificadores permitidos: Regressão Logística e Random Forest. Ambos usam a mesma divisão estratificada (`train_test_split`), 80% para treino e 20% para teste, `random_state=42`. A padronização da Regressão Logística faz parte de um `Pipeline` e é ajustada somente nos dados de treino. O conjunto de teste contém 570 clientes: 481 permaneceram e 89 cancelaram.

| Modelo | Acurácia | Precisão (classe 1) | Recall (classe 1) | F1 (classe 1) |
|---|---:|---:|---:|---:|
| Regressão Logística | 0,807 | 0,441 | 0,876 | 0,587 |
| Random Forest | 0,961 | 0,894 | 0,854 | 0,874 |

O Random Forest é usado no formulário por ter o maior F1. Na matriz de confusão, ele identificou 76 dos 89 clientes que cancelaram e deixou 13 passar; também marcou como risco 9 clientes que permaneceram. A Regressão Logística identificou 78 cancelamentos, mas marcou 99 clientes que permaneceram como risco. Para uma ação de retenção, falsos negativos podem significar perder a oportunidade de conversar com alguém que vai sair; falsos positivos podem gerar contatos desnecessários. A escolha depende também do custo dessas ações, que não foi medido neste trabalho.

Acurácia, precisão, recall e F1 são calculados no conjunto de teste. As matrizes são exibidas na página de resultados; as linhas representam a classe real e as colunas a prevista (0 = permaneceu, 1 = cancelou).

## Como executar

Requer Python 3.10 ou superior.

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Abra `http://127.0.0.1:5000`. A página inicial tem formulário de previsão e upload de CSV. Para gerar a avaliação no terminal:

```bash
python treinar.py
```

## Formato aceito no upload

O arquivo deve ser CSV com estas colunas (maiúsculas/minúsculas e espaços entre palavras conforme os nomes abaixo):

```text
Call Failure, Complains, Subscription Length, Charge Amount, Seconds of Use,
Frequency of use, Frequency of SMS, Distinct Called Numbers, Age Group,
Tariff Plan, Status, Age, Customer Value, Churn
```

O separador pode ser vírgula ou ponto e vírgula. O limite de envio é 8 MB e o arquivo pode ter até 100.000 registros. O sistema mostra uma amostra, diagnóstico, estatísticas, três gráficos e achados principais. O formulário valida os campos e mostra a classe estimada e a probabilidade indicada pelo modelo.

## Estrutura

- `app.py`: rotas Flask, formulário, gráficos e integração do classificador.
- `dados.py`: validação, limpeza e análise com Pandas.
- `modelo.py`: definição, divisão, treino e avaliação dos modelos.
- `treinar.py`: execução da comparação pelo terminal.
- `templates/`: páginas HTML.
- `static/`: estilos e JavaScript do upload.
- `data/`: base original e versão tratada.

## Limitações

A base representa clientes de uma empresa de telecomunicações do Irã e não necessariamente representa outros países, empresas ou períodos. As classes são desequilibradas; por isso, a acurácia deve ser lida junto com precisão, recall, F1 e matriz de confusão. O modelo não estima impacto financeiro de uma ação de retenção e suas probabilidades não são garantia de cancelamento. A previsão serve apenas como demonstração acadêmica.

## Integrantes e participação

- Gabriel Vitor Batista: Responsável pela parte de Machine Learning (modelo.py), treinando e comparando os modelos (Random Forest e Regressão Logística) com base no F1-Score.
- Anita de Oliveira Ries:Responsável pelo tratamento de dados (dados.py), realizando a limpeza, remoção de duplicatas, filtragem de valores inválidos e extração das estatísticas com o Pandas.
- Leandro Luiz de Mattos: Responsável pelo backend e rotas em Flask (app.py), integrando o modelo de Machine Learning à aplicação e implementando as validações do formulário de previsão.
- Sergio Rodrigo de Souza Filho: Responsável pelo front-end, pelas visualizações gráficas com Matplotlib (criar_graficos) e pelo script de teste no terminal (treinar.py), integrando os resultados às páginas web.

## Fontes e ferramentas

- Base: UCI Machine Learning Repository, Iranian Churn, DOI 10.24432/C5JW3Z.
- Bibliotecas: Flask, Pandas, Matplotlib e scikit-learn; documentação oficial de cada projeto.
- Assistente de IA: usado como apoio para organizar a estrutura, revisar trechos de código e preparar a documentação deste projeto. O grupo deve revisar o material, adaptar a explicação à própria compreensão e conseguir explicar o código na defesa, conforme a orientação da disciplina.
