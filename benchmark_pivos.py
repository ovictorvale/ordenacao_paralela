
import time
from concurrent.futures import ProcessPoolExecutor
from itertools import repeat

from tabelas import calcular_metricas, imprimir_tabela


# Divide o vetor de acordo com o pivo escolhido
def particionar(vetor, estrategia):
    if not vetor:
        return [], [], []

    if estrategia == "primeiro":
        pivo = vetor[0]

    elif estrategia == "mediana":
        candidatos = [
            vetor[0],
            vetor[len(vetor) // 2],
            vetor[-1]
        ]
        pivo = sorted(candidatos)[1]

    else:
        raise ValueError("Estrategia de pivo invalida!")

    menores = []
    iguais = []
    maiores = []

    for elemento in vetor:
        if elemento < pivo:
            menores.append(elemento)
        elif elemento > pivo:
            maiores.append(elemento)
        else:
            iguais.append(elemento)

    return menores, iguais, maiores


# QuickSort Sequencial com escolha do pivo
def quicksort_seq_pivo(vetor, estrategia):
    resultado = []

    # Pilha para evitar excesso de chamadas recursivas
    tarefas = [("ordenar", vetor)]

    while tarefas:
        acao, trecho = tarefas.pop()

        if acao == "adicionar":
            resultado.extend(trecho)

        elif len(trecho) <= 1:
            resultado.extend(trecho)

        else:
            menores, iguais, maiores = particionar(
                trecho, estrategia
            )

            tarefas.append(("ordenar", maiores))
            tarefas.append(("adicionar", iguais))
            tarefas.append(("ordenar", menores))

    return resultado


# QuickSort Paralelo
def quicksort_paralelo_pivo(vetor, estrategia, num_workers=4):
    # Primeiro particionamento
    menores, iguais, maiores = particionar(
        vetor, estrategia
    )

    # Segundo particionamento
    e1, iguais_e, e2 = particionar(
        menores, estrategia
    )

    d1, iguais_d, d2 = particionar(
        maiores, estrategia
    )

    # Quatro tarefas independentes
    blocos = [e1, e2, d1, d2]

    tamanhos = [len(bloco) for bloco in blocos]

    # Ordena em paralelo usando a mesma estrategia
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        blocos_ordenados = list(
            executor.map(
                quicksort_seq_pivo,
                blocos,
                repeat(estrategia)
            )
        )

    # Reune os resultados ordenados
    resultado = (
        blocos_ordenados[0]
        + iguais_e
        + blocos_ordenados[1]
        + iguais
        + blocos_ordenados[2]
        + iguais_d
        + blocos_ordenados[3]
    )

    return resultado, tamanhos


# Benchmark das estrategias
def executar_benchmark():
    n = 4_000
    num_workers = 4
    estrategias = ["primeiro", "mediana"]

    # Cria um vetor parcialmente ordenado
    dados = list(range(n))

    # Troca alguns elementos vizinhos
    for i in range(1, n - 2, 20):
        dados[i], dados[i + 1] = dados[i + 1], dados[i]

    resultados = []
    distribuicao = []

    print("\n=== BENCHMARK DE PIVOS - QUICKSORT ===")
    print(f"Elementos: {n:,}")
    print(f"Processos: {num_workers}")
    print("Entrada: vetor parcialmente ordenado")

    for estrategia in estrategias:
        print(f"\nTestando estrategia: {estrategia}...")

        dados_seq = dados.copy()
        dados_par = dados.copy()

        # Execucao sequencial
        inicio = time.perf_counter()

        resultado_seq = quicksort_seq_pivo(
            dados_seq, estrategia
        )

        tempo_serial = time.perf_counter() - inicio

        # Execucao paralela
        inicio = time.perf_counter()

        resultado_par, tamanhos = quicksort_paralelo_pivo(
            dados_par,
            estrategia,
            num_workers
        )

        tempo_paralelo = time.perf_counter() - inicio

        # Validacao
        assert resultado_seq == resultado_par == sorted(dados), (
            "Erro na ordenacao!"
        )

        # Metricas de desempenho
        speedup, eficiencia = calcular_metricas(
            tempo_serial,
            tempo_paralelo,
            num_workers
        )

        reducao = (
            (tempo_serial - tempo_paralelo) / tempo_serial
        ) * 100

        resultados.append([
            estrategia,
            f"{tempo_serial:.4f}",
            f"{tempo_paralelo:.4f}",
            f"{speedup:.2f}x",
            f"{eficiencia:.2f}%",
            f"{reducao:+.2f}%"
        ])

        # Registra a distribuicao entre as tarefas
        distribuicao.append([
            estrategia,
            *[f"{t:,}" for t in tamanhos]
        ])

    # Tabela de desempenho
    imprimir_tabela(
        "COMPARACAO DE DESEMPENHO",
        [
            "Pivo",
            "Serial (s)",
            "Paralelo (s)",
            "Speedup",
            "Eficiencia",
            "Reducao (%)"
        ],
        resultados
    )

    # Tabela de distribuicao de trabalho
    imprimir_tabela(
        "DISTRIBUICAO DAS TAREFAS",
        [
            "Pivo",
            "Bloco 1",
            "Bloco 2",
            "Bloco 3",
            "Bloco 4"
        ],
        distribuicao
    )

    print("\nTodos os resultados foram validados!")


if __name__ == "__main__":
    executar_benchmark()
