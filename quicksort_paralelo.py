
import random
import time
from concurrent.futures import ProcessPoolExecutor

from tabelas import calcular_metricas, imprimir_tabela


# Divide o vetor em relacao ao pivo
def particionar(vetor):
    if not vetor:
        return [], [], []

    pivo = vetor[len(vetor) // 2]

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


# QuickSort Sequencial
def quicksort_seq(vetor):
    if len(vetor) <= 1:
        return vetor

    menores, iguais, maiores = particionar(vetor)

    return (
        quicksort_seq(menores)
        + iguais
        + quicksort_seq(maiores)
    )


# QuickSort Paralelo com 4 tarefas
def parallel_quicksort(vetor, num_workers=4, threshold=10_000):
    if num_workers < 1 or threshold < 1:
        raise ValueError("Workers e threshold devem ser positivos.")

    # Evita paralelizar vetores muito pequenos
    if len(vetor) <= threshold or num_workers == 1:
        return quicksort_seq(vetor)

    # Primeiro nivel de particionamento
    esquerda, meio, direita = particionar(vetor)

    # Segundo nivel de particionamento
    e1, meio_e, e2 = particionar(esquerda)
    d1, meio_d, d2 = particionar(direita)

    # Quatro particoes independentes
    blocos = [e1, e2, d1, d2]

    # Ordena as particoes em paralelo
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        blocos_ordenados = list(
            executor.map(quicksort_seq, blocos)
        )

    # Reune as particoes na ordem correta
    return (
        blocos_ordenados[0]
        + meio_e
        + blocos_ordenados[1]
        + meio
        + blocos_ordenados[2]
        + meio_d
        + blocos_ordenados[3]
    )


# Benchmark
def executar_benchmark():
    tamanhos = [100_000, 500_000]
    num_workers = 4
    threshold = 10_000

    resultados = []

    print("\n=== QUICKSORT SEQUENCIAL VS PARALELO ===")
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

        # Execucao sequencial
        inicio = time.perf_counter()

        resultado_seq = quicksort_seq(dados.copy())

        tempo_serial = time.perf_counter() - inicio

        # Execucao paralela
        inicio = time.perf_counter()

        resultado_par = parallel_quicksort(
            dados.copy(),
            num_workers=num_workers,
            threshold=threshold
        )

        tempo_paralelo = time.perf_counter() - inicio

        # Validacao
        assert resultado_seq == resultado_par == sorted(dados), (
            "Erro: resultados da ordenacao sao diferentes!"
        )

        # Speedup e Eficiencia
        speedup, eficiencia = calcular_metricas(
            tempo_serial,
            tempo_paralelo,
            num_workers
        )

        # Reducao percentual no tempo
        reducao_tempo = (
            (tempo_serial - tempo_paralelo) / tempo_serial
        ) * 100

        # Identifica a situacao
        if tempo_paralelo < tempo_serial:
            situacao = "Paralelo mais rapido"
        elif tempo_paralelo > tempo_serial:
            situacao = "Paralelo mais lento"
        else:
            situacao = "Tempos iguais"

        resultados.append([
            f"{n:,}",
            f"{tempo_serial:.4f}",
            f"{tempo_paralelo:.4f}",
            f"{speedup:.2f}x",
            f"{eficiencia:.2f}%",
            f"{reducao_tempo:+.2f}%",
            situacao
        ])

    # Exibe os resultados
    imprimir_tabela(
        "RESULTADOS - QUICKSORT",
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
