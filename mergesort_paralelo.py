
import random
import time
from concurrent.futures import ProcessPoolExecutor

from tabelas import calcular_metricas, imprimir_tabela


# Junta dois vetores que já estão ordenados
def merge(esquerda, direita):
    resultado = []
    i = j = 0

    while i < len(esquerda) and j < len(direita):
        if esquerda[i] <= direita[j]:
            resultado.append(esquerda[i])
            i += 1
        else:
            resultado.append(direita[j])
            j += 1

    resultado.extend(esquerda[i:])
    resultado.extend(direita[j:])

    return resultado


# MergeSort Sequencial
def merge_sort_seq(vetor):
    if len(vetor) <= 1:
        return vetor

    meio = len(vetor) // 2

    esquerda = merge_sort_seq(vetor[:meio])
    direita = merge_sort_seq(vetor[meio:])

    return merge(esquerda, direita)


# MergeSort Paralelo
def parallel_merge_sort(vetor, num_workers=4, threshold=10_000):
    if num_workers < 1 or threshold < 1:
        raise ValueError("Workers e threshold devem ser positivos.")

    # Vetores pequenos são ordenados sequencialmente
    if len(vetor) <= threshold or num_workers == 1:
        return merge_sort_seq(vetor)

    # Divide o vetor em blocos conforme o threshold
    blocos = [
        vetor[i:i + threshold]
        for i in range(0, len(vetor), threshold)
    ]

    # Ordena os blocos em processos separados
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        blocos_ordenados = list(
            executor.map(merge_sort_seq, blocos)
        )

    # Intercala os blocos ordenados no processo principal
    while len(blocos_ordenados) > 1:
        novos_blocos = []

        for i in range(0, len(blocos_ordenados), 2):
            if i + 1 < len(blocos_ordenados):
                combinado = merge(
                    blocos_ordenados[i],
                    blocos_ordenados[i + 1]
                )
                novos_blocos.append(combinado)
            else:
                novos_blocos.append(blocos_ordenados[i])

        blocos_ordenados = novos_blocos

    return blocos_ordenados[0]


# Benchmark
def executar_benchmark():
    tamanhos = [10_000, 100_000, 500_000, 2_000_000]
    num_workers = 4
    threshold = 2_500

    resultados = []

    print("\n=== MERGESORT SEQUENCIAL VS PARALELO ===")
    print(f"Processos: {num_workers}")
    print(f"Threshold: {threshold:,}")

    for n in tamanhos:
        print(f"\nExecutando teste com N = {n:,}...")

        # Gera os mesmos dados para ambos os testes
        gerador = random.Random(42)
        dados = [
            gerador.randint(1, 10_000_000)
            for _ in range(n)
        ]

        dados_seq = dados.copy()
        dados_par = dados.copy()

        # Execução sequencial
        inicio = time.perf_counter()
        resultado_seq = merge_sort_seq(dados_seq)
        tempo_serial = time.perf_counter() - inicio

        # Execução paralela
        inicio = time.perf_counter()
        resultado_par = parallel_merge_sort(
            dados_par,
            num_workers=num_workers,
            threshold=threshold
        )
        tempo_paralelo = time.perf_counter() - inicio

        # Validação dos resultados
        assert resultado_seq == resultado_par == sorted(dados), (
            "Erro: resultados da ordenação são diferentes!"
        )

        # Speedup e Eficiência
        speedup, eficiencia = calcular_metricas(
            tempo_serial,
            tempo_paralelo,
            num_workers
        )

        # Redução percentual do tempo de execução
        reducao_tempo = (
            (tempo_serial - tempo_paralelo) / tempo_serial
        ) * 100

        # Verifica se houve ganho ou perda de desempenho
        if tempo_paralelo < tempo_serial:
            situacao = "Paralelo mais rapido"
        elif tempo_paralelo > tempo_serial:
            situacao = "Paralelo mais lento"
        else:
            situacao = "Tempos iguais"

        # Adiciona os resultados à tabela
        resultados.append([
            f"{n:,}",
            f"{tempo_serial:.4f}",
            f"{tempo_paralelo:.4f}",
            f"{speedup:.2f}x",
            f"{eficiencia:.2f}%",
            f"{reducao_tempo:+.2f}%",
            situacao
        ])

    # Exibe a tabela de resultados
    imprimir_tabela(
        "RESULTADOS - MERGESORT",
        [
            "N",
            "Serial (s)",
            "Paralelo (s)",
            "Speedup",
            "Eficiencia",
            "Reducao (%)",
            "Situacao"
        ],
        resultados
    )

    print("\nTodos os resultados foram validados!")


if __name__ == "__main__":
    executar_benchmark()
