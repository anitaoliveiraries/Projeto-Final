"""Treina e imprime a comparação dos modelos com a base tratada."""
from dados import tratar_dados
from modelo import carregar_base_padrao, treinar_e_avaliar

if __name__ == "__main__":
    dados, _ = tratar_dados(carregar_base_padrao())
    avaliacao = treinar_e_avaliar(dados)
    print("Divisão: 80% treino / 20% teste | random_state=42 | estratificada")
    print(f"Treino: {avaliacao['tamanho_treino']} | Teste: {avaliacao['tamanho_teste']}")
    print("\nModelo                 Acurácia  Precisão  Recall    F1")
    for nome, resultado in avaliacao["resultados"].items():
        print(f"{nome:22} {resultado['acuracia']:.3f}     {resultado['precisao']:.3f}     {resultado['recall']:.3f}   {resultado['f1']:.3f}")
        print("Matriz de confusão (linhas reais [0,1], colunas previstas [0,1]):")
        print(resultado["matriz"])
    print(f"\nModelo escolhido pelo maior F1: {avaliacao['escolhido']}")
